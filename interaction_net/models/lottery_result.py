from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from datetime import datetime
from interaction_net.models.base import Base

scrape_status_enum = ENUM(
    "pending", "in_progress", "completed", name="scrape_status_types", create_type=True
)


class LotteryResult(Base):
    __tablename__ = "lottery_results"
    id = Column(Integer, primary_key=True)
    scrape_status = Column(scrape_status_enum)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    lottery_result_users = relationship("LotteryResultUser", backref="lottery_result")
