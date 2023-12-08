from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from datetime import datetime
from interaction_net.models.base import Base
from interaction_net.models.enums import SCRAPE_STATUS_ENUM


class LotteryResult(Base):
    __tablename__ = "lottery_results"
    id = Column(Integer, primary_key=True)
    scrape_status = Column(SCRAPE_STATUS_ENUM)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    lottery_result_users = relationship("LotteryResultUser", backref="lottery_result")

    @classmethod
    def is_scraped(cls, session):
        """
        スクレイピング済みかどうかを判定する

        :param session: SQLAlchemy セッション
        :return: bool
        """
        current_date = datetime.now()
        first_day_of_month = datetime(current_date.year, current_date.month, 1)
        return (
            session.query(cls).filter(cls.created_at >= first_day_of_month).first()
            is not None
        )

    @classmethod
    def create_in_progress(cls, session):
        """
        in_progress状態のLotteryResultを作成する

        :param session: SQLAlchemy セッション
        :return: LotteryResult
        """
        lottery_result = cls(scrape_status="in_progress")
        session.add(lottery_result)
        session.commit()
        return lottery_result

    def completed(self, session):
        """
        スクレイピングが完了したことを記録する

        :param session: SQLAlchemy セッション
        :return: None
        """
        self.scrape_status = "completed"
        session.commit()

    def create_lottery_result_user(self, session, user_uuid):
        """
        LotteryResultUserを作成する

        :param session: SQLAlchemy セッション
        :param user_uuid: ユーザーUUID
        :return: LotteryResultUser
        """
        lottery_result_user = LotteryResultUser(
            lottery_result_id=self.id, user_uuid=user_uuid, is_winner=False
        )
        session.add(lottery_result_user)
        session.commit()
        return lottery_result_user
