import datetime
import mock
import pytest
import pytz
from batch.advantagealpha_price_history_fetcher import AlphavantagePriceHistoryFetcher
from stock_analysis.logic.order_history import TickerDate
from stock_analysis.logic.price_history import TickerDatePrice
from stock_analysis import constants


class TestAlphavantagePriceHistoryFetcher(object):

    def test_parse_historical_data(self):
        batch = AlphavantagePriceHistoryFetcher()
        content = '{ "Meta Data": {  "2. Symbol": "MOMO"},"Time Series (Daily)": {' + \
            '"2017-12-20": { "4. close": "1.0" }, ' + \
            '"2017-12-19": { "4. close": "2.0" }}}'
        content = content.encode()
        price_history = batch._parse_historical(content)
        assert price_history == [
            TickerDatePrice(ticker='MOMO', date=datetime.date(2017, 12, 19), price=2.0),
            TickerDatePrice(ticker='MOMO', date=datetime.date(2017, 12, 20), price=1.0),
        ]

    @pytest.mark.parametrize(
        'fetch_date,now,should_fetch', [
            # Have data for Thursday but not Friday and it's Sunday
            (datetime.date(2017, 6, 16), datetime.datetime(2017, 6, 18), True),
            # Have data for Friday and it's Sunday
            (datetime.date(2017, 6, 17), datetime.datetime(2017, 6, 18), False),
            # Have data for Friday and it's Monday before close
            (datetime.date(2017, 6, 17), datetime.datetime(2017, 6, 19, 15, tzinfo=pytz.timezone('US/Eastern')), False),
            # Have data for Friday and it's Monday after close
            (datetime.date(2017, 6, 17), datetime.datetime(2017, 6, 19, 17, tzinfo=pytz.timezone('US/Eastern')), True),
            # Have data for day before and it's before close
            (datetime.date(2017, 6, 13), datetime.datetime(2017, 6, 13, 15, tzinfo=pytz.timezone('US/Eastern')), False),
            # Have data for day before and it's after close
            (datetime.date(2017, 6, 13), datetime.datetime(2017, 6, 13, 17, tzinfo=pytz.timezone('US/Eastern')), True),

        ]
    )
    def test_should_fetch_data_for_date(self, fetch_date, now, should_fetch):
        batch = AlphavantagePriceHistoryFetcher()
        with mock.patch(
            'batch.advantagealpha_price_history_fetcher.datetime.datetime'
        ) as mock_datetime:
            mock_datetime.now.return_value = now
            assert batch.should_fetch_data_for_date(fetch_date) is should_fetch

    def test_fetch_ticker_history(self):
        batch = AlphavantagePriceHistoryFetcher()
        ticker_date = TickerDate('YELP', datetime.date(2017, 6, 12))
        ticker_date_price = TickerDatePrice('YELP', datetime.date(2017, 6, 12), 31.2)
        with mock.patch(
            'batch.advantagealpha_price_history_fetcher.time'
        ), mock.patch(
            'batch.advantagealpha_price_history_fetcher.requests'
        ) as mock_requests, mock.patch.object(
            batch,
            '_parse_historical',
            return_value=[ticker_date_price]
        ) as mock_parse:
                mock_requests.get = mock.Mock()
                data = batch.fetch_ticker_history(ticker_date)

                assert mock_requests.get.called
                assert mock_parse.called
                assert data == [ticker_date_price]

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
        batch = AlphavantagePriceHistoryFetcher()
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
        batch = AlphavantagePriceHistoryFetcher()
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
            benchmark_ticker_dates = [TickerDate(t, ticker_date.date) for t in constants.BENCHMARK_TICKERS]
            assert patch_process.call_args_list == [mock.call(ticker_date)] + \
                [mock.call(td) for td in benchmark_ticker_dates]

    def test_process_ticker_order_date(self):
        batch = AlphavantagePriceHistoryFetcher()
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
