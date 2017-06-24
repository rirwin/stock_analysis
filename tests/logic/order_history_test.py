import datetime
from sqlalchemy.orm import sessionmaker

from database import db
from database.order_history import OrderHistory
from stock_analysis.logic import order_history
from stock_analysis.logic.order_history import Order
from stock_analysis.logic.order_history import OrderHistoryLogic
from stock_analysis.logic.order_history import TickerDate


Session = sessionmaker(bind=db.engine)


class TestOrderHistoryLogic(object):

    @db.in_sandbox
    def test_add_buy_orders(self):
        logic = OrderHistoryLogic()
        user_id = 1
        order = Order(
            user_id=user_id,
            order_type=order_history.BUY_ORDER_TYPE,
            date=datetime.date(2015, 8, 9),
            ticker='AAPL',
            num_shares=20,
            price=150.001,
        )
        logic.add_orders([order])

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
            user_id=user_id,
            order_type=order_history.BUY_ORDER_TYPE,
            date=datetime.date(2015, 8, 9),
            ticker='AAPL',
            num_shares=20,
            price=150.002,
        )
        order2 = Order(
            user_id=user_id,
            order_type=order_history.BUY_ORDER_TYPE,
            date=datetime.date(2017, 1, 1),
            ticker='AAPL',
            num_shares=20,
            price=152.333,
        )
        logic.add_orders([order1, order2])

        ticker_dates = logic.get_tickers_and_min_dates_for_user(user_id)

        assert ticker_dates == [TickerDate(order1.ticker, order1.date)]

    @db.in_sandbox
    def test_get_all_order_tickers_min_date(self):
        logic = OrderHistoryLogic()
        user_id_1 = 1
        user_id_2 = 2
        order1 = Order(
            user_id=user_id_1,
            order_type=order_history.BUY_ORDER_TYPE,
            date=datetime.date(2015, 8, 9),
            ticker='AAPL',
            num_shares=20,
            price=150.001,
        )
        order2 = Order(
            user_id=user_id_2,
            order_type=order_history.BUY_ORDER_TYPE,
            date=datetime.date(2017, 1, 1),
            ticker='AAPL',
            num_shares=20,
            price=152.333,
        )
        logic.add_orders([order1, order2])

        ticker_dates = logic.get_all_order_tickers_min_date()
        assert ticker_dates == [TickerDate(order1.ticker, order1.date)]
