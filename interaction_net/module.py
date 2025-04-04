import time
import random
import sys, getopt
import os
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from interaction_net.models.base import Base, ENGINE
from interaction_net.models.lottery_apply import LotteryApply
from interaction_net.models.lottery_apply_user import LotteryApplyUser
from interaction_net.models.lottery_result import LotteryResult
from interaction_net.models.lottery_result_user import LotteryResultUser
from interaction_net.scrape import Scrape
from interaction_net.storage import Storage
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import UnexpectedAlertPresentException


class InteractionNet:
    def __init__(self, url="", webdriver_path=None, binary_location=None):
        self.scrape = Scrape(
            url=url, webdriver_path=webdriver_path, binary_location=binary_location
        )
        self.storage = Storage()
        self.results = {"errors": []}
        Base.metadata.create_all(bind=ENGINE)

    def apply(self, weeks=4, is_retry=False):
        """
        抽選の申し込みを行う
        """
        date = self.__find_date(weeks)
        logging.info(f"Date: {date}")
        session = Session(bind=ENGINE)

        lottery_apply = LotteryApply.find_by_date(session, date)
        if is_retry is False and lottery_apply is not None:
            self.results["errors"].append("Already scraped.")
            return self.results
        if lottery_apply is None:
            if is_retry is False:
                lottery_apply = LotteryApply.create_with_users(
                    session, date, self.storage.csv("users")
                )
            else:
                lottery_apply = LotteryApply.last(session)

        self.results["success"] = []
        for user in self.__scrape_users():
            lottery_apply_user = lottery_apply.find_lottery_apply_user_by_scrape_status(
                session, user["id"], "pending"
            )
            if lottery_apply_user is None:
                if is_retry is True:
                    lottery_apply_user = lottery_apply.create_lottery_apply_user(
                        session, user["id"]
                    )
                else:
                    continue

            lottery_apply_user.update_scrape_status(session, "in_progress")
            if self.__scrape_apply(user, date.strftime("%Y%m%d")):
                lottery_apply_user.update_scrape_status(session, "completed")
            else:
                lottery_apply_user.update_scrape_status(session, "error")
            self.results["success"].append(user["id"])
        return self.results

    def result(self, is_retry=False):
        """
        抽選結果を取得する
        """
        session = Session(bind=ENGINE)
        if is_retry is False and LotteryResult.is_scraped(session) is True:
            self.results["errors"].append("Already scraped.")
            return self.results
        lottery_result = (
            LotteryResult.last(session)
            if is_retry
            else LotteryResult.create_with_users(session)
        )

        self.results["accepted"] = []
        self.results["rejected"] = []
        for user in self.__scrape_users():
            lottery_result_user = lottery_result.find_by_id(session, user["id"])

            if lottery_result_user is None:
                lottery_result_user = lottery_result.create_lottery_result_user(
                    session, user["id"]
                )
            else:
                logging.info(f"SKIP!! {lottery_result_user.user_uuid}")
                continue

            if self.scrape.login(user["id"], user["pass"]) is False:
                lottery_result_user.lose(session)
                continue

            if self.scrape.result() is True:
                self.results["accepted"].append(user["id"])
                lottery_result_user.win(session)
            else:
                self.results["rejected"].append(user["id"])
                lottery_result_user.lose(session)
            self.scrape.logout()
        lottery_result.completed(session)
        return self.results

    def cancel(self):
        """
        申し込みをキャンセルする
        """
        session = Session(bind=ENGINE)

        if LotteryApply.is_scraped(session) is False:
            self.results["errors"].append("Not scraped.")
            return self.results

        lottery_apply = LotteryApply.last(session)
        if lottery_apply is None:
            self.results["errors"].append("Not found.")
            return self.results

        self.results["success"] = []
        self.results["skipped"] = []
        for user in self.__scrape_users():
            lottery_apply_user = lottery_apply.find_lottery_apply_user_by_scrape_status(
                session, user["id"], "completed"
            )
            if lottery_apply_user is None:
                continue
            if self.scrape.login(user["id"], user["pass"]) is False:
                continue

            if self.scrape.cancel() is True:
                self.results["success"].append(user["id"])
                lottery_apply_user.update_scrape_status(session, "canceled")
            else:
                self.results["skipped"].append(user["id"])
            self.scrape.logout()
        return self.results

    def test(self):
        """
        WebDriverのテストを行う
        """
        self.results["success"] = []
        count = 0
        for user in self.__scrape_users():
            count += 1
            if count > 3:
                break
            if self.scrape.login(user["id"], user["pass"]) is False:
                continue
            self.scrape.result()
            self.scrape.screenshot("result")
            self.scrape.logout()
            self.results["success"].append(user["id"])
        return self.results

    def __scrape_users(self):
        """
        ユーザー情報をスクレイピングする

        :return: ユーザー情報
        """
        for user in self.storage.csv("users"):
            try:
                yield user
            except (
                TimeoutException,
                NoSuchElementException,
                NoAlertPresentException,
                UnexpectedAlertPresentException,
            ) as e:
                logging.error(f"[{user}]: {e}")
                self.results["errors"].append(f"{user}: {e}")
                self.scrape.initialize()
            time.sleep(random.randint(1, 10))
        self.scrape.quit()

    def __scrape_apply(self, user, date):
        """
        申し込みをスクレイピングする

        :param user: ユーザー情報
        :param date: 日付
        :return: bool
        """
        if self.scrape.login(user["id"], user["pass"]) is False:
            return False

        if self.scrape.apply_menu() is False:
            self.scrape.logout()
            return False

        for ground in self.storage.csv("grounds"):
            purpose_type = "利用目的から"
            for schedule in self.storage.csv("schedules"):
                self.scrape.purpose_menu(
                    purpose_type,
                    ground["sports_type"],
                    ground["sports_name"],
                    ground["ground_type"],
                    schedule["ground_name"]
                )
                if (
                    self.scrape.calender(date, schedule["start"], schedule["end"])
                    is False
                ):
                    continue
                if self.scrape.apply(schedule["people"]) is False:
                    break
                purpose_type = "目的から"
        self.scrape.complete()
        self.scrape.logout()
        time.sleep(random.randint(1, 10))
        return True

    def __find_date(self, weeks):
        """
        申し込み日を取得する

        :param weeks: 申込日を第何週の土曜日にするか
        :return: 申し込み日
        """
        current_date = datetime.now()
        next_month = current_date.replace(day=1) + timedelta(days=32)
        first_day_of_month = datetime(next_month.year, next_month.month, 1)
        weekday_of_first = first_day_of_month.weekday()
        days_until_first_saturday = (5 - weekday_of_first) % 7
        first_saturday = first_day_of_month + timedelta(days=days_until_first_saturday)

        weeks = weeks - 1
        fourth_saturday = first_saturday + timedelta(weeks=weeks)
        return fourth_saturday
