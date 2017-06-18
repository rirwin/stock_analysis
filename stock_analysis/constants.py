USER_ID = 1

ticker_name_to_exchange = {}
nasdaq_tickers = [
    'AAPL', 'ADBE', 'ALGN', 'AMZN', 'ATVI', 'BIDU', 'BLUE', 'BOFI',
    'CELG', 'CGNX', 'COST', 'FB', 'FEYE', 'GOOG', 'HAIN',
    'HAS', 'ILMN', 'ISRG', 'JBLU', 'MAR', 'MASI', 'MELI',
    'MIDD', 'MOMO', 'NFLX', 'NVDA', 'OLED', 'PYPL', 'SBUX',
    'SPLK', 'SSNC', 'SWKS', 'TSLA', 'TTD', 'UBNT', 'ULTA',
    'Z',
]
nyse_tickers = [
    'AMT',
    'BUD', 'CMG', 'DIS', 'EBS', 'FDS', 'ICE', 'IJR', 'KMI', 'KMX',
    'MA', 'MKL', 'NKE', 'NYT', 'SHOP', 'SKX', 'TWLO', 'VEA', 'VEEV',
    'WDAY', 'ZOES',
]
for s in nasdaq_tickers:
    ticker_name_to_exchange[s] = 'NASDAQ'

for s in nyse_tickers:
    ticker_name_to_exchange[s] = 'NYSE'
