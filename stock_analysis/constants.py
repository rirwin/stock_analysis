USER_ID = 1

ticker_name_to_exchange = {}
nasdaq_tickers = [
    'AAPL', 'ADBE', 'ALGN', 'AMZN', 'ATVI', 'BIDU', 'BLUE', 'BOFI',
    'CELG', 'CGNX', 'COST', 'EXEL', 'FB', 'FEYE', 'GOOG', 'HAIN',
    'HAS', 'ILMN', 'IONS', 'ISRG', 'JBLU', 'MAR', 'MASI', 'MELI',
    'MIDD', 'MOMO', 'NFLX', 'NVDA', 'OLED', 'PYPL', 'QQQ', 'SBUX',
    'SPLK', 'SSNC', 'STMP', 'SWKS', 'TRVG', 'TSLA', 'TTD', 'UBNT', 'ULTA',
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
# Google's API doesn't allow downloading :S, switch to yahoo?
# https://query1.finance.yahoo.com/v7/finance/download/%5EIXIC?period1=1499151600&period2=1499583630&
# interval=1d&events=history&crumb=lQ0e2bklb6h
# Needs cookie magic.  no api calls wanted  (blocker)
# %5E is ^
# periods are both GMT 7am  (I think it's a glitche in TZ conversion, SF is 7 hours behind)
# Date    Open    High    Low    Close    Adj Close    Volume
# 2017-06-12    6153.560059    6183.810059    6110.669922    6175.459961    6175.459961    2586540000
# BENCHMARK_TICKERS = ['INX', 'DJI', 'IXIC']
# ticker_name_to_exchange['.INX'] = 'INDEXSP'
# ticker_name_to_exchange['.DJI'] = 'INDEXDJX'
# ticker_name_to_exchange['.IXIC'] = 'INDEXNASDAQ'
