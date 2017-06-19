import datetime
import mock
import pytest
import pytz
from batch.google_price_history_fetcher import GooglePriceHistoryFetcher
from batch.google_price_history_fetcher import DatePrice
from stock_analysis.logic.order_history import TickerDate
from stock_analysis.logic.price_history import TickerDatePrice


class TestGooglePriceHistoryFetcher(object):

    def test_parse_historical_data(self):
        batch = GooglePriceHistoryFetcher()
        content = 'Header Line\n2-Jun-17,1,1,1,1,27770715\n3-Jun-17,2,2,2,2,27770715'.encode()
        price_history = batch._parse_historical(content)
        assert price_history == [
            DatePrice(date=datetime.date(2017, 6, 2), price=1.0),
            DatePrice(date=datetime.date(2017, 6, 3), price=2.0),
        ]

    @pytest.mark.parametrize(
        'fetch_date,now,should_fetch', [
            (datetime.date(2017, 6, 16), datetime.datetime(2017, 6, 18), False),
            (datetime.date(2017, 6, 16), datetime.datetime(2017, 6, 19, 15, tzinfo=pytz.timezone('US/Eastern')), False),
            (datetime.date(2017, 6, 16), datetime.datetime(2017, 6, 19, 17, tzinfo=pytz.timezone('US/Eastern')), True),
            (datetime.date(2017, 6, 12), datetime.datetime(2017, 6, 13, 15, tzinfo=pytz.timezone('US/Eastern')), False),
            (datetime.date(2017, 6, 12), datetime.datetime(2017, 6, 13, 17, tzinfo=pytz.timezone('US/Eastern')), True),

        ]
    )
    def test_should_fetch_data_for_date(self, fetch_date, now, should_fetch):
        batch = GooglePriceHistoryFetcher()
        with mock.patch('batch.google_price_history_fetcher.datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = now
            assert batch.should_fetch_data_for_date(fetch_date) is should_fetch

    def test_fetch_ticker_history(self):
        batch = GooglePriceHistoryFetcher()
        ticker_date = TickerDate('YELP', datetime.date(2017, 6, 12))
        date_price = DatePrice(datetime.date(2017, 6, 12), 31.2)
        with mock.patch(
            'batch.google_price_history_fetcher.time'
        ), mock.patch(
            'batch.google_price_history_fetcher.requests'
        ) as mock_requests, mock.patch.object(
            batch,
            '_parse_historical',
            return_value=[date_price]
        ) as mock_parse:
                mock_requests.get = mock.Mock()
                data = batch.fetch_ticker_history(ticker_date)

                assert mock_requests.get.called
                assert mock_parse.called
                assert data == [
                    TickerDatePrice(ticker_date.ticker, date_price.date, date_price.price)
                ]

    @pytest.mark.parametrize(
        'ticker_date,min_date_history_exists,max_history_date,result', [
            (
                TickerDate('AAPL', datetime.date(2017, 6, 16)),
                False,
                None,
                datetime.date(2017, 6, 16)
            ),
            (
                TickerDate('AAPL', datetime.date(2017, 6, 16)),
                True,
                datetime.date(2017, 6, 26),
                datetime.date(2017, 6, 27)
            ),
        ]
    )
    def test_get_fetch_date(self, ticker_date, min_date_history_exists, max_history_date, result):
        batch = GooglePriceHistoryFetcher()
        with mock.patch.object(
            batch.price_logic,
            'does_ticker_date_history_exists',
            return_value=min_date_history_exists
        ), mock.patch.object(
            batch.price_logic,
            'get_max_date_history_for_ticker',
            return_value=max_history_date
        ):
            assert batch.get_fetch_date(ticker_date) == result

    def test_run(self):
        batch = GooglePriceHistoryFetcher()
        ticker_date = TickerDate('AAPL', datetime.date(2017, 6, 19))

        with mock.patch.object(
            batch.order_logic,
            'get_all_order_tickers_min_date',
            return_value=[ticker_date]
        ), mock.patch.object(
            batch,
            'process_ticker_order_date'
        ) as patch_process:

            batch.run()
            assert patch_process.call_args_list == [mock.call(ticker_date)]

    def test_process_ticker_order_date(self):
        batch = GooglePriceHistoryFetcher()
        ticker_date = TickerDate('AAPL', datetime.date(2017, 6, 19))
        mock_history = mock.Mock()
        with mock.patch.object(
            batch,
            'get_fetch_date',
            return_value=ticker_date.date
        ), mock.patch.object(
            batch,
            'should_fetch_data_for_date',
            return_value=True
        ), mock.patch.object(
            batch,
            'fetch_ticker_history',
            return_value=mock_history
        ), mock.patch.object(
            batch.price_logic,
            'add_prices'
        ) as mock_price_logic:

            batch.process_ticker_order_date(ticker_date)
            assert mock_price_logic.call_args_list == [mock.call(mock_history)]
