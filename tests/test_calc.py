import pytest

from precifique.core.calc import calculate_price
from precifique.core.models import Labor, Material, Overhead, Product


@pytest.fixture
def product():
    return Product(sku="MUG-001", name="Ceramic Mug", profit_margin=30.0)


@pytest.fixture
def materials():
    return [Material(product_sku="MUG-001", name="Clay", unit_cost=5.0, quantity=2.0)]


@pytest.fixture
def labor():
    return [Labor(product_sku="MUG-001", hours=2.0, hourly_rate=10.0)]


@pytest.fixture
def overhead():
    return [
        Overhead(
            product_sku="MUG-001",
            rent=3.0, tools=2.0, packaging=1.5, shipping=1.0, taxes=0.5,
        )
    ]


class TestSellingPrice:
    def test_correct_selling_price(self, product, materials, labor, overhead):
        # total_cost = (5*2) + (2*10) + (3+2+1.5+1+0.5) = 10 + 20 + 8 = 38
        # selling_price = 38 / (1 - 0.30) = 38 / 0.70 ≈ 54.285714
        result = calculate_price(product, materials, labor, overhead)
        assert result.selling_price == pytest.approx(54.285714, rel=1e-5)

    def test_zero_margin_selling_price_equals_total_cost(self, materials, labor, overhead):
        p = Product(sku="MUG-001", name="Ceramic Mug", profit_margin=0.0)
        result = calculate_price(p, materials, labor, overhead)
        assert result.selling_price == pytest.approx(result.total_cost)


class TestSubtotals:
    def test_materials_subtotal(self, product, materials, labor, overhead):
        result = calculate_price(product, materials, labor, overhead)
        assert result.materials_subtotal == pytest.approx(10.0)  # 5.0 * 2.0

    def test_materials_subtotal_sums_multiple(self, product, labor, overhead):
        mats = [
            Material(product_sku="MUG-001", name="Clay", unit_cost=5.0, quantity=2.0),
            Material(product_sku="MUG-001", name="Glaze", unit_cost=3.0, quantity=1.0),
        ]
        result = calculate_price(product, mats, labor, overhead)
        assert result.materials_subtotal == pytest.approx(13.0)  # 10 + 3

    def test_empty_materials_gives_zero_subtotal(self, product, labor, overhead):
        result = calculate_price(product, [], labor, overhead)
        assert result.materials_subtotal == pytest.approx(0.0)

    def test_labor_subtotal(self, product, materials, labor, overhead):
        result = calculate_price(product, materials, labor, overhead)
        assert result.labor_subtotal == pytest.approx(20.0)  # 2.0 * 10.0

    def test_labor_subtotal_sums_multiple(self, product, materials, overhead):
        lab = [
            Labor(product_sku="MUG-001", hours=2.0, hourly_rate=10.0),
            Labor(product_sku="MUG-001", hours=1.0, hourly_rate=15.0),
        ]
        result = calculate_price(product, materials, lab, overhead)
        assert result.labor_subtotal == pytest.approx(35.0)  # 20 + 15

    def test_overhead_subtotal(self, product, materials, labor, overhead):
        result = calculate_price(product, materials, labor, overhead)
        assert result.overhead_subtotal == pytest.approx(8.0)  # 3+2+1.5+1+0.5

    def test_overhead_fields_summed_across_records(self, product, materials, labor):
        ovh = [
            Overhead(product_sku="MUG-001", rent=3.0, tools=2.0, packaging=0, shipping=0, taxes=0),
            Overhead(product_sku="MUG-001", rent=1.0, tools=0.0, packaging=1.5, shipping=1.0, taxes=0.5),
        ]
        result = calculate_price(product, materials, labor, ovh)
        assert result.rent == pytest.approx(4.0)
        assert result.tools == pytest.approx(2.0)
        assert result.packaging == pytest.approx(1.5)
        assert result.overhead_subtotal == pytest.approx(9.0)

    def test_total_cost(self, product, materials, labor, overhead):
        result = calculate_price(product, materials, labor, overhead)
        assert result.total_cost == pytest.approx(38.0)  # 10 + 20 + 8


class TestBreakdownFields:
    def test_product_name_in_breakdown(self, product, materials, labor, overhead):
        result = calculate_price(product, materials, labor, overhead)
        assert result.product_name == "Ceramic Mug"

    def test_profit_margin_in_breakdown(self, product, materials, labor, overhead):
        result = calculate_price(product, materials, labor, overhead)
        assert result.profit_margin == 30.0
