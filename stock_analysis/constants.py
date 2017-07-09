USER_ID = 1

ticker_name_to_exchange = {}
nasdaq_tickers = [
    'AAPL', 'ADBE', 'ALGN', 'AMZN', 'ATVI', 'BIDU', 'BLUE', 'BOFI',
    'CELG', 'CGNX', 'COST', 'EXEL', 'FB', 'FEYE', 'GOOG', 'HAIN',
    'HAS', 'ILMN', 'ISRG', 'JBLU', 'MAR', 'MASI', 'MELI',
    'MIDD', 'MOMO', 'NFLX', 'NVDA', 'OLED', 'PYPL', 'QQQ', 'SBUX',
    'SPLK', 'SSNC', 'STMP', 'SWKS', 'TSLA', 'TTD', 'UBNT', 'ULTA',
    'YELP', 'Z',
]
nyse_tickers = [
    'AMT',  # TODO this might be working again in the API
    'BUD', 'CMG', 'DIA', 'DIS', 'EBS', 'FDS', 'ELLI', 'ICE', 'IJR', 'KMI', 'KMX',
    'MA', 'MKL', 'NKE', 'NYT', 'PAYC', 'SHOP', 'SKX', 'SPY', 'TWLO', 'TXT',
    'VEA', 'VEEV', 'WDAY', 'ZOES',
]
for s in nasdaq_tickers:
    ticker_name_to_exchange[s] = 'NASDAQ'

for s in nyse_tickers:
    ticker_name_to_exchange[s] = 'NYSE'

BENCHMARK_TICKERS = ['SPY', 'QQQ', 'DIA']
