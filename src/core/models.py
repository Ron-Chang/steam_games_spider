from sqlalchemy import func, text
from sqlalchemy.schema import UniqueConstraint
from app import db

# ====================== exsample ====================== #
"""
class TableName(db.Model):
    __bind_key__ = 'database_name'
    __tablename__ = 'table_name'

    __table_args__ = (
        UniqueConstraint("column_a", "column_b", name='unique_component_commit'),
    )  # unique compose key

    id = db.Column(db.Integer, primary_key=True)
    column_a = db.Column(db.String(10), nullable=False)
    column_b = db.Column(db.String(120))
    update_datetime = db.Column(db.DateTime)
    create_datetime = db.Column(db.DateTime, server_default=func.now())
"""

class SteamGameInfo(db.Model):
    __bind_key__ = 'spider'
    __tablename__ = 'steam_game_info'

    id = db.Column(db.Integer, primary_key=True)
    steam_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(120))

    discount = db.Column(db.Float)
    normal_price = db.Column(db.Integer)
    released_date = db.Column(db.DateTime)

    overall_reviews = db.Column(db.String(30))
    rate_of_positive = db.Column(db.Float)
    amount_of_reviews = db.Column(db.Integer)

    is_bundle = db.Column(db.Boolean)
    is_support_win = db.Column(db.Boolean)
    is_support_mac = db.Column(db.Boolean)
    is_support_linux = db.Column(db.Boolean)

    update_datetime = db.Column(db.DateTime)
    create_datetime = db.Column(db.DateTime, server_default=func.now())
