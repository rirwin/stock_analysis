from sqlalchemy.orm import sessionmaker
from database import db
from database.price_history import PriceHistory
from database.order_history import OrderHistory
from stock_analysis.logic.price_history import PriceHistoryLogic


Session = sessionmaker(bind=db.engine)
price_logic = PriceHistoryLogic()


class GainHistoryLogic(object):

    def get_percent_gain(self, user_id, ticker):
        session = Session()
        result = session.query(OrderHistory.price)\
            .filter_by(ticker=ticker)\
            .filter_by(user_id=user_id)\
            .first()  # TODO change this for multiple order gains
        order_price = result[0]

        max_date = price_logic.get_max_date_history_for_ticker(ticker)
        result = session.query(PriceHistory.price)\
            .filter_by(ticker=ticker)\
            .filter_by(date=max_date.isoformat())\
            .first()
        current_price = result[0]

        return 100 * (current_price - order_price) / order_price
