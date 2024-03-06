from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, desc
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from datetime import datetime
from interaction_net.models.base import Base
from interaction_net.models.lottery_apply_user import LotteryApplyUser


class LotteryApply(Base):
    __tablename__ = "lottery_applies"
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    lottery_apply_users = relationship("LotteryApplyUser", backref="lottery_applies")

    @classmethod
    def create_with_users(cls, session, date, users):
        """
        LotteryApplyとLotteryApplyUserを作成する

        :param session: SQLAlchemy セッション
        :param date: 日付
        :param users: ユーザー情報
        :return: LotteryApply
        """
        lottery_apply = cls(date=date)
        session.add(lottery_apply)
        session.commit()
        lottery_apply_users = []
        for user in users:
            lottery_apply_user = LotteryApplyUser(
                lottery_apply_id=lottery_apply.id,
                user_uuid=user["id"],
                scrape_status="pending",
            )
            lottery_apply_users.append(lottery_apply_user)
        session.bulk_save_objects(lottery_apply_users)
        return lottery_apply

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
    def last(cls, session):
        """
        最後の値を取得する

        :param session: SQLAlchemy セッション
        :return: LotteryApply
        """
        return session.query(cls).order_by(desc(cls.id)).first()

    @classmethod
    def find_by_date(cls, session, date):
        """
        日付でLotteryApplyを取得する

        :param session: SQLAlchemy セッション
        :param date: 日付
        :return: LotteryApply
        """
        return session.query(cls).filter(cls.date == date).first()

    def find_lottery_apply_user_by_scrape_status(
        self, session, user_uuid, scrape_status
    ):
        """
        scrape_statusが同じLotteryApplyUserを取得する

        :param session: SQLAlchemy セッション
        :param user_uuid: ユーザーUUID
        :param scrape_status: スクレイピング結果
        :return: LotteryApplyUser
        """
        return (
            session.query(LotteryApplyUser)
            .filter_by(
                lottery_apply_id=self.id,
                user_uuid=user_uuid,
                scrape_status=scrape_status,
            )
            .first()
        )

    def create_lottery_apply_user(self, session, user_uuid):
        """
        LotteryApplyUserを作成する

        :param session: SQLAlchemy セッション
        :param user_uuid: ユーザーUUID
        :return: LotteryApplyUser
        """
        return LotteryApplyUser.create(session, self.id, user_uuid)