import time
import random
import sys, getopt
import os
import logging
from datetime import datetime, timedelta
from interaction_net.scrape import Scrape
from interaction_net.storage import Storage
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import UnexpectedAlertPresentException


class IntarctionNet:
    def __init__(self, url="", webdriver_path=None, binary_location=None):
        self.scrape = Scrape(
            url=url, webdriver_path=webdriver_path, binary_location=binary_location
        )
        self.storage = Storage()
        self.results = {"errors": []}

    def apply(self):
        self.results["success"] = []
        date = self.__find_date()
        for user in self.__scrape_users():
            self.__scrape_apply(user, date)
            self.results["success"].append(user["id"])
        return self.results

    def result(self):
        self.results["accepted"] = []
        self.results["rejected"] = []
        for user in self.__scrape_users():
            self.scrape.login(user["id"], user["pass"])
            if self.scrape.result() is True:
                self.results["accepted"].append(user["id"])
            else:
                self.results["rejected"].append(user["id"])
            self.scrape.logout()
        return self.results

    def test(self):
        self.results["success"] = []
        count = 0
        for user in self.__scrape_users():
            count += 1
            if count > 3:
                break
            self.scrape.login(user["id"], user["pass"])
            self.scrape.apply_menu()
            self.scrape.logout()
            self.results["success"].append(user["id"])
        return self.results

    def __scrape_users(self):
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
        current_date = datetime.now()
        next_month = current_date.replace(day=1) + timedelta(days=32)
        first_day_of_month = datetime(next_month.year, next_month.month, 1)
        weekday_of_first = first_day_of_month.weekday()
        days_until_first_saturday = (5 - weekday_of_first) % 7
        first_saturday = first_day_of_month + timedelta(days=days_until_first_saturday)
        fourth_saturday = first_saturday + timedelta(weeks=3)
        return fourth_saturday.strftime("%Y%m%d")
