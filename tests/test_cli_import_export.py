import csv

import pytest
from typer.testing import CliRunner

from precifique.cli.main import app

runner = CliRunner()


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    d = tmp_path / "data"
    monkeypatch.setenv("PRECIFIQUE_DATA_DIR", str(d))
    return d


@pytest.fixture
def product(data_dir):
    runner.invoke(app, [
        "product", "add",
        "--sku", "MUG-001",
        "--name", "Ceramic Mug",
        "--profit-margin", "30.0",
    ])
    return data_dir


@pytest.fixture
def full_product(data_dir):
    """Product with material, labor, and overhead."""
    runner.invoke(app, ["product", "add", "--sku", "MUG-001", "--name", "Ceramic Mug", "--profit-margin", "30.0"])
    runner.invoke(app, ["material", "add", "MUG-001", "--name", "Clay", "--unit-cost", "5.0", "--quantity", "2.0"])
    runner.invoke(app, ["labor", "add", "MUG-001", "--hours", "2.0", "--hourly-rate", "10.0"])
    runner.invoke(app, ["overhead", "add", "MUG-001", "--rent", "3.0", "--tools", "2.0", "--packaging", "1.0", "--shipping", "1.0", "--taxes", "0.5"])
    return data_dir


class TestExportProducts:
    def test_export_creates_csv_file(self, product, tmp_path):
        out = tmp_path / "products.csv"
        result = runner.invoke(app, ["export", "products", str(out)])
        assert result.exit_code == 0
        assert out.exists()

    def test_export_csv_has_correct_columns(self, product, tmp_path):
        out = tmp_path / "products.csv"
        runner.invoke(app, ["export", "products", str(out)])
        with open(out) as f:
            reader = csv.DictReader(f)
            assert set(reader.fieldnames) == {"id", "sku", "name", "profit_margin"}

    def test_export_csv_contains_product_data(self, product, tmp_path):
        out = tmp_path / "products.csv"
        runner.invoke(app, ["export", "products", str(out)])
        with open(out) as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 1
        assert rows[0]["sku"] == "MUG-001"
        assert rows[0]["name"] == "Ceramic Mug"
        assert rows[0]["profit_margin"] == "30.0"


class TestExportAllEntities:
    @pytest.mark.parametrize("entity,expected_columns", [
        ("materials", {"id", "product_sku", "name", "unit_cost", "quantity"}),
        ("labor", {"id", "product_sku", "hours", "hourly_rate"}),
        ("overhead", {"id", "product_sku", "rent", "tools", "packaging", "shipping", "taxes"}),
    ])
    def test_export_entity_has_correct_columns(self, full_product, tmp_path, entity, expected_columns):
        out = tmp_path / f"{entity}.csv"
        result = runner.invoke(app, ["export", entity, str(out)])
        assert result.exit_code == 0
        with open(out) as f:
            reader = csv.DictReader(f)
            assert set(reader.fieldnames) == expected_columns


class TestImportProducts:
    def test_import_inserts_new_records(self, data_dir, tmp_path):
        # Create a CSV with a new product
        out = tmp_path / "products.csv"
        with open(out, "w") as f:
            f.write("id,sku,name,profit_margin\n")
            f.write("00000000-0000-0000-0000-000000000001,BOWL-001,Clay Bowl,25.0\n")

        result = runner.invoke(app, ["import", "products", str(out)])
        assert result.exit_code == 0

        listed = runner.invoke(app, ["product", "list"])
        assert "BOWL-001" in listed.output

    def test_import_updates_existing_record_by_id(self, data_dir, tmp_path):
        # Add a product via CLI, then export, modify, and reimport
        runner.invoke(app, ["product", "add", "--sku", "MUG-001", "--name", "Ceramic Mug", "--profit-margin", "30.0"])

        out = tmp_path / "products.csv"
        runner.invoke(app, ["export", "products", str(out)])

        # Read exported CSV, modify the name
        with open(out) as f:
            rows = list(csv.DictReader(f))
        rows[0]["name"] = "Updated Mug"
        with open(out, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        result = runner.invoke(app, ["import", "products", str(out)])
        assert result.exit_code == 0

        shown = runner.invoke(app, ["product", "show", "MUG-001"])
        assert "Updated Mug" in shown.output


class TestImportExportRoundTrip:
    def test_round_trip_preserves_all_records(self, full_product, tmp_path):
        for entity in ("products", "materials", "labor", "overhead"):
            out = tmp_path / f"{entity}.csv"
            runner.invoke(app, ["export", entity, str(out)])

        # Wipe data dir and reimport
        import shutil
        shutil.rmtree(str(full_product), ignore_errors=True)

        for entity in ("products", "materials", "labor", "overhead"):
            out = tmp_path / f"{entity}.csv"
            result = runner.invoke(app, ["import", entity, str(out)])
            assert result.exit_code == 0

        listed = runner.invoke(app, ["product", "list"])
        assert "MUG-001" in listed.output


class TestImportErrors:
    def test_unknown_entity_exits_nonzero(self, data_dir, tmp_path):
        out = tmp_path / "foo.csv"
        out.write_text("id,foo\n1,bar\n")
        result = runner.invoke(app, ["import", "widgets", str(out)])
        assert result.exit_code != 0

    def test_unknown_entity_prints_error(self, data_dir, tmp_path):
        out = tmp_path / "foo.csv"
        out.write_text("id,foo\n1,bar\n")
        result = runner.invoke(app, ["import", "widgets", str(out)])
        assert "widgets" in result.output

    def test_missing_columns_exits_nonzero(self, data_dir, tmp_path):
        out = tmp_path / "products.csv"
        out.write_text("id,sku\nsome-id,MUG-001\n")  # missing name, profit_margin
        result = runner.invoke(app, ["import", "products", str(out)])
        assert result.exit_code != 0

    def test_missing_columns_prints_error(self, data_dir, tmp_path):
        out = tmp_path / "products.csv"
        out.write_text("id,sku\nsome-id,MUG-001\n")
        result = runner.invoke(app, ["import", "products", str(out)])
        assert "missing" in result.output.lower()

    def test_export_unknown_entity_exits_nonzero(self, data_dir, tmp_path):
        out = tmp_path / "foo.csv"
        result = runner.invoke(app, ["export", "widgets", str(out)])
        assert result.exit_code != 0
