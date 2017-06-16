symbol_name_to_exchange = {}
nasdaq_symbols = [
    'AAPL', 'ADBE', 'ALGN', 'AMZN', 'ATVI', 'BIDU', 'BLUE', 'BOFI',
    'CELG', 'CGNX', 'COST', 'FB', 'FEYE', 'GOOG', 'HAIN',
    'HAS', 'ILMN', 'ISRG', 'JBLU', 'MAR', 'MASI', 'MELI',
    'MIDD', 'MOMO', 'NFLX', 'NVDA', 'OLED', 'PYPL', 'SBUX',
    'SPLK', 'SSNC', 'SWKS', 'TSLA', 'TTD', 'UBNT', 'ULTA',
    'Z',
]
nyse_symbols = [
    'AMT',
    'BUD', 'CMG', 'DIS', 'EBS', 'FDS', 'ICE', 'KMI', 'KMX',
    'MA', 'MKL', 'NKE', 'NYT', 'SHOP', 'SKX', 'TWLO', 'VEEV',
    'WDAY', 'ZOES',
]
for s in nasdaq_symbols:
    symbol_name_to_exchange[s] = 'NASDAQ'

for s in nyse_symbols:
    symbol_name_to_exchange[s] = 'NYSE'
