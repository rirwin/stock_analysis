import datetime
from stock_analysis.commands import portfolio
from stock_analysis.commands.portfolio import PortfolioStockDetails
from stock_analysis.logic import order_history
from stock_analysis.logic.order_history import Order
from stock_analysis.logic import price_history
from stock_analysis.logic.price_history import TickerDatePrice
from database import db


class TestPortfolioCommands(object):

    user_id = 1
    order_logic = order_history.OrderHistoryLogic()
    price_logic = price_history.PriceHistoryLogic()

    @db.in_sandbox
    def test_get_portfolio_details(self):
        cmds = portfolio.PortfolioCommands()
        order1 = Order(
            user_id=self.user_id,
            order_type=order_history.BUY_ORDER_TYPE,
            ticker='AAPL',
            date=datetime.date(2017, 6, 12),
            num_shares=2,
            price=150.0,
        )
        order2 = Order(
            user_id=self.user_id,
            order_type=order_history.BUY_ORDER_TYPE,
            ticker='ATVI',
            date=datetime.date(2017, 6, 13),
            num_shares=3,
            price=170.0,
        )

        prices1 = [
            TickerDatePrice('AAPL', datetime.date(2017, 6, 12), 149.0),
            TickerDatePrice('AAPL', datetime.date(2017, 6, 13), 151.0),
            TickerDatePrice('AAPL', datetime.date(2017, 6, 14), 153.0),
            TickerDatePrice('AAPL', datetime.date(2017, 6, 15), 153.0),
        ]
        prices2 = [
            TickerDatePrice('ATVI', datetime.date(2017, 6, 13), 170.0),
            TickerDatePrice('ATVI', datetime.date(2017, 6, 14), 171.0),
            TickerDatePrice('ATVI', datetime.date(2017, 6, 15), 172.0),
        ]
        self.order_logic.add_orders([order1, order2])
        self.price_logic.add_prices(prices1)
        self.price_logic.add_prices(prices2)

        details = cmds.get_portfolio_details(self.user_id)
        port_value = order1.num_shares * prices1[-1].price + order2.num_shares * prices2[-1].price
        expected = [
            PortfolioStockDetails(
                ticker=order1.ticker,
                price=prices1[-1].price,
                gain1dp=100 * (prices1[-1].price - prices1[-2].price) / prices1[-2].price,
                gain1dv=order1.num_shares * (prices1[-1].price - prices1[-2].price),
                gainp=100 * (prices1[-1].price - order1.price) / order1.price,
                gainv=order1.num_shares * (prices1[-1].price - order1.price),
                portfoliop=100 * (order1.num_shares * prices1[-1].price) / port_value,
                value=order1.num_shares * prices1[-1].price,
            ),
            PortfolioStockDetails(
                ticker=order2.ticker,
                price=prices2[-1].price,
                gain1dp=100 * (prices2[-1].price - prices2[-2].price) / prices2[-2].price,
                gain1dv=order2.num_shares * (prices2[-1].price - prices2[-2].price),
                gainp=100 * (prices2[-1].price - order2.price) / order2.price,
                gainv=order2.num_shares * (prices2[-1].price - order2.price),
                portfoliop=100 * (order2.num_shares * prices2[-1].price) / port_value,
                value=order2.num_shares * prices2[-1].price,
            ),
        ]
        assert details == expected
        # TODO 1wk, 1mo, 3mo, 1yr stats for stock
