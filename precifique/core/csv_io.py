import csv
from pathlib import Path
from typing import Any

from precifique.core.models import Labor, Material, Overhead, Product
from precifique.core.storage import (
    load_labor,
    load_materials,
    load_overhead,
    load_products,
    save_labor,
    save_materials,
    save_overhead,
    save_products,
)

_ENTITY_MAP = {
    "products": {
        "load": load_products,
        "save": save_products,
        "model": Product,
        "fields": ["id", "sku", "name", "profit_margin"],
    },
    "materials": {
        "load": load_materials,
        "save": save_materials,
        "model": Material,
        "fields": ["id", "product_sku", "name", "unit_cost", "quantity"],
    },
    "labor": {
        "load": load_labor,
        "save": save_labor,
        "model": Labor,
        "fields": ["id", "product_sku", "hours", "hourly_rate"],
    },
    "overhead": {
        "load": load_overhead,
        "save": save_overhead,
        "model": Overhead,
        "fields": ["id", "product_sku", "rent", "tools", "packaging", "shipping", "taxes"],
    },
}


def export_entity(entity: str, file_path: Path, data_dir: Path) -> None:
    meta = _ENTITY_MAP[entity]
    records = meta["load"](data_dir)
    fields = meta["fields"]
    with open(file_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow({k: str(getattr(record, k)) for k in fields})


def import_entity(entity: str, file_path: Path, data_dir: Path) -> int:
    """Merge records by ID. Returns count of records processed."""
    meta = _ENTITY_MAP[entity]
    fields = meta["fields"]
    model_cls = meta["model"]

    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or not set(fields).issubset(set(reader.fieldnames)):
            missing = set(fields) - set(reader.fieldnames or [])
            raise ValueError(f"CSV missing required columns: {missing}")
        rows = list(reader)

    existing = meta["load"](data_dir)
    existing_by_id = {str(r.id): r for r in existing}

    for row in rows:
        record = model_cls(**{k: row[k] for k in fields})
        existing_by_id[str(record.id)] = record

    meta["save"](list(existing_by_id.values()), data_dir)
    return len(rows)
