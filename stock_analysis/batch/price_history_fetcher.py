import datetime
import pytz

from stock_analysis.logic.order import OrderHistoryLogic
from stock_analysis.logic.price import PriceHistoryLogic


class RowParserException(Exception):
    pass


USER_ID = 1

URL_TEMPLATE = 'http://www.google.com/finance/historical?' + \
    'q={exchange}:{ticker}&startdate={month}+{day}%2C+{year}&output=csv'


class PriceHistoryFetcher(object):

    def __init__(self):
        self.order_logic = OrderHistoryLogic()
        self.price_logic = PriceHistoryLogic()

    def run(self):
        ticker_dates = self.order_logic.get_tickers_and_min_dates_for_user(USER_ID)
        for ticker_date in ticker_dates:
            begin_date = self.price_logic.get_max_date_history_for_ticker(ticker_date.ticker)
            if not begin_date:
                begin_date = ticker_date.date
            data = self.fetch_ticker(ticker_date.ticker, begin_date)
        return data

    def fetch_ticker(self):
        pass

    def get_end_date(self):
        """Only get completed days data (after 4pm ET)
        Ignore weekends and holidays - the api won't return data
        """
        now_dt = datetime.datetime.now(pytz.timezone('US/Eastern'))
        if now_dt.hour >= 16:
            return now_dt.date()
        return (now_dt - datetime.timedelta(1)).date()


if __name__ == "__main__":
    PriceHistoryFetcher().run()
