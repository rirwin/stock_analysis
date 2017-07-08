from collections import namedtuple
from stock_analysis.logic import order_history
from stock_analysis.logic import price_history


PortfolioStockDetails = namedtuple(
    'PortfolioStockDetails',
    ['ticker', 'price', 'gain1dp', 'gain1dv', 'gainp', 'gainv', 'portfoliop', 'value']
)


class PortfolioCommands(object):

    order_logic = order_history.OrderHistoryLogic()
    price_logic = price_history.PriceHistoryLogic()

    def get_portfolio_details(self, user_id):
        (end_date, start_date) = self.price_logic.get_dates_last_two_sessions()
        ticker_to_num_shares = self.order_logic.get_portfolio_shares_owned_on_date(user_id, end_date)
        tickers = sorted(ticker_to_num_shares.keys())

        # benchmark_tickers = ['SPY', 'QQQ']

        dates = [start_date, end_date]  # Add 1 week, 1mo, 3mo
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
            # TODO - 2 things - get data for IJR and handle general case better if data is missing
            if ticker != 'IJR'
        ]
