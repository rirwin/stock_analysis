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

    user_id = 1
    gain_logic = GainHistoryLogic()
    order_logic = OrderHistoryLogic()
    price_logic = PriceHistoryLogic()

    @db.in_sandbox
    def test_percent_gain_single_purchase(self):
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

        self.order_logic.add_orders(self.user_id, [order])
        self.price_logic.add_prices(prices)

        assert self.gain_logic.get_percent_gain(self.user_id, order.ticker) == \
            100 * (prices[-1].price - order.price) / order.price

    @db.in_sandbox
    def test_percent_gain_double_purchase(self):
        order1 = Order(
            date=datetime.date(2017, 6, 12),
            ticker='AAPL',
            num_shares=2,
            price=150.0,
        )
        order2 = Order(
            date=datetime.date(2017, 6, 19),
            ticker='AAPL',
            num_shares=3,
            price=170.0,
        )
        prices = [
            TickerDatePrice(
                ticker='AAPL',
                date=order1.date + datetime.timedelta(days=x),
                price=order1.price + x
            )
            for x in range(5)
        ] + [                # Needed so there are no prices on weekends
            TickerDatePrice(
                ticker='AAPL',
                date=order2.date + datetime.timedelta(days=x),
                price=order2.price + x
            )
            for x in range(5)
        ]
        self.order_logic.add_orders(self.user_id, [order1, order2])
        self.price_logic.add_prices(prices)

        initial_value = order1.price * order1.num_shares + order2.price * order2.num_shares
        final_value = (order1.num_shares + order2.num_shares) * prices[-1].price
        assert self.gain_logic.get_percent_gain(self.user_id, order1.ticker) == \
            100 * (final_value - initial_value) / initial_value
