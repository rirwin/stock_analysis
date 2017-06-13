from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String


Base = declarative_base()


class OrderHistory(Base):

    __tablename__ = 'order_history'

    date = Column(Integer, primary_key=True)
    ticker = Column(String, primary_key=True)
    num_shares = Column(Integer, primary_key=True)
    price = Column(Float, primary_key=True)
