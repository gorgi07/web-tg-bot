import sqlalchemy
from .db_session import SqlAlchemyBase


class Friend(SqlAlchemyBase):
    __tablename__ = 'friends'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=False, unique=True,
                           index=True)
    friends = sqlalchemy.Column(sqlalchemy.String, default="")
    friends_input = sqlalchemy.Column(sqlalchemy.String, default="")
    friends_output = sqlalchemy.Column(sqlalchemy.String, default="")
