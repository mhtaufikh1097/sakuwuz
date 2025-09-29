from django import template

register = template.Library()

@register.filter
def rupiah(value):
    try:
        n = float(value or 0)
    except (TypeError, ValueError):
        n = 0
    parts = f"{n:,.2f}".split(".")
    main = parts[0].replace(",", ".")
    frac = parts[1]
    return f"Rp {main},{frac}"
