import sqlalchemy
from .db_session import SqlAlchemyBase


class Admin(SqlAlchemyBase):
    __tablename__ = 'admins'

    hash_id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=False, unique=True,
                           index=True)
