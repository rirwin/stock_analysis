from collections import namedtuple
import datetime
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from database.price_history import PriceHistory
from database import db


TickerDatePrice = namedtuple('TickerDatePrice', ['ticker', 'date', 'price'])
Session = sessionmaker(bind=db.engine)


class PriceHistoryLogic(object):

    def add_prices(self, ticker_date_prices):
        session = Session()
        for ticker_date_price in ticker_date_prices:
            session.add(
                PriceHistory(
                    date=ticker_date_price.date.isoformat(),
                    ticker=ticker_date_price.ticker,
                    price=ticker_date_price.price,
                )
            )
        session.commit()

    def get_max_date_history_for_ticker(self, ticker):
        session = Session()
        date_str = session.query(func.max(PriceHistory.date))\
            .filter_by(ticker=ticker)\
            .first()
        date = datetime.datetime.strptime(date_str[0], '%Y-%m-%d').date()
        session.close()
        return date

    def does_ticker_date_history_exists(self, ticker_date):
        session = Session()
        exists = session.query(PriceHistory.ticker)\
            .filter_by(ticker=ticker_date.ticker)\
            .filter_by(date=ticker_date.date)\
            .first()
        session.close()
        return bool(exists)

    def get_ticker_dates_prices(self, ticker_dates):
        session = Session()
        ticker_date_prices = []
        # TODO consider batching queries
        for ticker_date in ticker_dates:
            result = session.query(PriceHistory.price)\
                .filter_by(ticker=ticker_date.ticker)\
                .filter_by(date=ticker_date.date)\
                .first()
            ticker_date_prices.append(
                TickerDatePrice(
                    ticker=ticker_date.ticker,
                    date=ticker_date.date,
                    price=float(result[0])
                )
            )
        session.close()
        return ticker_date_prices

    def get_tickers_gains(self, tickers, date_range):
        session = Session()
        results = session.query(PriceHistory.ticker, PriceHistory.price)\
            .filter(PriceHistory.ticker.in_(tickers))\
            .filter(PriceHistory.date.in_(date_range))\
            .order_by(PriceHistory.ticker, PriceHistory.date)\
            .all()
        session.close()

        assert len(tickers) * 2 == len(results)
        idx = 0
        gains = []
        while idx < len(results):
            begin_price = results[idx][1]
            end_price = results[idx + 1][1]
            gain = 100 * (end_price - begin_price) / begin_price
            gains.append((results[idx][0], gain,))
            idx += 2
        return gains
