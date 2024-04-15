import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=False, unique=True,
                           index=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    menu = sqlalchemy.Column(sqlalchemy.String, default='main')
    rate = sqlalchemy.Column(sqlalchemy.String,
                             index=True, default=0)
    admin = sqlalchemy.Column(sqlalchemy.String, default=0)