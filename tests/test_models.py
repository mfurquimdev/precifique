import pytest
from uuid import UUID
from pydantic import ValidationError

from precifique.core.models import Labor, Material, Overhead, Product


class TestProduct:
    def test_valid_product_constructs(self):
        p = Product(sku="MUG-001", name="Ceramic Mug", profit_margin=30.0)
        assert p.sku == "MUG-001"
        assert p.name == "Ceramic Mug"
        assert p.profit_margin == 30.0

    def test_id_is_auto_generated(self):
        p = Product(sku="MUG-001", name="Ceramic Mug", profit_margin=30.0)
        assert isinstance(p.id, UUID)

    def test_rejects_negative_margin(self):
        with pytest.raises(ValidationError):
            Product(sku="MUG-001", name="Ceramic Mug", profit_margin=-1.0)

    def test_rejects_margin_of_100(self):
        with pytest.raises(ValidationError):
            Product(sku="MUG-001", name="Ceramic Mug", profit_margin=100.0)

    def test_rejects_margin_above_100(self):
        with pytest.raises(ValidationError):
            Product(sku="MUG-001", name="Ceramic Mug", profit_margin=101.0)

    def test_accepts_zero_margin(self):
        p = Product(sku="MUG-001", name="Ceramic Mug", profit_margin=0.0)
        assert p.profit_margin == 0.0


class TestMaterial:
    def test_valid_material_constructs(self):
        m = Material(product_sku="MUG-001", name="Clay", unit_cost=5.0, quantity=2.0)
        assert m.product_sku == "MUG-001"
        assert m.unit_cost == 5.0
        assert m.quantity == 2.0

    def test_rejects_negative_unit_cost(self):
        with pytest.raises(ValidationError):
            Material(product_sku="MUG-001", name="Clay", unit_cost=-1.0, quantity=2.0)

    def test_accepts_zero_unit_cost(self):
        m = Material(product_sku="MUG-001", name="Clay", unit_cost=0.0, quantity=1.0)
        assert m.unit_cost == 0.0

    def test_rejects_zero_quantity(self):
        with pytest.raises(ValidationError):
            Material(product_sku="MUG-001", name="Clay", unit_cost=5.0, quantity=0.0)

    def test_rejects_negative_quantity(self):
        with pytest.raises(ValidationError):
            Material(product_sku="MUG-001", name="Clay", unit_cost=5.0, quantity=-1.0)


class TestLabor:
    def test_valid_labor_constructs(self):
        l = Labor(product_sku="MUG-001", hours=2.0, hourly_rate=25.0)
        assert l.hours == 2.0
        assert l.hourly_rate == 25.0

    def test_rejects_negative_hours(self):
        with pytest.raises(ValidationError):
            Labor(product_sku="MUG-001", hours=-1.0, hourly_rate=25.0)

    def test_rejects_negative_hourly_rate(self):
        with pytest.raises(ValidationError):
            Labor(product_sku="MUG-001", hours=2.0, hourly_rate=-1.0)

    def test_accepts_zero_hours(self):
        l = Labor(product_sku="MUG-001", hours=0.0, hourly_rate=25.0)
        assert l.hours == 0.0


class TestOverhead:
    def test_valid_overhead_constructs(self):
        o = Overhead(
            product_sku="MUG-001",
            rent=3.0, tools=2.0, packaging=1.5, shipping=1.0, taxes=0.5
        )
        assert o.rent == 3.0

    def test_rejects_negative_rent(self):
        with pytest.raises(ValidationError):
            Overhead(product_sku="MUG-001", rent=-1.0, tools=0, packaging=0, shipping=0, taxes=0)

    def test_rejects_negative_tools(self):
        with pytest.raises(ValidationError):
            Overhead(product_sku="MUG-001", rent=0, tools=-1.0, packaging=0, shipping=0, taxes=0)

    def test_rejects_negative_packaging(self):
        with pytest.raises(ValidationError):
            Overhead(product_sku="MUG-001", rent=0, tools=0, packaging=-1.0, shipping=0, taxes=0)

    def test_rejects_negative_shipping(self):
        with pytest.raises(ValidationError):
            Overhead(product_sku="MUG-001", rent=0, tools=0, packaging=0, shipping=-1.0, taxes=0)

    def test_rejects_negative_taxes(self):
        with pytest.raises(ValidationError):
            Overhead(product_sku="MUG-001", rent=0, tools=0, packaging=0, shipping=0, taxes=-1.0)

    def test_accepts_all_zero_overhead(self):
        o = Overhead(product_sku="MUG-001", rent=0, tools=0, packaging=0, shipping=0, taxes=0)
        assert o.rent == 0
