from sqlalchemy.orm import sessionmaker

from vault.db.engine import engine

Session = sessionmaker(bind=engine)
