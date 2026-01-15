
class StockDetail:
    __table__ = "stock_detail"

    def __init__(self, symbol, date, open_price, high_price, low_price,
                 close_price, volume, change, market_cap, updated_at):
        self.symbol = symbol
        self.date = date
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.volume = volume
        self.change = change
        self.market_cap = market_cap
        self.updated_at = updated_at

    def __repr__(self):
        return (f"StockDetail(symbol={self.symbol}, date={self.date}, "
                f"open={self.open_price}, close={self.close_price}, "
                f"volume={self.volume})")


class StockInfo:
    __table__ = "stock"

    def __init__(self, symbol, company_name, exchange, industry, profile):
        self.symbol = symbol
        self.company_name = company_name
        self.exchange = exchange
        self.industry = industry
        self.profile = profile

    def __repr__(self):
        return (f"StockInfo(symbol={self.symbol}, "
                f"company_name={self.company_name}, exchange={self.exchange})")


import uuid

class News:
    __table__ = "news"

    def __init__(self, id=None, url_news=None, title=None, image_news=None, description=None, source=None, updated_at=None):
        self.id = id or uuid.uuid4()   
        self.url_news = url_news
        self.title = title
        self.image_news = image_news
        self.description = description
        self.source = source
        self.updated_at = updated_at

    def __repr__(self):
        return (f"News(id={self.id}, title={self.title}, url_news={self.url_news}, "
                f"updated_at={self.updated_at}, source={self.source})")


import uuid
from datetime import datetime

class Subscription:
    __table__ = "subscriptions"

    def __init__(self, user_email, id=None, amount=0, end_date=None, 
                 plan=None, start_date=None, status=None, transaction_id=None):
        self.user_email = user_email
        self.id = id or uuid.uuid4()
        self.amount = amount
        self.end_date = end_date or (datetime.now())
        self.plan = plan
        self.start_date = start_date or datetime.now()
        self.status = status
        self.transaction_id = transaction_id

    def __repr__(self):
        return (f"Subscription(user_email={self.user_email}, id={self.id}, amount={self.amount}, "
                f"plan={self.plan}, status={self.status}, transaction_id={self.transaction_id}, "
                f"start_date={self.start_date}, end_date={self.end_date})")


class Users:
    __table__ = "users"

    def __init__(self, email, password, role, user_token, name=None, created_at=None):
        self.email = email
        self.password = password
        self.role = role
        self.user_token = user_token
        self.name = name
        self.created_at = created_at  

    def __repr__(self):
        return f"Users(email={self.email}, role={self.role}, name={self.name})"

    import uuid

class Watchlist:
    __table__ = "watchlist"

    def __init__(self, email=None, symbol=None):
        self.email = email
        self.symbol = symbol

    def __repr__(self):
        return f"Watchlist(email={self.email}, symbol={self.symbol})"
