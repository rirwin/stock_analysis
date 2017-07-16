from collections import defaultdict
import datetime
from stock_analysis.commands import portfolio
from stock_analysis.commands.portfolio import PortfolioStockDetails
from stock_analysis import constants
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

    @db.in_sandbox
    def test_get_benchmark_comparison_to_order_prices(self):
        cmds = portfolio.PortfolioCommands()
        order1 = Order(
            user_id=self.user_id,
            order_type=order_history.BUY_ORDER_TYPE,
            ticker='AAPL',
            date=datetime.date(2017, 6, 8),
            num_shares=2,
            price=149.0,
        )
        order2 = Order(
            user_id=self.user_id,
            order_type=order_history.BUY_ORDER_TYPE,
            ticker='ATVI',
            date=datetime.date(2017, 6, 9),
            num_shares=3,
            price=170.0,
        )

        prices = [
            TickerDatePrice('AAPL', datetime.date(2017, 6, 8), 149.0),
            TickerDatePrice('AAPL', datetime.date(2017, 6, 9), 149.0),
            TickerDatePrice('AAPL', datetime.date(2017, 6, 12), 149.0),
            TickerDatePrice('AAPL', datetime.date(2017, 6, 13), 151.0),
            TickerDatePrice('AAPL', datetime.date(2017, 6, 14), 153.0),
            TickerDatePrice('AAPL', datetime.date(2017, 6, 15), 153.0),
            TickerDatePrice('ATVI', datetime.date(2017, 6, 9), 170.0),
            TickerDatePrice('ATVI', datetime.date(2017, 6, 12), 170.0),
            TickerDatePrice('ATVI', datetime.date(2017, 6, 13), 170.0),
            TickerDatePrice('ATVI', datetime.date(2017, 6, 14), 171.0),
            TickerDatePrice('ATVI', datetime.date(2017, 6, 15), 172.0),
        ]
        # benchmark ticker 0 stays flat, 1 goes down 1 per day, 2 goes up 2 per day
        benchmark_diffs = {k: v for (k, v) in zip(constants.BENCHMARK_TICKERS, [0, -1, 2])}
        base_benchmark_price = 1000.0  # for all benchmarks
        benchmark_prices = []
        dates = [  # create the list manually - need to skip the weekend :S
            datetime.date(2017, 6, 8),
            datetime.date(2017, 6, 9),
            datetime.date(2017, 6, 12),
            datetime.date(2017, 6, 13),
            datetime.date(2017, 6, 14),
            datetime.date(2017, 6, 15),
        ]
        for ticker in constants.BENCHMARK_TICKERS:
            days = 0
            for idx, date in enumerate(dates):
                benchmark_prices.append(
                    TickerDatePrice(
                        ticker,
                        date,
                        base_benchmark_price + benchmark_diffs[ticker] * idx
                    )
                )
                days += 1

        prices.extend(benchmark_prices)
        self.order_logic.add_orders([order1, order2])
        self.price_logic.add_prices(prices)

        expected_order_comps = defaultdict(list)
        aapl_gain = 100 * (prices[5].price - order1.price) / order1.price
        aapl_bench_gain = {
            k: (100 * (5 * benchmark_diffs[k]) / base_benchmark_price)
            for k in constants.BENCHMARK_TICKERS
        }
        aapl_comp_gains = {k: (aapl_gain - aapl_bench_gain[k]) for k in constants.BENCHMARK_TICKERS}
        atvi_gain = 100 * (prices[10].price - order2.price) / order2.price
        atvi_bench_gain = {
            k: (100 * (4 * benchmark_diffs[k]) / base_benchmark_price)
            for k in constants.BENCHMARK_TICKERS
        }
        atvi_comp_gains = {k: (atvi_gain - atvi_bench_gain[k]) for k in constants.BENCHMARK_TICKERS}
        expected_order_comps['AAPL'].append((order1, aapl_comp_gains, order1.price / (order1.price + order2.price)))
        expected_order_comps['ATVI'].append((order2, atvi_comp_gains, order2.price / (order1.price + order2.price)))

        order_comps = cmds.get_benchmark_comparison_to_order_prices(self.user_id)

        for ticker in ['AAPL', 'ATVI']:
            order_comp = order_comps[ticker][0]
            assert expected_order_comps[ticker][0][0] == order_comp[0]  # order
            assert expected_order_comps[ticker][0][2] == order_comp[2]  # weights
            bench_gains = order_comp[1]
            for bench_ticker, comp_gain in bench_gains.items():
                assert _nearly_equal(expected_order_comps[ticker][0][1][bench_ticker], comp_gain)

    @db.in_sandbox
    def test_get_benchmark_comparison_to_fixed_date_prices(self):
        cmds = portfolio.PortfolioCommands()
        order1 = Order(
            user_id=self.user_id,
            order_type=order_history.BUY_ORDER_TYPE,
            ticker='AAPL',
            date=datetime.date(2017, 6, 8),
            num_shares=2,
            price=149.0,
        )
        order2 = Order(
            user_id=self.user_id,
            order_type=order_history.BUY_ORDER_TYPE,
            ticker='ATVI',
            date=datetime.date(2017, 6, 9),
            num_shares=3,
            price=170.0,
        )

        prices = [
            TickerDatePrice('AAPL', datetime.date(2017, 6, 8), 149.0),
            TickerDatePrice('AAPL', datetime.date(2017, 6, 9), 149.0),
            TickerDatePrice('AAPL', datetime.date(2017, 6, 12), 149.0),
            TickerDatePrice('AAPL', datetime.date(2017, 6, 13), 151.0),
            TickerDatePrice('AAPL', datetime.date(2017, 6, 14), 153.0),
            TickerDatePrice('AAPL', datetime.date(2017, 6, 15), 153.0),
            TickerDatePrice('ATVI', datetime.date(2017, 6, 9), 170.0),
            TickerDatePrice('ATVI', datetime.date(2017, 6, 12), 170.0),
            TickerDatePrice('ATVI', datetime.date(2017, 6, 13), 170.0),
            TickerDatePrice('ATVI', datetime.date(2017, 6, 14), 171.0),
            TickerDatePrice('ATVI', datetime.date(2017, 6, 15), 172.0),
        ]
        # benchmark ticker 0 stays flat, 1 goes down 1 per day, 2 goes up 2 per day
        benchmark_diffs = {k: v for (k, v) in zip(constants.BENCHMARK_TICKERS, [0, -1, 2])}
        base_benchmark_price = 1000.0  # for all benchmarks
        benchmark_prices = []
        dates = [  # create the list manually - need to skip the weekend :S
            datetime.date(2017, 6, 8),
            datetime.date(2017, 6, 9),
            datetime.date(2017, 6, 12),
            datetime.date(2017, 6, 13),
            datetime.date(2017, 6, 14),
            datetime.date(2017, 6, 15),
        ]
        for ticker in constants.BENCHMARK_TICKERS:
            days = 0
            for idx, date in enumerate(dates):
                benchmark_prices.append(
                    TickerDatePrice(
                        ticker,
                        date,
                        base_benchmark_price + benchmark_diffs[ticker] * idx
                    )
                )
                days += 1

        prices.extend(benchmark_prices)
        self.order_logic.add_orders([order1, order2])
        self.price_logic.add_prices(prices)

        aapl_1d_gain = 100 * (prices[5].price - prices[4].price) / prices[4].price
        aapl_7d_gain = 100 * (prices[5].price - prices[0].price) / prices[0].price
        atvi_1d_gain = 100 * (prices[10].price - prices[9].price) / prices[9].price

        bench_1d_gains = {
            k: (100 * (1 * benchmark_diffs[k]) / base_benchmark_price)
            for k in constants.BENCHMARK_TICKERS
        }
        bench_7d_gains = {
            k: (100 * (5 * benchmark_diffs[k]) / base_benchmark_price)
            for k in constants.BENCHMARK_TICKERS
        }

        # Initialize to Nones
        comp_intervals = ['1dp', '7dp', '30dp', '90dp', '365dp']
        expected_comp_gains = {}
        for ticker in ['AAPL', 'ATVI']:
            expected_comp_gains[ticker] = {}
            for bench_ticker in constants.BENCHMARK_TICKERS:
                expected_comp_gains[ticker][bench_ticker] = {}
                for interval in comp_intervals:
                    expected_comp_gains[ticker][bench_ticker][interval] = None

        for bench_ticker in constants.BENCHMARK_TICKERS:
            expected_comp_gains['AAPL'][bench_ticker]['1dp'] = aapl_1d_gain - bench_1d_gains[bench_ticker]
            expected_comp_gains['AAPL'][bench_ticker]['7dp'] = aapl_7d_gain - bench_7d_gains[bench_ticker]
            expected_comp_gains['ATVI'][bench_ticker]['1dp'] = atvi_1d_gain - bench_1d_gains[bench_ticker]

        fixed_date_comps = cmds.get_benchmark_comparison_to_fixed_date_prices(self.user_id)
        for ticker in ['AAPL', 'ATVI']:
            for bench_ticker in constants.BENCHMARK_TICKERS:
                for interval in comp_intervals:
                    assert _nearly_equal(
                        fixed_date_comps[ticker][bench_ticker][interval],
                        expected_comp_gains[ticker][bench_ticker][interval]
                    )


def _nearly_equal(float1, float2, tolerance_percent=1.0):
    if (float1 is None and float2 is None) or (abs(float1 - float2) <= tolerance_percent / 100):
        return True
    return abs(float1 - float2) <= abs(float1 - float2 / float1) * (tolerance_percent / 100.0)
