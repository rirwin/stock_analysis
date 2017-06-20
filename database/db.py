import os
from sqlalchemy import create_engine

from database.order_history import OrderHistory
from database.price_history import PriceHistory
from database.order_history import Base as OrderBase
from database.price_history import Base as PriceBase


if os.environ.get('USE_TEST_DB') is not None:
    engine = create_engine('sqlite://')
else:
    engine = create_engine('sqlite:///database/stock_history.sqlite3db')


def create_all_tables():
    OrderBase.metadata.create_all(engine)
    PriceBase.metadata.create_all(engine)


def drop_all_tables():
    OrderHistory.__table__.drop(engine)
    PriceHistory.__table__.drop(engine)


def in_sandbox(func):
    def new_func(*args, **kwargs):
        create_all_tables()
        try:
            func(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            drop_all_tables()
    return new_func
