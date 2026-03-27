import csv
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from precifique.core.models import Labor, Material, Overhead, Product

T = TypeVar("T", bound=BaseModel)


def _load(model_cls: type[T], path: Path) -> list[T]:
    if not path.exists():
        return []
    with open(path, newline="") as f:
        return [model_cls.model_validate(row) for row in csv.DictReader(f)]


def _save(items: list[T], path: Path, model_cls: type[T]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not items:
        path.write_text("")
        return
    fields = list(model_cls.model_fields.keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for item in items:
            writer.writerow(item.model_dump(mode="json"))


def _merge(incoming: list[T], path: Path, model_cls: type[T]) -> None:
    existing = {str(item.id): item for item in _load(model_cls, path)}
    for item in incoming:
        existing[str(item.id)] = item
    _save(list(existing.values()), path, model_cls)


def _products_path(data_dir: Path) -> Path:
    return data_dir / "products.csv"


def _materials_path(data_dir: Path) -> Path:
    return data_dir / "materials.csv"


def _labor_path(data_dir: Path) -> Path:
    return data_dir / "labor.csv"


def _overhead_path(data_dir: Path) -> Path:
    return data_dir / "overhead.csv"


def load_products(data_dir: Path) -> list[Product]:
    return _load(Product, _products_path(data_dir))


def save_products(products: list[Product], data_dir: Path) -> None:
    _save(products, _products_path(data_dir), Product)


def merge_products(incoming: list[Product], data_dir: Path) -> None:
    _merge(incoming, _products_path(data_dir), Product)


def load_materials(data_dir: Path) -> list[Material]:
    return _load(Material, _materials_path(data_dir))


def save_materials(materials: list[Material], data_dir: Path) -> None:
    _save(materials, _materials_path(data_dir), Material)


def merge_materials(incoming: list[Material], data_dir: Path) -> None:
    _merge(incoming, _materials_path(data_dir), Material)


def load_labor(data_dir: Path) -> list[Labor]:
    return _load(Labor, _labor_path(data_dir))


def save_labor(labor: list[Labor], data_dir: Path) -> None:
    _save(labor, _labor_path(data_dir), Labor)


def merge_labor(incoming: list[Labor], data_dir: Path) -> None:
    _merge(incoming, _labor_path(data_dir), Labor)


def load_overhead(data_dir: Path) -> list[Overhead]:
    return _load(Overhead, _overhead_path(data_dir))


def save_overhead(overhead: list[Overhead], data_dir: Path) -> None:
    _save(overhead, _overhead_path(data_dir), Overhead)


def merge_overhead(incoming: list[Overhead], data_dir: Path) -> None:
    _merge(incoming, _overhead_path(data_dir), Overhead)
