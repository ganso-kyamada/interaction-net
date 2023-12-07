from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from interaction_net.models.base import Base


class LotteryResultUser(Base):
    __tablename__ = "lottery_result_users"
    id = Column(Integer, primary_key=True)
    lottery_result_id = Column(Integer, ForeignKey("lottery_results.id"))
    user_uuid = Column(String)
    is_winner = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
