"""
Utilidades compartilhadas entre modelos
"""
from datetime import datetime, date


def coerce_date(value, field_name):
    """
    Garante que valores destinados a colunas Date sejam objetos date.

    Accepts:
        - date: retornado diretamente
        - datetime: convertido para date
        - str: interpretado via ISO format (YYYY-MM-DD)
        - None: permitido
    """
    if value is None:
        return None

    if isinstance(value, date) and not isinstance(value, datetime):
        return value

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f'Formato de data inválido para {field_name}') from exc

    raise TypeError(f'Valor inválido para {field_name}: {value!r}')
