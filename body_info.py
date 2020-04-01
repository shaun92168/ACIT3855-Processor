from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class BodyInfo(Base):
    """ Body Info """

    __tablename__ = "body_info"

    id = Column(Integer, primary_key=True)
    member_id= Column(String(250), nullable=False)
    store_id = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    weight = Column(Integer, nullable=False)
    body_fat = Column(Integer, nullable=False)

    def __init__(self, member_id, store_id, timestamp, weight, body_fat):
        """ Initializes a body info record """
        self.member_id = member_id
        self.store_id = store_id
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now()
        self.weight = weight
        self.body_fat = body_fat

    def to_dict(self):
        """ Dictionary Representation of a body info record """
        dict = {}
        dict['id'] = self.id
        dict['member_id'] = self.member_id
        dict['store_id'] = self.store_id
        dict['body_info'] = {}
        dict['body_info']['weight'] = self.weight
        dict['body_info']['body_fat'] = self.body_fat
        dict['timestamp'] = self.timestamp
        return dict
