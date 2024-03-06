from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from interaction_net.models.base import Base
from interaction_net.models.enums import SCRAPE_STATUS_ENUM


class LotteryApplyUser(Base):
    __tablename__ = "lottery_apply_users"
    id = Column(Integer, primary_key=True)
    lottery_apply_id = Column(Integer, ForeignKey("lottery_applies.id"))
    scrape_status = Column(SCRAPE_STATUS_ENUM)
    user_uuid = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def update_scrape_status(self, session, scrape_status):
        """
        scrape_statusを更新する

        :param session: SQLAlchemy セッション
        :param scrape_status: ステータス
        :return: None
        """
        self.scrape_status = scrape_status
        session.commit()

    @classmethod
    def create(cls, session, lottery_apply_id, user_uuid):
        """
        LotteryApplyUserを作成する

        :param session: SQLAlchemy セッション
        :param lottery_apply_id: LotteryApply ID
        :param user_uuid: ユーザーID
        :return: LotteryApplyUser
        """
        lottery_apply_user = cls(
            lottery_apply_id=lottery_apply_id, user_uuid=user_uuid, scrape_status="pending"
        )
        session.add(lottery_apply_user)
        session.commit()
        return lottery_apply_user
