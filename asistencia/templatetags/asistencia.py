from datetime import timedelta

from django import template

register = template.Library()


@register.filter
def duracion(valor):
    """timedelta → «8:30» (horas:minutos)."""
    if not isinstance(valor, timedelta):
        return '—'
    minutos = int(valor.total_seconds() // 60)
    return f'{minutos // 60}:{minutos % 60:02d}'


@register.filter
def minutos(valor):
    """Minutos → «45 min» o «1 h 05 min»."""
    if not valor:
        return '—'
    return f'{valor} min' if valor < 60 else f'{valor // 60} h {valor % 60:02d} min'
