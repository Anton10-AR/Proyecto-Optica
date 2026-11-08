from django import template

register = template.Library()


@register.filter
def dioptria(valor):
    """Graduación con signo y dos decimales, como se escribe en una receta: +1,25 · −0,50 · 0,00."""
    if valor is None or valor == '':
        return '—'
    if valor == 0:
        return '0,00'
    signo = '+' if valor > 0 else '−'
    return f'{signo}{abs(valor):.2f}'.replace('.', ',')


@register.filter
def eje(valor):
    return f'{valor}°' if valor is not None else '—'
