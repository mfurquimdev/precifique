import typer

from precifique.config import get_config
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

app = typer.Typer()
product_app = typer.Typer()
material_app = typer.Typer()
labor_app = typer.Typer()
overhead_app = typer.Typer()

app.add_typer(product_app, name="product", help="Manage your product catalog.")
app.add_typer(material_app, name="material", help="Manage materials.")
app.add_typer(labor_app, name="labor", help="Manage labor.")
app.add_typer(overhead_app, name="overhead", help="Manage overhead costs.")


@product_app.command("add")
def product_add(
    sku: str = typer.Option(..., prompt=True),
    name: str = typer.Option(..., prompt=True),
    profit_margin: float = typer.Option(..., "--profit-margin", prompt=True),
) -> None:
    from precifique.core.models import Product

    config = get_config()
    products = load_products(config.data_dir)

    product = Product(sku=sku, name=name, profit_margin=profit_margin)
    products.append(product)
    save_products(products, config.data_dir)

    typer.echo(f"Added product: {sku}")


@product_app.command("list")
def product_list() -> None:
    config = get_config()
    products = load_products(config.data_dir)

    if not products:
        typer.echo("No products in catalog.")
        return

    typer.echo(f"{'SKU':<20} {'Name':<30} {'Margin':>8}")
    typer.echo("-" * 60)
    for p in products:
        typer.echo(f"{p.sku:<20} {p.name:<30} {p.profit_margin:>7.1f}%")


@product_app.command("show")
def product_show(sku: str = typer.Argument(...)) -> None:
    config = get_config()
    products = load_products(config.data_dir)

    match = next((p for p in products if p.sku == sku), None)
    if match is None:
        typer.echo(f"Product '{sku}' not found.", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"SKU:           {match.sku}")
    typer.echo(f"Name:          {match.name}")
    typer.echo(f"Profit Margin: {match.profit_margin}%")


@product_app.command("delete")
def product_delete(sku: str = typer.Argument(...)) -> None:
    config = get_config()
    products = load_products(config.data_dir)

    remaining = [p for p in products if p.sku != sku]
    if len(remaining) == len(products):
        typer.echo(f"Product '{sku}' not found.", err=True)
        raise typer.Exit(code=1)

    save_products(remaining, config.data_dir)
    typer.echo(f"Deleted product: {sku}")


def _require_product(sku: str) -> None:
    config = get_config()
    products = load_products(config.data_dir)
    if not any(p.sku == sku for p in products):
        typer.echo(f"Product '{sku}' not found.", err=True)
        raise typer.Exit(code=1)


@material_app.command("add")
def material_add(
    product_sku: str = typer.Argument(...),
    name: str = typer.Option(..., prompt=True),
    unit_cost: float = typer.Option(..., "--unit-cost", prompt=True),
    quantity: float = typer.Option(..., prompt=True),
) -> None:
    from precifique.core.models import Material

    _require_product(product_sku)
    config = get_config()
    material = Material(product_sku=product_sku, name=name, unit_cost=unit_cost, quantity=quantity)
    materials = load_materials(config.data_dir)
    materials.append(material)
    save_materials(materials, config.data_dir)
    typer.echo(f"Added material '{name}' to {product_sku}.")


@labor_app.command("add")
def labor_add(
    product_sku: str = typer.Argument(...),
    hours: float = typer.Option(..., prompt=True),
    hourly_rate: float = typer.Option(..., "--hourly-rate", prompt=True),
) -> None:
    from precifique.core.models import Labor

    _require_product(product_sku)
    config = get_config()
    labor = Labor(product_sku=product_sku, hours=hours, hourly_rate=hourly_rate)
    labor_list = load_labor(config.data_dir)
    labor_list.append(labor)
    save_labor(labor_list, config.data_dir)
    typer.echo(f"Added labor to {product_sku}.")


@overhead_app.command("add")
def overhead_add(
    product_sku: str = typer.Argument(...),
    rent: float = typer.Option(..., prompt=True),
    tools: float = typer.Option(..., prompt=True),
    packaging: float = typer.Option(..., prompt=True),
    shipping: float = typer.Option(..., prompt=True),
    taxes: float = typer.Option(..., prompt=True),
) -> None:
    from precifique.core.models import Overhead

    _require_product(product_sku)
    config = get_config()
    overhead = Overhead(
        product_sku=product_sku,
        rent=rent, tools=tools, packaging=packaging, shipping=shipping, taxes=taxes,
    )
    overhead_list = load_overhead(config.data_dir)
    overhead_list.append(overhead)
    save_overhead(overhead_list, config.data_dir)
    typer.echo(f"Added overhead to {product_sku}.")
