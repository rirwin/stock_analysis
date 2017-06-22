import datetime
from sqlalchemy.orm import sessionmaker

from database import db
from database.price_history import PriceHistory
from stock_analysis.logic.price_history import PriceHistoryLogic
from stock_analysis.logic.price_history import TickerDatePrice
from stock_analysis.logic.order_history import TickerDate


Session = sessionmaker(bind=db.engine)


class TestPriceHistoryLogic(object):

    @db.in_sandbox
    def test_add_prices(self):
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

    @db.in_sandbox
    def test_does_ticker_date_history_exists_true_case(self):
        logic = PriceHistoryLogic()
        price = TickerDatePrice(
            ticker='AAPL',
            date=datetime.date(2015, 8, 9),
            price=150.001,
        )
        logic.add_prices([price])

        assert logic.does_ticker_date_history_exists(TickerDate(price.ticker, price.date))

    @db.in_sandbox
    def test_does_ticker_date_history_exists_false_case(self):
        logic = PriceHistoryLogic()
        ticker = 'AAPL'
        date = datetime.date(2015, 8, 9)

        assert not logic.does_ticker_date_history_exists(TickerDate(ticker, date))

    @db.in_sandbox
    def test_get_gain_time_range(self):
        logic = PriceHistoryLogic()
        ticker = 'AAPL'
        price1 = TickerDatePrice(
            ticker=ticker,
            date=datetime.date(2017, 6, 26),
            price=150.0
        )
        price2 = TickerDatePrice(
            ticker=ticker,
            date=datetime.date(2017, 6, 30),
            price=170.0
        )
        logic.add_prices([price1])
        logic.add_prices([price2])

        assert logic.get_gain_time_range('AAPL', (price1.date, price2.date)) == \
            100 * (price2.price - price1.price) / (price1.price)
