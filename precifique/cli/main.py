import typer

from precifique.config import get_config
from precifique.core.storage import (
    load_products,
    save_products,
)

app = typer.Typer()
product_app = typer.Typer()
app.add_typer(product_app, name="product", help="Manage your product catalog.")


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
