from sqlalchemy import text


def test_engine_connects(db_engine):
    with db_engine.connect() as conn:
        resultado = conn.execute(text("SELECT 1"))

        assert resultado.scalar() == 1
