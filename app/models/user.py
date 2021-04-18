from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.database import base


class User(base):
    __tablename__ = 'users'

    login = Column(String, primary_key=True)
    password = Column(String)
    bots = relationship('Bot')
