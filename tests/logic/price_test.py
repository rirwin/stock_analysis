import datetime
from sqlalchemy.orm import sessionmaker

from database import db
from database.price_history import PriceHistory
from stock_analysis.logic.price import PriceHistoryLogic
from stock_analysis.logic.price import TickerDatePrice


Session = sessionmaker(bind=db.engine)


class TestPriceHistoryLogic(object):

    @db.in_sandbox
    def test_add_pricess(self):
        logic = PriceHistoryLogic()
        price = TickerDatePrice(
            ticker='AAPL',
            date=datetime.date(2015, 8, 9),
            price=150.001,
        )
        logic.add_prices([price])

        session = Session()

        resp = session.query(PriceHistory).all()
        assert len(resp) == 1
        price_in_db = resp[0]
        assert price_in_db.date == price.date.isoformat()
        assert price_in_db.ticker == price.ticker
        assert price_in_db.price == price.price

        session.close()

    @db.in_sandbox
    def test_get_max_date_history_for_ticker(self):
        logic = PriceHistoryLogic()
        price1 = TickerDatePrice(
            ticker='AAPL',
            date=datetime.date(2015, 8, 9),
            price=150.001,
        )
        price2 = TickerDatePrice(
            ticker='AAPL',
            date=datetime.date(2015, 8, 10),
            price=152.333,
        )
        logic.add_prices([price1, price2])

        max_date = logic.get_max_date_history_for_ticker(price1.ticker)

        assert max_date == price2.date
