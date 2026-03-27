import pytest
from typer.testing import CliRunner

from precifique.cli.main import app
from precifique.core.models import Product
from precifique.core.storage import save_products

runner = CliRunner()


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    d = tmp_path / "data"
    monkeypatch.setenv("PRECIFIQUE_DATA_DIR", str(d))
    return d


@pytest.fixture
def product(data_dir):
    p = Product(sku="MUG-001", name="Ceramic Mug", profit_margin=30.0)
    save_products([p], data_dir)
    return p


class TestMaterialAdd:
    def test_add_exits_zero(self, product, data_dir):
        result = runner.invoke(app, [
            "material", "add", "MUG-001",
            "--name", "Clay",
            "--unit-cost", "5.0",
            "--quantity", "2.0",
        ])
        assert result.exit_code == 0

    def test_add_persists_material(self, product, data_dir):
        runner.invoke(app, [
            "material", "add", "MUG-001",
            "--name", "Clay",
            "--unit-cost", "5.0",
            "--quantity", "2.0",
        ])
        from precifique.core.storage import load_materials
        materials = load_materials(data_dir)
        assert any(m.name == "Clay" and m.product_sku == "MUG-001" for m in materials)

    def test_add_unknown_sku_exits_nonzero(self, data_dir):
        result = runner.invoke(app, [
            "material", "add", "UNKNOWN",
            "--name", "Clay",
            "--unit-cost", "5.0",
            "--quantity", "2.0",
        ])
        assert result.exit_code != 0


class TestLaborAdd:
    def test_add_exits_zero(self, product, data_dir):
        result = runner.invoke(app, [
            "labor", "add", "MUG-001",
            "--hours", "2.0",
            "--hourly-rate", "10.0",
        ])
        assert result.exit_code == 0

    def test_add_persists_labor(self, product, data_dir):
        runner.invoke(app, [
            "labor", "add", "MUG-001",
            "--hours", "2.0",
            "--hourly-rate", "10.0",
        ])
        from precifique.core.storage import load_labor
        labor = load_labor(data_dir)
        assert any(l.hours == 2.0 and l.product_sku == "MUG-001" for l in labor)

    def test_add_unknown_sku_exits_nonzero(self, data_dir):
        result = runner.invoke(app, [
            "labor", "add", "UNKNOWN",
            "--hours", "2.0",
            "--hourly-rate", "10.0",
        ])
        assert result.exit_code != 0


class TestOverheadAdd:
    def test_add_exits_zero(self, product, data_dir):
        result = runner.invoke(app, [
            "overhead", "add", "MUG-001",
            "--rent", "3.0",
            "--tools", "2.0",
            "--packaging", "1.5",
            "--shipping", "1.0",
            "--taxes", "0.5",
        ])
        assert result.exit_code == 0

    def test_add_persists_overhead(self, product, data_dir):
        runner.invoke(app, [
            "overhead", "add", "MUG-001",
            "--rent", "3.0",
            "--tools", "2.0",
            "--packaging", "1.5",
            "--shipping", "1.0",
            "--taxes", "0.5",
        ])
        from precifique.core.storage import load_overhead
        overhead = load_overhead(data_dir)
        assert any(o.rent == 3.0 and o.product_sku == "MUG-001" for o in overhead)

    def test_add_unknown_sku_exits_nonzero(self, data_dir):
        result = runner.invoke(app, [
            "overhead", "add", "UNKNOWN",
            "--rent", "3.0",
            "--tools", "2.0",
            "--packaging", "1.5",
            "--shipping", "1.0",
            "--taxes", "0.5",
        ])
        assert result.exit_code != 0
