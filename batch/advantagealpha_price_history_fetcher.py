from collections import namedtuple
import datetime
import json
import logging
import pytz
import requests
import time

from stock_analysis.logic.order_history import OrderHistoryLogic
from stock_analysis.logic.order_history import TickerDate
from stock_analysis.logic.price_history import PriceHistoryLogic
from stock_analysis.logic.price_history import TickerDatePrice


logging.basicConfig(level=logging.INFO)
module_name = __file__.split('/')[-1].split('.')[0]
logger = logging.getLogger(module_name)


DatePrice = namedtuple('DatePrice', ['date', 'price'])


class RowParserException(Exception):
    pass


API_KEY = 'GET_KEY_FOR_FREE'
API_KEY = 'AZQX3LJX6ENWPYXR'
URL_TEMPLATE = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY' + \
    '&symbol={ticker}&apikey={api_key}&outputsize=compact'


class AlphavantagePriceHistoryFetcher(object):

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
        self.log.info("...Fetching data from %s to now..." % ticker_date.date.isoformat())
        url = self._form_url(ticker_date)
        # TODO check throttle
        time.sleep(1)  # Sleep to throttle hitting api
        response = requests.get(url)
        content = response.content
        data = self._parse_historical(content)
        data = [d for d in data if d.date >= ticker_date.date]
        assert data[0].date == ticker_date.date
        assert data[0].ticker == ticker_date.ticker
        return data

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

        if fetch_weekday <= 4:  # Mon-Friday
            if (day_diff == 0 and now_is_after_close) or day_diff >= 1:
                return True

        if fetch_weekday > 4:  # Saturday (data for week exists)
            if (day_diff == 2 and now_is_after_close) or day_diff >= 3:
                return True

        self.log.info("...Skipping fetch, no new data...")
        return False

    def _form_url(self, ticker_date):
        return URL_TEMPLATE.format(
            ticker=ticker_date.ticker,
            api_key=API_KEY,
        )

    def _parse_historical(self, content):
        """Gets bytes of json and returns lines of TickerDatePrice tuples
        { "Meta Data": {  "2. Symbol": "MOMO"},
          "Time Series (Daily)": {
            "2017-12-20": { "4. close": "26.0200", },
            "2017-12-19": { "4. close": "25.8600", },
        }
        """
        data = json.loads(content.decode())
        rows = []
        ticker = data['Meta Data']['2. Symbol']
        for date_str, price_data_point in data['Time Series (Daily)'].items():
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            price = float(price_data_point['4. close'])
            rows.append(TickerDatePrice(ticker, date, price))
        return sorted(rows, key=lambda x: x.date)


if __name__ == "__main__":
    AlphavantagePriceHistoryFetcher().run()
