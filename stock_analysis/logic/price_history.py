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
