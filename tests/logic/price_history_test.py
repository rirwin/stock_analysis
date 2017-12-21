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
    def test_get_ticker_dates_prices(self):
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

        ticker_date_prices = logic.get_ticker_dates_prices([
            TickerDate(price1.ticker, price1.date),
            TickerDate(price2.ticker, price2.date),
        ])
        assert set(ticker_date_prices) == set([price1, price2])

    @db.in_sandbox
    def test_get_ticker_price_history_map(self):
        logic = PriceHistoryLogic()
        ticker1 = 'AAPL'
        ticker2 = 'ATVI'
        date1 = datetime.date(2017, 6, 26)
        date2 = datetime.date(2017, 6, 27)

        price1 = TickerDatePrice(
            ticker=ticker1,
            date=date1,
            price=150.0
        )
        price2 = TickerDatePrice(
            ticker=ticker1,
            date=date2,
            price=170.0
        )
        price3 = TickerDatePrice(
            ticker=ticker2,
            date=date1,
            price=120.0
        )
        price4 = TickerDatePrice(
            ticker=ticker2,
            date=date2,
            price=130.0
        )
        logic.add_prices([price1, price2, price3, price4])
        history_map = logic.get_ticker_price_history_map([ticker1, ticker2], [date1, date2])
        expected_map = {
            ticker1: {date1: price1.price, date2: price2.price},
            ticker2: {date1: price3.price, date2: price4.price},
        }
        assert history_map == expected_map

    @db.in_sandbox
    def test_get_tickers_gains(self):
        logic = PriceHistoryLogic()
        ticker1 = 'AAPL'
        price1a = TickerDatePrice(
            ticker=ticker1,
            date=datetime.date(2017, 6, 26),
            price=150.0
        )
        price1b = TickerDatePrice(
            ticker=ticker1,
            date=datetime.date(2017, 6, 30),
            price=170.0
        )
        ticker2 = 'ATVI'
        price2a = TickerDatePrice(
            ticker=ticker2,
            date=datetime.date(2017, 6, 26),
            price=60.0
        )
        price2b = TickerDatePrice(
            ticker=ticker2,
            date=datetime.date(2017, 6, 30),
            price=65.0
        )
        logic.add_prices([price1a, price1b, price2a, price2b])

        gains = logic.get_tickers_gains(
            [ticker1, ticker2],
            (price1a.date, price1b.date),
        )
        gain1 = 100 * (price1b.price - price1a.price) / price1a.price
        gain2 = 100 * (price2b.price - price2a.price) / price2a.price
        assert set(gains) == set([(ticker1, gain1,), (ticker2, gain2,)])

    @db.in_sandbox
    def test_get_dates_last_two_sessions(self):
        logic = PriceHistoryLogic()
        price0 = TickerDatePrice(
            ticker='AAPL',
            date=datetime.date(2017, 6, 21),
            price=149.001,
        )
        price1 = TickerDatePrice(
            ticker='AAPL',
            date=datetime.date(2017, 6, 22),
            price=150.001,
        )
        price2 = TickerDatePrice(
            ticker='AAPL',
            date=datetime.date(2017, 6, 23),
            price=152.333,
        )
        logic.add_prices([price0, price1, price2])

        dates = logic.get_dates_last_two_sessions()

        assert dates == (price2.date, price1.date)
