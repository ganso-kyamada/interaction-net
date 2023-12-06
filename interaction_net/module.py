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
        self.url = url
        self.webdriver_path = webdriver_path
        self.binary_location = binary_location

    def apply(self):
        results = {"success": [], "errors": []}
        scrape = Scrape(
            url=self.url,
            webdriver_path=self.webdriver_path,
            binary_location=self.binary_location,
            debug_mode=self.debug_mode,
        )
        storage = Storage()
        date = self.__find_date()
        for user in storage.csv("users"):
            try:
                self.__execute_apply(scrape, storage, user, date)
                results["success"].append(user["id"])
            except (
                TimeoutException,
                NoSuchElementException,
                NoAlertPresentException,
                UnexpectedAlertPresentException,
            ) as e:
                logging.error(f"[{user}]: {e}")
                results["errors"].append(f"{user}: {e}")
                scrape.initialize()
        scrape.quit()
        return results

    def result(self):
        results = {"accepted": [], "rejected": [], "errors": []}
        scrape = Scrape(
            url=self.url,
            webdriver_path=self.webdriver_path,
            binary_location=self.binary_location,
        )
        storage = Storage()
        for user in storage.csv("users"):
            try:
                scrape.login(user["id"], user["pass"])
                if scrape.result() is True:
                    results["accepted"].append(user["id"])
                else:
                    results["rejected"].append(user["id"])
                scrape.logout()
            except (
                TimeoutException,
                NoSuchElementException,
                NoAlertPresentException,
                UnexpectedAlertPresentException,
            ) as e:
                logging.error(f"[{user}]: {e}")
                results["errors"].append(f"{user}: {e}")
                scrape.initialize()
            time.sleep(random.randint(1, 10))
        scrape.quit()
        return results

    def test(self):
        results = {"success": [], "errors": []}
        scrape = Scrape(
            url=self.url,
            webdriver_path=self.webdriver_path,
            binary_location=self.binary_location,
        )
        storage = Storage()
        count = 0
        for user in storage.csv("users"):
            count += 1
            if count > 3:
                break

            try:
                scrape.login(user["id"], user["pass"])
                scrape.apply_menu()
                scrape.logout()
                results["success"].append(user["id"])
            except (
                TimeoutException,
                NoSuchElementException,
                NoAlertPresentException,
                UnexpectedAlertPresentException,
            ) as e:
                logging.error(f"[{user}]: {e}")
                results["errors"].append(f"{user}: {e}")
                scrape.initialize()
        scrape.quit()
        return results

    def __execute_apply(self, scrape, storage, user, date):
        scrape.login(user["id"], user["pass"])

        if scrape.apply_menu() is False:
            scrape.logout()
            return

        for ground in storage.csv("grounds"):
            purpose_type = "利用目的から"
            for schedule in storage.csv("schedules"):
                scrape.purpose_menu(
                    purpose_type,
                    ground["sports_type"],
                    ground["sports_name"],
                    ground["name"],
                )
                if scrape.calender(date, schedule["start"], schedule["end"]) is False:
                    continue
                if scrape.apply(schedule["people"]) is False:
                    break
                purpose_type = "目的から"
        scrape.complete()
        scrape.logout()
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
