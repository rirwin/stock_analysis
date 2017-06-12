import datetime
from constants import symbol_name_to_exchange



txn_history_csv_lines = txn_history_csv.split('\n')
orders = []
for line in txn_history_csv_lines:
    attrs = line.split(',')
    date = datetime.datetime.strptime(attrs[0], "%m/%d/%y").date()
    symbol_name = attrs[3]
    num_shares = int(attrs[4])
    share_price = float(attrs[6])
    orders.append(
        Order(
            Symbol(symbol_name_to_exchange[symbol_name], symbol_name),
            date,
            num_shares,
            share_price
        )
    )
