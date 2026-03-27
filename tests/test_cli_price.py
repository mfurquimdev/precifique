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
def product_with_costs(data_dir):
    """Add product + material + labor + overhead via CLI."""
    runner.invoke(app, [
        "product", "add",
        "--sku", "MUG-001",
        "--name", "Ceramic Mug",
        "--profit-margin", "30.0",
    ])
    runner.invoke(app, [
        "material", "add", "MUG-001",
        "--name", "Clay",
        "--unit-cost", "12.50",
        "--quantity", "1.0",
    ])
    runner.invoke(app, [
        "labor", "add", "MUG-001",
        "--hours", "2.0",
        "--hourly-rate", "10.0",
    ])
    runner.invoke(app, [
        "overhead", "add", "MUG-001",
        "--rent", "3.0",
        "--tools", "2.0",
        "--packaging", "1.50",
        "--shipping", "1.0",
        "--taxes", "0.50",
    ])
    return data_dir


class TestPriceCommand:
    def test_price_exits_zero(self, product_with_costs):
        result = runner.invoke(app, ["price", "MUG-001"])
        assert result.exit_code == 0

    def test_price_shows_selling_price(self, product_with_costs):
        result = runner.invoke(app, ["price", "MUG-001"])
        assert "57.86" in result.output

    def test_price_shows_product_name(self, product_with_costs):
        result = runner.invoke(app, ["price", "MUG-001"])
        assert "Ceramic Mug" in result.output

    def test_price_shows_subtotals(self, product_with_costs):
        result = runner.invoke(app, ["price", "MUG-001"])
        assert "12.50" in result.output  # materials
        assert "20.00" in result.output  # labor
        assert "8.00" in result.output   # overhead

    def test_price_shows_overhead_breakdown(self, product_with_costs):
        result = runner.invoke(app, ["price", "MUG-001"])
        assert "3.00" in result.output   # rent
        assert "2.00" in result.output   # tools
        assert "1.50" in result.output   # packaging
        assert "1.00" in result.output   # shipping
        assert "0.50" in result.output   # taxes

    def test_price_currency_from_env(self, product_with_costs, monkeypatch):
        monkeypatch.setenv("PRECIFIQUE_CURRENCY", "USD")
        result = runner.invoke(app, ["price", "MUG-001"])
        assert "$" in result.output

    def test_price_unknown_sku_exits_nonzero(self, data_dir):
        result = runner.invoke(app, ["price", "UNKNOWN"])
        assert result.exit_code != 0

    def test_price_unknown_sku_prints_error(self, data_dir):
        result = runner.invoke(app, ["price", "UNKNOWN"])
        assert "UNKNOWN" in result.output

    def test_price_full_lifecycle(self, product_with_costs):
        """Integration: full lifecycle with correct selling price math."""
        # total_cost = 12.50 + 20.00 + 8.00 = 40.50
        # selling_price = 40.50 / (1 - 0.30) = 57.857... → 57.86
        result = runner.invoke(app, ["price", "MUG-001"])
        assert result.exit_code == 0
        assert "40.50" in result.output
        assert "57.86" in result.output
