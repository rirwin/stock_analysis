from collections import defaultdict
from collections import namedtuple
import datetime
import itertools
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from database.price_history import PriceHistory
from database import db
from stock_analysis.logic.order_history import TickerDate


TickerDatePrice = namedtuple('TickerDatePrice', ['ticker', 'date', 'price'])
Session = sessionmaker(bind=db.engine)


class PriceHistoryLogic(object):

    def add_prices(self, ticker_date_prices):
        session = Session()
        for ticker_date_price in ticker_date_prices:
            session.add(
                PriceHistory(
                    date=ticker_date_price.date.isoformat(),
                    ticker=ticker_date_price.ticker,
                    price=ticker_date_price.price,
                )
            )
        session.commit()

    def get_max_date_history_for_ticker(self, ticker):
        session = Session()
        date_str = session.query(func.max(PriceHistory.date))\
            .filter_by(ticker=ticker)\
            .first()
        date = self._make_date_from_isoformatted_string(date_str[0])
        session.close()
        return date

    def does_ticker_date_history_exists(self, ticker_date):
        session = Session()
        exists = session.query(PriceHistory.ticker)\
            .filter_by(ticker=ticker_date.ticker)\
            .filter_by(date=ticker_date.date)\
            .first()
        session.close()
        return bool(exists)

    def get_ticker_price_history_map(self, tickers, dates):
        ticker_dates = [TickerDate(x[0], x[1]) for x in itertools.product(tickers, dates)]
        prices = self.get_ticker_dates_prices(ticker_dates)
        price_info = defaultdict(dict)
        for price in prices:
            price_info[price.ticker][price.date] = price.price
        return price_info

    def get_ticker_dates_prices(self, ticker_dates):
        tickers = [td.ticker for td in ticker_dates]
        dates = [td.date for td in ticker_dates]
        session = Session()
        results = session.query(PriceHistory.ticker, PriceHistory.date, PriceHistory.price)\
            .filter(PriceHistory.ticker.in_(tickers))\
            .filter(PriceHistory.date.in_(dates))\
            .all()
        session.close()
        ticker_date_prices = [
            TickerDatePrice(
                ticker=result[0],
                date=self._make_date_from_isoformatted_string(result[1]),
                price=float(result[2])
            )
            for result in results
            if result
        ]
        return ticker_date_prices

    def get_tickers_gains(self, tickers, date_range):
        session = Session()
        results = session.query(PriceHistory.ticker, PriceHistory.price)\
            .filter(PriceHistory.ticker.in_(tickers))\
            .filter(PriceHistory.date.in_(date_range))\
            .order_by(PriceHistory.ticker, PriceHistory.date)\
            .all()
        session.close()

        assert len(tickers) * 2 == len(results)
        idx = 0
        gains = []
        while idx < len(results):
            begin_price = results[idx][1]
            end_price = results[idx + 1][1]
            gain = 100 * (end_price - begin_price) / begin_price
            gains.append((results[idx][0], gain,))
            idx += 2
        return gains

    def get_dates_last_two_sessions(self):
        session = Session()
        results = session.query(PriceHistory.date)\
            .group_by(PriceHistory.date)\
            .order_by(desc(PriceHistory.date))\
            .limit(2)\
            .all()
        session.close()
        assert len(results) == 2
        last_session_date = self._make_date_from_isoformatted_string(results[0][0])
        the_day_before = self._make_date_from_isoformatted_string(results[1][0])
        return (last_session_date, the_day_before)

    def get_benchmark_history_dates(self):
        session = Session()
        results = session.query(PriceHistory.date)\
            .group_by(PriceHistory.date)\
            .order_by(desc(PriceHistory.date))\
            .limit(260)\
            .all()  # 52 weeks * 5 = 260
        session.close()

        all_dates = [self._make_date_from_isoformatted_string(result[0]) for result in results]

        return [self._get_date_match_in_data(all_dates[0], days_back, all_dates) for days_back in (0, 1, 7, 30, 90, 365)]

    def _get_date_match_in_data(self, most_recent_date, days_back_target, all_dates):
        for days_back in range(3):  # Never more than a 3 day break
            if most_recent_date - datetime.timedelta(days=days_back_target) - datetime.timedelta(days_back) in all_dates:
                return most_recent_date - datetime.timedelta(days=days_back_target) - datetime.timedelta(days_back)

    def _make_date_from_isoformatted_string(self, date_str):
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
