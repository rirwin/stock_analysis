import datetime
import requests
import pickle
from collections import namedtuple
from collections import defaultdict
import os.path
import time


URL_TEMPLATE = 'http://www.google.com/finance/historical?q={exchange}:{symbol}&startdate={month}+{day}%2C+{year}&output=csv'
WEB_CACHE = 'web_cache.pickle'

Order = namedtuple('Order', ['symbol', 'date', 'num_shares', 'price'])
Symbol = namedtuple('Symbol', ['exchange', 'name'])
SymbolDate = namedtuple('SymbolDate', ['symbol', 'date'])
StockPriceDate = namedtuple('StockPriceDate', ['price', 'date'])

benchmark_symbols = [
    Symbol('NYSEARCA', 'SPY'),
    Symbol('NYSEARCA', 'IWM')
]

class StockOwnershipHistory(object):

    def __init__(self, orders):
        self.orders = orders
        symbols = set(order.symbol for order in self.orders)
        symbols = [s for s in symbols]
        self.symbols = sorted(symbols, key=lambda x: x.name)

        self.symbol_shares_map = defaultdict(int)
        for order in orders:
            self.symbol_shares_map[order.symbol] += order.num_shares

        min_date_all_orders = datetime.date.today()
        for order in orders:
            if order.date < min_date_all_orders:
                min_date_all_orders = order.date

        self.portfolio_start_date = min_date_all_orders
        self.benchmark_symbols = benchmark_symbols


    def _load_cache(self):
        if not os.path.isfile(WEB_CACHE):
            with open(WEB_CACHE, 'wb') as handle:
                pickle.dump({}, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(WEB_CACHE, 'rb') as handle:
            self._web_cache = pickle.load(handle)

    def _save_cache(self):
        with open(WEB_CACHE, 'wb') as handle:
            pickle.dump(self._web_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load_history_all_orders(self):
        self._load_cache()
        symbol_dates = self._get_symbols_min_date_from_orders()
        self.ownership_history = {}
        self.benchmark_history = {}

        for symbol_date in symbol_dates:
            self.ownership_history[symbol_date.symbol] = self.get_history(symbol_date)

        for benchmark_symbol in self.benchmark_symbols:
            self.benchmark_history[benchmark_symbol] = self.get_history(
                SymbolDate(benchmark_symbol, self.portfolio_start_date)
            )

        self._save_cache()

    def get_history(self, symbol_date):
        url = self._form_url(symbol_date)
        content = self._web_cache.get(url)
        if content is None:
            response = requests.get(url)
            time.sleep(1)  # Sleep to throttle hitting api
            content = response.content
            self._web_cache[url] = content
        return self._parse_historical(content)

    def _form_url(self, symbol_date):
        '''http://www.google.com/finance/historical?q=NASDAQ:AAPL&startdate=May+24%2C+2017&output=csv'''
        return URL_TEMPLATE.format(
            exchange=symbol_date.symbol.exchange,
            symbol=symbol_date.symbol.name,
            month=symbol_date.date.strftime('%B'),
            day=symbol_date.date.day,
            year=symbol_date.date.year
        )

    def _get_symbols_min_date_from_orders(self):
        symbol_to_date = {}
        for order in self.orders:
            if order.symbol not in symbol_to_date:
                symbol_to_date[order.symbol] = order.date
            elif order.date < symbol_to_date[order.symbol]:
                symbol_to_date[order.symbol] = order.date

        symbol_dates = [SymbolDate(k, v) for k, v in symbol_to_date.items()]
        return sorted(symbol_dates, key=lambda x: x.date)

    def _parse_historical(self, content):
        lines = content.decode().strip().split('\n')
        rows = []
        for line in lines[1:]:  # Skip the header row
            rows.append(self._parse_line(line))
        return sorted(rows, key=lambda x: x.date)

    def _parse_line(self, line):
        '''Parse line in format 2-Jun-17,153.58,155.45,152.89,155.45,27770715
        The second to last field is the closing price.
        '''
        fields = line.split(',')
        date = self._parse_date(fields[0])
        close = float(fields[-2])
        return StockPriceDate(close, date)

    def _parse_date(self, date_str):
        '''Parse date in format 26-May-17'''
        return datetime.datetime.strptime(date_str, "%d-%b-%y").date()

    def print_portfolio(self):
        for symbol in self.symbols:

            print(
                "{}  -  {}".format(
                    symbol.name,
                    "${:,.0f}".format(self.calculate_symbol_ownership_value(symbol)).rjust(10, ' '),
                )
            )

    def calculate_symbol_ownership_value(self, symbol):
        last_close = self.ownership_history[symbol][-1]
        return last_close.price * self.symbol_shares_map[symbol]

    def calculate_symbol_ownership_percent_gain(self, symbol):
        last_close = self.ownership_history[symbol][-1]
        #return last_close.price * self.symbol_shares_map[symbol] / self.ownership_history[]

    def calculate_gain_from_history(self, prices):
        start_price = prices[0].price
        start_date = prices[0].date
        end_price = prices[-1].price
        end_date = prices[-1].date
        gain_percent = 100 * float(end_price - start_price) / start_price
        num_days = (end_date - start_date).days
        return gain_percent, num_days
