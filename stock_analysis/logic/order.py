from collections import namedtuple
import datetime
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from database.order_history import OrderHistory
from database import db


Order = namedtuple('Order', ['ticker', 'date', 'num_shares', 'price'])
TickerDate = namedtuple('TickerDate', ['ticker', 'date'])
Session = sessionmaker(bind=db.engine)


class OrderHistoryLogic(object):

    def add_orders(self, user_id, orders):
        session = Session()
        for order in orders:
            session.add(
                OrderHistory(
                    user_id=user_id,
                    date=order.date,
                    ticker=order.ticker,
                    num_shares=order.num_shares,
                    price=order.price,
                )
            )
        session.commit()

    def get_tickers_and_min_dates_for_user(self, user_id):
        session = Session()
        resp = session.query(OrderHistory.ticker, func.min(OrderHistory.date))\
            .filter_by(user_id=user_id)\
            .group_by(OrderHistory.ticker)\
            .all()
        ticker_dates = [
            TickerDate(x[0], datetime.datetime.strptime(x[1], '%Y-%m-%d').date())
            for x in resp
        ]
        session.close()
        return ticker_dates

    def get_all_order_tickers_min_date(self):
        session = Session()
        resp = session.query(OrderHistory.ticker, func.min(OrderHistory.date))\
            .group_by(OrderHistory.ticker)\
            .all()
        ticker_dates = [
            TickerDate(x[0], datetime.datetime.strptime(x[1], '%Y-%m-%d').date())
            for x in resp
        ]
        session.close()
        return ticker_dates
