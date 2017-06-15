from collections import namedtuple
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

    #def get_tickers_and_min_dates_for_user(self, user_id):
    #    session = Session()
    #    query = '''
    #    SELECT
    #            min(date) AS date,
    #            ticker
    #    FROM
    #            order_history
    #    WHERE
    #            user_id = {user_id}
    #    GROUP
    #    BY
    #            ticker
    #    '''.format(user_id=user_id)
    #    results = session.fetch_many(query)
    #    session.close()
    #    return results
