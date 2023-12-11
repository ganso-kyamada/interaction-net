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


class IntarctionNet:
    def __init__(self, url="", webdriver_path=None, binary_location=None, force=False):
        self.scrape = Scrape(
            url=url, webdriver_path=webdriver_path, binary_location=binary_location
        )
        self.storage = Storage()
        self.force = force
        self.results = {"errors": []}
        Base.metadata.create_all(bind=ENGINE)

    def apply(self):
        """
        抽選の申し込みを行う
        """
        date = self.__find_date()
        session = Session(bind=ENGINE)
        if LotteryApply.is_scraped(session) is True:
            self.results["errors"].append("Already scraped.")
            return self.results
        lottery_apply = LotteryApply.create_with_users(
            session, date, self.storage.csv("users")
        )

        self.results["success"] = []
        for user in self.__scrape_users():
            lottery_apply_user = lottery_apply.find_pending_lottery_apply_user(
                session, user["id"]
            )
            if lottery_apply_user is None:
                continue
            lottery_apply_user.update_scrape_status(session, "in_progress")
            self.__scrape_apply(user, date.strftime("%Y%m%d"))
            lottery_apply_user.update_scrape_status(session, "completed")
            self.results["success"].append(user["id"])
        return self.results

    def result(self):
        """
        抽選結果を取得する
        """
        session = Session(bind=ENGINE)
        if self.force is False and LotteryResult.is_scraped(session) is True:
            self.results["errors"].append("Already scraped.")
            return self.results
        lottery_result = LotteryResult.create_in_progress(session)

        self.results["accepted"] = []
        self.results["rejected"] = []
        for user in self.__scrape_users():
            lottery_result_user = lottery_result.create_lottery_result_user(
                session, user["id"]
            )
            self.scrape.login(user["id"], user["pass"])
            if self.scrape.result() is True:
                self.results["accepted"].append(user["id"])
                lottery_result_user.win(session)
            else:
                self.results["rejected"].append(user["id"])
                lottery_result_user.lose(session)
            self.scrape.logout()
        lottery_result.completed(session)
        return self.results

    def test(self):
        """
        WebDriverのテストを行う
        """
        self.results["success"] = []
        count = 0
        for user in self.__scrape_users():
            count += 1
            if self.force is False and count > 3:
                break
            self.scrape.login(user["id"], user["pass"])
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
        """
        self.scrape.login(user["id"], user["pass"])

        if self.scrape.apply_menu() is False:
            self.scrape.logout()
            return

        for ground in self.storage.csv("grounds"):
            purpose_type = "利用目的から"
            for schedule in self.storage.csv("schedules"):
                self.scrape.purpose_menu(
                    purpose_type,
                    ground["sports_type"],
                    ground["sports_name"],
                    ground["name"],
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

    def __find_date(self):
        """
        申し込み日を取得する
        申し込み日は毎月第4土曜日とする

        :return: 申し込み日
        """
        current_date = datetime.now()
        next_month = current_date.replace(day=1) + timedelta(days=32)
        first_day_of_month = datetime(next_month.year, next_month.month, 1)
        weekday_of_first = first_day_of_month.weekday()
        days_until_first_saturday = (5 - weekday_of_first) % 7
        first_saturday = first_day_of_month + timedelta(days=days_until_first_saturday)
        fourth_saturday = first_saturday + timedelta(weeks=3)
        return fourth_saturday
