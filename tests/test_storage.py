from pathlib import Path
from uuid import uuid4

import pytest

from precifique.core.models import Labor, Material, Overhead, Product
from precifique.core.storage import (
    load_labor,
    load_materials,
    load_overhead,
    load_products,
    merge_labor,
    merge_materials,
    merge_overhead,
    merge_products,
    save_labor,
    save_materials,
    save_overhead,
    save_products,
)


@pytest.fixture
def data_dir(tmp_path):
    return tmp_path / "data"


@pytest.fixture
def product():
    return Product(sku="MUG-001", name="Ceramic Mug", profit_margin=30.0)


@pytest.fixture
def material(product):
    return Material(product_sku=product.sku, name="Clay", unit_cost=5.0, quantity=2.0)


@pytest.fixture
def labor(product):
    return Labor(product_sku=product.sku, hours=2.0, hourly_rate=25.0)


@pytest.fixture
def overhead(product):
    return Overhead(
        product_sku=product.sku,
        rent=3.0, tools=2.0, packaging=1.5, shipping=1.0, taxes=0.5,
    )


class TestLoadProducts:
    def test_returns_empty_list_when_csv_missing(self, data_dir):
        assert load_products(data_dir) == []

    def test_round_trip(self, data_dir, product):
        save_products([product], data_dir)
        loaded = load_products(data_dir)
        assert loaded == [product]

    def test_creates_data_dir_if_missing(self, data_dir, product):
        assert not data_dir.exists()
        save_products([product], data_dir)
        assert data_dir.exists()

    def test_round_trip_multiple(self, data_dir):
        products = [
            Product(sku="MUG-001", name="Ceramic Mug", profit_margin=30.0),
            Product(sku="BOWL-001", name="Clay Bowl", profit_margin=25.0),
        ]
        save_products(products, data_dir)
        assert load_products(data_dir) == products


class TestMergeProducts:
    def test_merge_inserts_new_record(self, data_dir, product):
        save_products([], data_dir)
        merge_products([product], data_dir)
        assert load_products(data_dir) == [product]

    def test_merge_updates_existing_record(self, data_dir, product):
        save_products([product], data_dir)
        updated = product.model_copy(update={"name": "Updated Mug"})
        merge_products([updated], data_dir)
        loaded = load_products(data_dir)
        assert len(loaded) == 1
        assert loaded[0].name == "Updated Mug"

    def test_merge_does_not_delete_other_records(self, data_dir):
        existing = Product(sku="MUG-001", name="Ceramic Mug", profit_margin=30.0)
        incoming = Product(sku="BOWL-001", name="Clay Bowl", profit_margin=25.0)
        save_products([existing], data_dir)
        merge_products([incoming], data_dir)
        loaded = load_products(data_dir)
        assert len(loaded) == 2


class TestMaterialsRoundTrip:
    def test_round_trip(self, data_dir, material):
        save_materials([material], data_dir)
        assert load_materials(data_dir) == [material]

    def test_returns_empty_list_when_csv_missing(self, data_dir):
        assert load_materials(data_dir) == []

    def test_merge_inserts_new_record(self, data_dir, material):
        merge_materials([material], data_dir)
        assert load_materials(data_dir) == [material]

    def test_merge_updates_existing_record(self, data_dir, material):
        save_materials([material], data_dir)
        updated = material.model_copy(update={"unit_cost": 9.99})
        merge_materials([updated], data_dir)
        loaded = load_materials(data_dir)
        assert len(loaded) == 1
        assert loaded[0].unit_cost == 9.99


class TestLaborRoundTrip:
    def test_round_trip(self, data_dir, labor):
        save_labor([labor], data_dir)
        assert load_labor(data_dir) == [labor]

    def test_returns_empty_list_when_csv_missing(self, data_dir):
        assert load_labor(data_dir) == []

    def test_merge_inserts_new_record(self, data_dir, labor):
        merge_labor([labor], data_dir)
        assert load_labor(data_dir) == [labor]

    def test_merge_updates_existing_record(self, data_dir, labor):
        save_labor([labor], data_dir)
        updated = labor.model_copy(update={"hours": 4.0})
        merge_labor([updated], data_dir)
        loaded = load_labor(data_dir)
        assert len(loaded) == 1
        assert loaded[0].hours == 4.0


class TestOverheadRoundTrip:
    def test_round_trip(self, data_dir, overhead):
        save_overhead([overhead], data_dir)
        assert load_overhead(data_dir) == [overhead]

    def test_returns_empty_list_when_csv_missing(self, data_dir):
        assert load_overhead(data_dir) == []

    def test_merge_inserts_new_record(self, data_dir, overhead):
        merge_overhead([overhead], data_dir)
        assert load_overhead(data_dir) == [overhead]

    def test_merge_updates_existing_record(self, data_dir, overhead):
        save_overhead([overhead], data_dir)
        updated = overhead.model_copy(update={"rent": 10.0})
        merge_overhead([updated], data_dir)
        loaded = load_overhead(data_dir)
        assert len(loaded) == 1
        assert loaded[0].rent == 10.0
