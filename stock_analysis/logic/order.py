from sqlalchemy.orm import sessionmaker
from database.order_history import OrderHistory
from database import db


Session = sessionmaker(bind=db.engine)


class OrderHistoryLogic(object):

    def add_orders(self, user_id, orders):
        session = Session()
        for order in orders:
            session.add(
                OrderHistory(
                    user_id=user_id,
                    date=order.date,
                    ticker=order.ticker,
                    num_shares=order.num_shares,
                    price=order.price,
                )
            )
        session.commit()

