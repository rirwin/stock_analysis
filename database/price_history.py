from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String


Base = declarative_base()


class PriceHistory(Base):

    __tablename__ = 'price_history'

    date = Column(Integer, primary_key=True)
    ticker = Column(String, primary_key=True)
    price = Column(Float, primary_key=True)


if __name__ == "__main__":
    from database import db
    Base.metadata.create_all(db.engine)
