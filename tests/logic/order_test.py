import datetime
from sqlalchemy.orm import sessionmaker

from database import db
from database.order_history import OrderHistory
from stock_analysis.logic.order import Order
from stock_analysis.logic.order import OrderHistoryLogic
from stock_analysis.logic.order import TickerDate


Session = sessionmaker(bind=db.engine)


class TestOrderHistoryLogic(object):

    @db.in_sandbox
    def test_add_orders(self):
        logic = OrderHistoryLogic()
        user_id = 1
        order = Order(
            date=datetime.date(2015, 8, 9),
            ticker='AAPL',
            num_shares=20,
            price=150.001,
        )
        logic.add_orders(user_id, [order])

        session = Session()

        resp = session.query(OrderHistory).all()
        assert len(resp) == 1
        order_in_db = resp[0]
        assert order_in_db.user_id == user_id
        assert order_in_db.date == order.date.isoformat()
        assert order_in_db.ticker == order.ticker
        assert order_in_db.num_shares == order.num_shares
        assert order_in_db.price == order.price

        session.close()

    @db.in_sandbox
    def test_get_tickers_and_min_dates_for_user(self):
        logic = OrderHistoryLogic()
        user_id = 1
        order1 = Order(
            date=datetime.date(2015, 8, 9),
            ticker='AAPL',
            num_shares=20,
            price=150.001,
        )
        order2 = Order(
            date=datetime.date(2017, 1, 1),
            ticker='AAPL',
            num_shares=20,
            price=152.333,
        )
        logic.add_orders(user_id, [order1, order2])

        ticker_dates = logic.get_tickers_and_min_dates_for_user(user_id)

        assert ticker_dates == [TickerDate(order1.ticker, order1.date)]
