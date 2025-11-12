from functools import lru_cache
from sqlalchemy import inspect

from app import db


@lru_cache(maxsize=1)
def _questao_columns():
    """Cache columns available in the ``questoes`` table."""
    inspector = inspect(db.engine)
    return {column['name'] for column in inspector.get_columns('questoes')}


def questao_has_column(name: str) -> bool:
    """Verifica se a coluna existe na tabela ``questoes``."""
    return name in _questao_columns()
