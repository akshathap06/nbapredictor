from sqlalchemy import Column, Integer, String, Float, DateTime
from .db import Base

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    home_team = Column(String, index=True)
    away_team = Column(String, index=True)
    prediction = Column(Float)
    game_date = Column(DateTime)
    actual_result = Column(String) 