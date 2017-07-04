import argparse
import datetime
import mock
import pytest

from batch.etrade_csv_ingestor import EtradeIngestor
from batch.etrade_csv_ingestor import RowParserException
from stock_analysis.logic import order_history


class TestEtradeCsvIngestor(object):

    def test_init(self):
        batch = EtradeIngestor()
        args = batch.arg_parser.parse_args(['--csv-path', './path/to/data.csv'])
        assert args == argparse.Namespace(csv_path='./path/to/data.csv')
        assert type(batch.order_logic) == order_history.OrderHistoryLogic

    def test_run(self):
        batch = EtradeIngestor()
        csv_path = './path/to/data.csv'
        mock_args = mock.Mock()
        mock_args.csv_path = csv_path
        mock_parsed_orders = mock.Mock()
        with \
                mock.patch.object(
                    batch.arg_parser, 'parse_args', return_value=mock_args
                ) as patch_parse_args, \
                mock.patch.object(
                    batch, 'parse_orders_from_csv', return_value=mock_parsed_orders
                ) as patch_parse_orders, \
                mock.patch.object(batch.order_logic, 'add_orders') as patch_add_orders:

            batch.run()
            assert patch_parse_args.called
            assert patch_parse_orders.call_args_list == [mock.call(csv_path)]
            assert patch_add_orders.call_args_list == [mock.call(mock_parsed_orders)]

    def test_parse_orders_from_csv(self):
        csv_path = '/path/to/csv'
        mock_reader = mock.Mock()
        mock_orders = mock.Mock()
        batch = EtradeIngestor()
        with \
                mock.patch('builtins.open') as patch_open,\
                mock.patch('csv.reader', return_value=mock_reader) as patch_reader,\
                mock.patch.object(
                    batch, 'parse_orders_from_csv_reader', return_value=mock_orders
                ) as patch_parse_orders:

            orders = batch.parse_orders_from_csv(csv_path)
            assert patch_open.call_args_list == [mock.call(csv_path)]
            assert patch_reader.called
            assert patch_parse_orders.call_args_list == [mock.call(mock_reader)]
            assert orders == mock_orders

    def test_parse_orders_from_csv_reader(self):
        batch = EtradeIngestor()

        # the reader is reader in a loop (i.e., for row in reader:)
        reader = [
            '06/12/17,Bought,EQ,NFLX,19,-2924.87,153.6799,4.95,NETFLIX COM INC'.split(','),
            '06/08/17,Bought,EQ,NFLX,39,-2924.46,151.9,4.95,NETFLIX COM INC'.split(','),
        ]
        orders = batch.parse_orders_from_csv_reader(reader)
        assert set(orders) == set([
            order_history.Order(
                batch.user_id,
                order_history.BUY_ORDER_TYPE,
                'NFLX',
                datetime.datetime(2017, 6, 12).date(),
                19,
                153.6799
            ),
            order_history.Order(
                batch.user_id,
                order_history.BUY_ORDER_TYPE,
                'NFLX',
                datetime.datetime(2017, 6, 8).date(),
                39, 151.9
            ),
        ])

    def test_extract_order_from_row_skips_malformed_row(self):
        batch = EtradeIngestor()
        row = 'MALFORMED_DATE,Bought,EQ,NFLX,39,-2924.46,151.9,4.95,NETFLIX COM INC'.split(',')

        with pytest.raises(RowParserException):
            batch.extract_order_from_row(row)

    def test_extract_order_from_row_ignores_non_bought_txn_type(self):
        batch = EtradeIngestor()
        row = '06/12/17,UKNOWN_TXN_TYPE,EQ,NFLX,39,-2924.46,151.9,4.95,NETFLIX COM INC'.split(',')

        order = batch.extract_order_from_row(row)
        assert order is None

    def test_parse_orders_from_csv_reader_skips_malformed_lines(self):
        batch = EtradeIngestor()

        # the reader is reader in a loop (i.e., for row in reader:)
        reader = [
            '06/12/17,Bought,EQ,NFLX,19,-2924.87,153.6799,4.95,NETFLIX COM INC'.split(','),
            '06/08/17,Bought,EQ,NFLX,39,-2924.46,151.9,4.95,NETFLIX COM INC'.split(','),
            'MALFORMED_DATE,Bought,EQ,NFLX,39,-2924.46,151.9,4.95,NETFLIX COM INC'.split(','),
        ]
        orders = batch.parse_orders_from_csv_reader(reader)
        assert set(orders) == set([
            order_history.Order(
                batch.user_id,
                order_history.BUY_ORDER_TYPE,
                'NFLX',
                datetime.datetime(2017, 6, 12).date(),
                19,
                153.6799
            ),
            order_history.Order(
                batch.user_id,
                order_history.BUY_ORDER_TYPE,
                'NFLX',
                datetime.datetime(2017, 6, 8).date(),
                39, 151.9
            ),
        ])
