import argparse
import datetime
import mock

from stock_analysis.batch.etrade_csv_ingestor import EtradeIngestor
from stock_analysis.logic import order

USER_ID = 1


class TestEtradeCsvIngestor(object):

    def test_init(self):
        batch = EtradeIngestor()
        args = batch.arg_parser.parse_args(['--csv-path', './path/to/data.csv'])
        assert args == argparse.Namespace(csv_path='./path/to/data.csv')
        assert type(batch.order_logic) == order.OrderHistoryLogic

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
            assert patch_add_orders.call_args_list == [mock.call(USER_ID, mock_parsed_orders)]

    def test_parse_orders_from_csv_reader(self):
        batch = EtradeIngestor()

        # the reader is reader in a loop (i.e., for row in reader:)
        reader = [
            '06/12/17,Bought,EQ,NFLX,19,-2924.87,153.6799,4.95,NETFLIX COM INC'.split(','),
            '06/08/17,Bought,EQ,NFLX,39,-2924.46,151.9,4.95,NETFLIX COM INC'.split(','),
        ]
        orders = batch.parse_orders_from_csv_reader(reader)
        assert set(orders) == set([
            order.Order('NFLX', datetime.datetime(2017, 6, 12).date(), 19, 153.6799),
            order.Order('NFLX', datetime.datetime(2017, 6, 8).date(), 39, 151.9),
        ])
        print(orders)
