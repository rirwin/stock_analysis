from stock_analysis.logic import order_history


order_logic = order_history.OrderHistoryLogic()


orders = [
    order_history.Order(*o) for o in
    [
        [1,'B','2017-06-21','EXEL',164,24.272],
        [1,'B','2017-06-21','STMP',34,147.085],
        [1,'B','2017-06-21','PAYC',71,70.81],
        [1,'B','2017-06-21','TXT',106,47.0],
        [1,'B','2017-06-16','FB',53,149.7],
        [1,'B','2017-06-15','STMP',24,144.811],
        [1,'B','2017-06-15','MIDD',26,131.0019],
        [1,'B','2017-06-15','ELLI',27,109.45],
        [1,'B','2017-06-12','NFLX',19,153.6799],
        [1,'B','2017-06-09','NVDA',20,150.7962],
    ]
]

order_logic.add_orders(orders)
