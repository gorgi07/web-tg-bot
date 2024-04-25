import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=False, unique=True,
                           index=True)
    name = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    rate = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    def full_information(self):
        return [self.id, self.name, self.rate]
