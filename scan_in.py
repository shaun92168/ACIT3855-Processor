from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class ScanIn(Base):
    """ Scan In """

    __tablename__ = "scan_in"

    id = Column(Integer, primary_key=True)
    member_id= Column(String(250), nullable=False)
    store_id = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, member_id, store_id, timestamp):
        """ Initializes a scan in record """
        self.member_id = member_id
        self.store_id = store_id
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        """ Dictionary Representation of a scan in record """
        dict = {}
        dict['id'] = self.id
        dict['member_id'] = self.member_id
        dict['store_id'] = self.store_id
        dict['timestamp'] = self.timestamp
        return dict
