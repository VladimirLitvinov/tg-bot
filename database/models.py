from sqlalchemy import Column, Integer, String, Date, DateTime

from .base import Base


class History(Base):
    """
    Table for recording user search history
    """
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_tg_id = Column(Integer)
    date_search = Column(DateTime)
    enter_date = Column(Date)
    exit_date = Column(Date)
    city = Column(String)
    adults = Column(Integer, nullable=False)
    children = Column(Integer, nullable=True, default=None)
    infants = Column(Integer, nullable=True, default=None)
    pets = Column(Integer, nullable=True, default=None)
    currency = Column(String, nullable=True, default=None)
