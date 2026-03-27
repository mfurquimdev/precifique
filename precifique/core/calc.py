from precifique.core.models import Labor, Material, Overhead, PriceBreakdown, Product


def calculate_price(
    product: Product,
    materials: list[Material],
    labor: list[Labor],
    overhead: list[Overhead],
) -> PriceBreakdown:
    materials_subtotal = sum(m.unit_cost * m.quantity for m in materials)
    labor_subtotal = sum(l.hours * l.hourly_rate for l in labor)

    rent = sum(o.rent for o in overhead)
    tools = sum(o.tools for o in overhead)
    packaging = sum(o.packaging for o in overhead)
    shipping = sum(o.shipping for o in overhead)
    taxes = sum(o.taxes for o in overhead)
    overhead_subtotal = rent + tools + packaging + shipping + taxes

    total_cost = materials_subtotal + labor_subtotal + overhead_subtotal
    selling_price = total_cost / (1 - product.profit_margin / 100)

    return PriceBreakdown(
        product_name=product.name,
        materials_subtotal=materials_subtotal,
        labor_subtotal=labor_subtotal,
        overhead_subtotal=overhead_subtotal,
        rent=rent,
        tools=tools,
        packaging=packaging,
        shipping=shipping,
        taxes=taxes,
        total_cost=total_cost,
        profit_margin=product.profit_margin,
        selling_price=selling_price,
    )
