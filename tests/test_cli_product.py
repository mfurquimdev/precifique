import pytest
from typer.testing import CliRunner

from precifique.cli.main import app

runner = CliRunner()


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    d = tmp_path / "data"
    monkeypatch.setenv("PRECIFIQUE_DATA_DIR", str(d))
    return d


class TestProductAdd:
    def test_add_exits_zero(self, data_dir):
        result = runner.invoke(app, [
            "product", "add",
            "--sku", "MUG-001",
            "--name", "Ceramic Mug",
            "--profit-margin", "30.0",
        ])
        assert result.exit_code == 0

    def test_add_prints_sku(self, data_dir):
        result = runner.invoke(app, [
            "product", "add",
            "--sku", "MUG-001",
            "--name", "Ceramic Mug",
            "--profit-margin", "30.0",
        ])
        assert "MUG-001" in result.output

    def test_add_persists_product(self, data_dir):
        runner.invoke(app, [
            "product", "add",
            "--sku", "MUG-001",
            "--name", "Ceramic Mug",
            "--profit-margin", "30.0",
        ])
        result = runner.invoke(app, ["product", "list"])
        assert "MUG-001" in result.output


class TestProductList:
    def test_list_empty_catalog(self, data_dir):
        result = runner.invoke(app, ["product", "list"])
        assert result.exit_code == 0
        assert "empty" in result.output.lower() or "no products" in result.output.lower()

    def test_list_shows_all_products(self, data_dir):
        runner.invoke(app, ["product", "add", "--sku", "MUG-001", "--name", "Ceramic Mug", "--profit-margin", "30.0"])
        runner.invoke(app, ["product", "add", "--sku", "BOWL-001", "--name", "Clay Bowl", "--profit-margin", "25.0"])
        result = runner.invoke(app, ["product", "list"])
        assert "MUG-001" in result.output
        assert "BOWL-001" in result.output


class TestProductShow:
    def test_show_existing_product(self, data_dir):
        runner.invoke(app, ["product", "add", "--sku", "MUG-001", "--name", "Ceramic Mug", "--profit-margin", "30.0"])
        result = runner.invoke(app, ["product", "show", "MUG-001"])
        assert result.exit_code == 0
        assert "Ceramic Mug" in result.output
        assert "30" in result.output

    def test_show_unknown_sku_exits_nonzero(self, data_dir):
        result = runner.invoke(app, ["product", "show", "UNKNOWN"])
        assert result.exit_code != 0


class TestProductDelete:
    def test_delete_removes_product(self, data_dir):
        runner.invoke(app, ["product", "add", "--sku", "MUG-001", "--name", "Ceramic Mug", "--profit-margin", "30.0"])
        runner.invoke(app, ["product", "delete", "MUG-001"])
        result = runner.invoke(app, ["product", "list"])
        assert "MUG-001" not in result.output

    def test_delete_exits_zero(self, data_dir):
        runner.invoke(app, ["product", "add", "--sku", "MUG-001", "--name", "Ceramic Mug", "--profit-margin", "30.0"])
        result = runner.invoke(app, ["product", "delete", "MUG-001"])
        assert result.exit_code == 0

    def test_delete_unknown_sku_exits_nonzero(self, data_dir):
        result = runner.invoke(app, ["product", "delete", "UNKNOWN"])
        assert result.exit_code != 0
