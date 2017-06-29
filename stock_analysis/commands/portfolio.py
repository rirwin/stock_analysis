from collections import defaultdict
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
        ticker_share_counts = self.order_logic.get_portfolio_shares_owned_on_date(user_id, end_date)
        tickers = sorted([x.ticker for x in ticker_share_counts])
        dates = [start_date, end_date]
        price_info = self.price_logic.get_ticker_price_history_map(tickers, dates)
        orders = self.order_logic.get_orders_for_user(user_id)

        # TODO consider pushing these dictionaries created here to the logic layer
        ticker_to_num_shares = {}
        for ticker_count in ticker_share_counts:
            ticker_to_num_shares[ticker_count.ticker] = ticker_count.num_shares

        # we have shares owned, ignore sell orders for porfolio details
        order_info = defaultdict(list)

        # sum bought shares
        for order in orders:
            order_info[order.ticker].append(order)

        retained_order_purchase_value = {}
        for k in order_info.keys():
            num_sold_to_remove = sum(
                o.num_shares for o in order_info[k]
                if o.order_type == order_history.SELL_ORDER_TYPE
            )
            buy_orders = [o for o in order_info[k] if o.order_type == order_history.BUY_ORDER_TYPE]
            # assume sold oldest shares
            buy_orders.sort(key=lambda order: order.date)
            for buy_order in buy_orders:
                if num_sold_to_remove > 0:
                    if buy_order.num_share - num_sold_to_remove >= 0:
                        buy_order.num_shares -= num_sold_to_remove
                        num_sold_to_remove = 0
                    else:
                        shares_to_remove = buy_order.num_shares
                        buy_order.num_shares = 0
                        num_sold_to_remove -= shares_to_remove

            retained_order_purchase_value[k] = sum(o.num_shares * o.price for o in buy_orders)

        port_value = sum(price_info[ticker][end_date] * ticker_to_num_shares[ticker] for ticker in tickers)

        return [
            PortfolioStockDetails(
                ticker=ticker,
                price=price_info[ticker][end_date],
                gain1dp=100 * (price_info[ticker][end_date] - price_info[ticker][start_date]) /
                    price_info[ticker][start_date],
                gain1dv=ticker_to_num_shares[ticker] * (price_info[ticker][end_date] - price_info[ticker][start_date]),
                gainp=100 * (price_info[ticker][end_date] * ticker_to_num_shares[ticker] -
                    retained_order_purchase_value[ticker]) / retained_order_purchase_value[ticker],
                gainv=ticker_to_num_shares[ticker] * price_info[ticker][end_date] -
                retained_order_purchase_value[ticker],
                portfoliop=100 * (ticker_to_num_shares[ticker] * price_info[ticker][end_date]) / port_value,
                value=ticker_to_num_shares[ticker] * price_info[ticker][end_date]
            )
            for ticker in tickers
        ]
