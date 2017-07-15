from collections import defaultdict
from collections import namedtuple
from stock_analysis.logic import order_history
from stock_analysis.logic import price_history
from stock_analysis import constants


PortfolioStockDetails = namedtuple(
    'PortfolioStockDetails',
    ['ticker', 'price', 'gain1dp', 'gain1dv', 'gainp', 'gainv', 'portfoliop', 'value']
)

# Get 1d for comparisons (then 1wk, 1mo, 3mo, 1yr)


class PortfolioCommands(object):

    order_logic = order_history.OrderHistoryLogic()
    price_logic = price_history.PriceHistoryLogic()

    def get_portfolio_details(self, user_id):
        (end_date, start_date) = self.price_logic.get_dates_last_two_sessions()
        ticker_to_num_shares = self.order_logic.get_portfolio_shares_owned_on_date(user_id, end_date)
        tickers = sorted(ticker_to_num_shares.keys())

        dates = [start_date, end_date]
        price_info = self.price_logic.get_ticker_price_history_map(tickers, dates)
        purchase_value, _ = self.order_logic.get_ticker_total_purchased_sold(user_id)

        port_value = sum(price_info[ticker][end_date] * ticker_to_num_shares[ticker] for ticker in tickers)

        return [
            PortfolioStockDetails(
                ticker=ticker,
                price=price_info[ticker][end_date],
                gain1dp=100 * (price_info[ticker][end_date] - price_info[ticker][start_date]) /
                    price_info[ticker][start_date],
                gain1dv=ticker_to_num_shares[ticker] * (price_info[ticker][end_date] - price_info[ticker][start_date]),
                gainp=100 * (price_info[ticker][end_date] * ticker_to_num_shares[ticker] -
                    purchase_value[ticker]) / purchase_value[ticker],
                gainv=ticker_to_num_shares[ticker] * price_info[ticker][end_date] -
                purchase_value[ticker],
                portfoliop=100 * (ticker_to_num_shares[ticker] * price_info[ticker][end_date]) / port_value,
                value=ticker_to_num_shares[ticker] * price_info[ticker][end_date]
            )
            for ticker in tickers
        ]

    def get_benchmark_comparison_to_order_prices(self, user_id):
        """Each purchase order should be compared against what would've happened if a benchmark was bought instead"""
        # get every order (assume only buys for now - think about how to handle sold)
        orders = self.order_logic.get_orders_for_user(user_id)
        tickers = set([o.ticker for o in orders if o.order_type == order_history.BUY_ORDER_TYPE])
        tickers = list(tickers)
        order_tickers = list(tickers)
        tickers.extend(constants.BENCHMARK_TICKERS)
        dates = set([o.date for o in orders if o.order_type == order_history.BUY_ORDER_TYPE])
        historical_dates = self.price_logic.get_benchmark_history_dates()
        dates.update(historical_dates)
        ticker_date_price_map = self.price_logic.get_ticker_price_history_map(tickers, dates)

        curr_date = historical_dates[0]

        # compute the purchase date vs a decision not to purchase {each bench ticker}
        total_assets_purchased = sum(o.price for o in orders if o.order_type == order_history.BUY_ORDER_TYPE)
        order_comps = defaultdict(list)  # {ticker: [(order, gain, weight)]
        for order in orders:
            order_gain = 100 * (ticker_date_price_map[order.ticker][curr_date] - order.price) / order.price
            weight = order.price / total_assets_purchased
            gain_info = {}
            for comp_ticker in constants.BENCHMARK_TICKERS:
                comp_curr_price = ticker_date_price_map[comp_ticker][curr_date]
                comp_start_price = ticker_date_price_map[comp_ticker][order.date]
                comp_gain = 100 * (comp_curr_price - comp_start_price) / comp_start_price
                gain_info[comp_ticker] = order_gain - comp_gain

            order_comps[order.ticker].append((order, gain_info, weight))
        return order_comps

    def get_benchmark_comparison_to_fixed_date_prices(self, user_id):
        """Each purchase order should be compared against what would've happened if owned a benchmark
        stock in the last x days instead
        """
        # get every order (assume only buys for now - think about how to handle sold)
        orders = self.order_logic.get_orders_for_user(user_id)
        tickers = set([o.ticker for o in orders if o.order_type == order_history.BUY_ORDER_TYPE])
        tickers = list(tickers)
        order_tickers = list(tickers)
        tickers.extend(constants.BENCHMARK_TICKERS)
        dates = set([o.date for o in orders if o.order_type == order_history.BUY_ORDER_TYPE])
        historical_dates = self.price_logic.get_benchmark_history_dates()
        dates.update(historical_dates)
        ticker_date_price_map = self.price_logic.get_ticker_price_history_map(tickers, dates)

        # for each benchmark ticker
        #    - compute {1, 7, 30, 90, 365} day comp with {each bench ticker}
        curr_date = historical_dates[0]
        fixed_date_comps = {}
        for ticker in order_tickers:
            fixed_date_comps[ticker] = {}
            curr_ticker_price = ticker_date_price_map[ticker][curr_date]
            for benchmark_ticker in constants.BENCHMARK_TICKERS:
                fixed_date_comps[ticker][benchmark_ticker] = {}
                curr_benchmark_price = ticker_date_price_map[benchmark_ticker][curr_date]
                for date, label in zip(historical_dates[1:], ['1dp', '7dp', '30dp', '90dp', '365dp']):
                    historical_benchmark_price = ticker_date_price_map[benchmark_ticker].get(date)
                    historical_ticker_price = ticker_date_price_map[ticker].get(date)
                    if historical_benchmark_price is not None and historical_ticker_price is not None:
                        benchmark_gain = 100 * (curr_benchmark_price - historical_benchmark_price) / historical_benchmark_price
                        ticker_gain = 100 * (curr_ticker_price - historical_ticker_price) / historical_ticker_price
                        fixed_date_comps[ticker][benchmark_ticker][label] = ticker_gain - benchmark_gain
                    else:
                        fixed_date_comps[ticker][benchmark_ticker][label] = None

        return fixed_date_comps
