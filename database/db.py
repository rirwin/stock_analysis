import os
from sqlalchemy import create_engine

if os.environ.get('USE_TEST_DB') is not None:
    engine = create_engine('sqlite://')
else:
    engine = create_engine('sqlite:///database/stock_history.sqlite3db')
