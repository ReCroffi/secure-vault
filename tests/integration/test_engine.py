from sqlalchemy import text

from vault.db.engine import engine


def test_engine_connects(): 
    with engine.connect() as conn:
        resultado = conn.execute(text('SELECT 1'))
    
        assert resultado.scalar() == 1