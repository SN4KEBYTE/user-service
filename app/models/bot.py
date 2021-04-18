from sqlalchemy import Column, String, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.database import base


class Bot(base):
    __tablename__ = 'bots'

    bot_id = Column(String, primary_key=True)
    token = Column(String)
    state = Column(JSON)
    config = Column(JSON)
    owner_login = Column(String, ForeignKey('users.login'))
