from collections import namedtuple
import datetime
import logging
import pytz
import requests
import time

from stock_analysis.logic.order_history import OrderHistoryLogic
from stock_analysis.logic.order_history import TickerDate
from stock_analysis.logic.price_history import PriceHistoryLogic
from stock_analysis.logic.price_history import TickerDatePrice
from stock_analysis import constants


logging.basicConfig(level=logging.INFO)
module_name = __file__.split('/')[-1].split('.')[0]
logger = logging.getLogger(module_name)


DatePrice = namedtuple('DatePrice', ['date', 'price'])


class RowParserException(Exception):
    pass


URL_TEMPLATE = 'http://www.google.com/finance/historical?' + \
    'q={exchange}:{ticker}&startdate={month}+{day}%2C+{year}&output=csv'


class GooglePriceHistoryFetcher(object):

    def __init__(self):
        self.order_logic = OrderHistoryLogic()
        self.price_logic = PriceHistoryLogic()
        self.log = logger

    def run(self):
        ticker_min_order_dates = self.order_logic.get_all_order_tickers_min_date()
        for ticker_date in ticker_min_order_dates:
            self.process_ticker_order_date(ticker_date)

    def process_ticker_order_date(self, ticker_date):
        self.log.info("Processing ticker %s" % ticker_date.ticker)
        fetch_date = self.get_fetch_date(ticker_date)
        if self.should_fetch_data_for_date(fetch_date):
            self.log.info(
                "Fetch history for ticker %s to %s" %
                (ticker_date.ticker, fetch_date.isoformat())
            )
            history = self.fetch_ticker_history(TickerDate(ticker_date.ticker, fetch_date))
            self.price_logic.add_prices(history)

    def get_fetch_date(self, ticker_min_order_date):
        """gets a date that could be fetched,
        either the min order date or max history date + 1
        """
        if self.price_logic.does_ticker_date_history_exists(ticker_min_order_date):
            return self.price_logic.get_max_date_history_for_ticker(
                ticker_min_order_date.ticker
            ) + datetime.timedelta(days=1)
        return ticker_min_order_date.date

    def fetch_ticker_history(self, ticker_date):
        self.log.info("...Fetching data from % to now..." % ticker_date.date.isoformat())
        url = self._form_url(ticker_date)
        # TODO check throttle
        time.sleep(1)  # Sleep to throttle hitting api
        response = requests.get(url)
        content = response.content
        data = self._parse_historical(content)
        return [TickerDatePrice(ticker_date.ticker, x.date, x.price) for x in data]

    def should_fetch_data_for_date(self, fetch_date):
        """See if there is possibly new data to fetch.
        fetch_date is the max_history date + 1 or order date if no history exists.
        Cases not to fetch:
        (1) fetch_date is today.
        (2) fetch_date is yesterday (not Friday) and it's after today's close.
        (3) fetch_date is a Friday and it's not Monday after close.
        """
        now_dt = datetime.datetime.now(pytz.timezone('US/Eastern'))
        fetch_weekday = fetch_date.weekday()
        day_diff = (now_dt.date() - fetch_date).days

        now_is_after_close = False
        if now_dt.hour >= 16:
            now_is_after_close = True

        if fetch_weekday < 4:  # Mon-Thurs
            if (day_diff == 1 and now_is_after_close) or day_diff >= 2:
                return True

        if fetch_weekday >= 4:  # Friday
            if (day_diff == 3 and now_is_after_close) or day_diff >= 4:
                return True

        self.log.info("...Skipping fetch, no new data...")
        return False

    def _form_url(self, ticker_date):
        '''http://www.google.com/finance/historical?q=NASDAQ:AAPL&startdate=May+24%2C+2017&output=csv'''
        return URL_TEMPLATE.format(
            exchange=constants.ticker_name_to_exchange[ticker_date.ticker],
            ticker=ticker_date.ticker,
            month=ticker_date.date.strftime('%B'),
            day=ticker_date.date.day,
            year=ticker_date.date.year
        )

    def _parse_historical(self, content):
        lines = content.decode().strip().split('\n')
        rows = []
        for line in lines[1:]:  # Skip the header row
            rows.append(self._parse_line(line))
        return sorted(rows, key=lambda x: x.date)

    def _parse_line(self, line):
        """Parse line in format 2-Jun-17,153.58,155.45,152.89,155.45,27770715
        The second to last field is the closing price.
        """
        fields = line.split(',')
        date = self._parse_date(fields[0])
        close = float(fields[-2])
        return DatePrice(date, close)

    def _parse_date(self, date_str):
        """Parse date in format 26-May-17"""
        return datetime.datetime.strptime(date_str, "%d-%b-%y").date()


if __name__ == "__main__":
    GooglePriceHistoryFetcher().run()
