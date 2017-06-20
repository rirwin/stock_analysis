from sqlalchemy.orm import sessionmaker
from database import db
from database.price_history import PriceHistory
from database.order_history import OrderHistory
from stock_analysis.logic.price_history import PriceHistoryLogic


Session = sessionmaker(bind=db.engine)
price_logic = PriceHistoryLogic()


class PortfolioLogic(object):

    def get_percent_gain(self, user_id, ticker):
        session = Session()
        result = session.query(OrderHistory.price, OrderHistory.num_shares)\
            .filter_by(ticker=ticker)\
            .filter_by(user_id=user_id)\
            .all()
        initial_value = sum(x.price * x.num_shares for x in result)
        num_shares = sum(x.num_shares for x in result)

        max_date = price_logic.get_max_date_history_for_ticker(ticker)
        result = session.query(PriceHistory.price)\
            .filter_by(ticker=ticker)\
            .filter_by(date=max_date.isoformat())\
            .first()
        final_price = result[0]
        final_value = final_price * num_shares
        return 100 * (final_value - initial_value) / initial_value

    def get_stock_value(self, user_id, ticker):
        session = Session()
        result = session.query(OrderHistory.price, OrderHistory.num_shares)\
            .filter_by(ticker=ticker)\
            .filter_by(user_id=user_id)\
            .all()
        num_shares = sum(x.num_shares for x in result)

        max_date = price_logic.get_max_date_history_for_ticker(ticker)
        result = session.query(PriceHistory.price)\
            .filter_by(ticker=ticker)\
            .filter_by(date=max_date.isoformat())\
            .first()
        final_price = result[0]
        return final_price * num_shares
