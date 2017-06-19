import datetime
from sqlalchemy.orm import sessionmaker

from database import db
from stock_analysis.logic.gain_history import GainHistoryLogic
from stock_analysis.logic.order_history import Order
from stock_analysis.logic.order_history import OrderHistoryLogic
from stock_analysis.logic.price_history import PriceHistoryLogic
from stock_analysis.logic.price_history import TickerDatePrice


Session = sessionmaker(bind=db.engine)


class TestGainHistoryLogic(object):

    @db.in_sandbox
    def test_percent_gain_single_purchase(self):
        gain_logic = GainHistoryLogic()
        order_logic = OrderHistoryLogic()
        price_logic = PriceHistoryLogic()
        user_id = 1
        order = Order(
            date=datetime.date(2017, 6, 12),
            ticker='AAPL',
            num_shares=1,
            price=150.0,
        )
        prices = [
            TickerDatePrice(
                ticker='AAPL',
                date=order.date + datetime.timedelta(days=x),
                price=order.price + x
            )
            for x in range(5)
        ]

        order_logic.add_orders(user_id, [order])
        price_logic.add_prices(prices)

        assert gain_logic.get_percent_gain(user_id, order.ticker) == \
            100 * (prices[-1].price - order.price) / order.price
