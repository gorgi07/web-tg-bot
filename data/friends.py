import sqlalchemy
from .db_session import SqlAlchemyBase


class Friend(SqlAlchemyBase):
    __tablename__ = 'friends'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=False, unique=True,
                           index=True)
    name = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    friends = sqlalchemy.Column(sqlalchemy.String, default="None")
    friends_input = sqlalchemy.Column(sqlalchemy.String, default="None")
    friends_output = sqlalchemy.Column(sqlalchemy.String, default="None")

    def full_information(self):
        return [self.id, self.name, self.friends, self.friends_input, self.friends_output]
