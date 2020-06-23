import datetime
from stock_analysis.logic import order_history
from stock_analysis.logic import price_history


order_logic = order_history.OrderHistoryLogic()
price_logic = price_history.PriceHistoryLogic()


orders = [
    order_history.Order(*o) for o in
    [
        [1, 'B', 'FB', '2020-05-26', 53, 232.1],
        [1, 'B', 'NFLX', '2020-05-26', 19, 414.1],
        [1, 'B', 'NVDA', '2020-05-26', 20, 340.7962],
    ]
]


prices = [
    price_history.TickerDatePrice(
        ticker=p[1],
        date=datetime.datetime.strptime(p[0], '%Y-%m-%d').date(),
        price=p[2],
    ) for p in
    [
        ('2020-05-26', 'FB', 232.2,),
        ('2020-05-27', 'FB', 229.1,),
        ('2020-05-26', 'NFLX', 414.7,),
        ('2020-05-27', 'NFLX', 419.9,),
        ('2020-05-26', 'NVDA', 348.7,),
        ('2020-05-27', 'NVDA', 341.0,),
        ('2020-05-26', 'QQQ', 229.0,),
        ('2020-05-27', 'QQQ', 230.3,),
        ('2020-05-26', 'SPY', 299.1,),
        ('2020-05-27', 'SPY', 303.5,),
        ('2020-05-26', 'DIA', '250.2',),
        ('2020-05-27', 'DIA', 255.7,),
    ]
]

order_logic.add_orders(orders)
price_logic.add_prices(prices)
