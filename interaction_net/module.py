import time
import random
import sys, getopt
import os
from datetime import datetime, timedelta
from interaction_net.scrape import Scrape
from interaction_net.storage import Storage


class IntarctionNet:
    def __init__(self, url="", webdriver_path=None, debug_mode=False):
        self.url = url
        self.webdriver_path = webdriver_path
        self.debug_mode = debug_mode

    def apply(self):
        scrape = Scrape(url=self.url, webdriver_path=self.webdriver_path, debug_mode=self.debug_mode)
        storage = Storage()
        current_year = datetime.now().year
        current_month = datetime.now().month
        date = self.__find_fourth_saturday(current_year, current_month)

        debug_count = 0
        for user in storage.csv("users"):
            scrape.login(user["id"], user["pass"])

            if scrape.apply_menu() is False:
                scrape.logout()
                continue

            if self.debug_mode is True and debug_count > 3:
                break

            if self.debug_mode is True:
                debug_count += 1
                scrape.logout()
                continue

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
        scrape.quit()

    def result(self):
        scrape = Scrape(url=self.url, webdriver_path=self.webdriver_path, debug_mode=self.debug_mode)
        storage = Storage()
        for user in storage.csv("users"):
            scrape.login(user["id"], user["pass"])
            scrape.result()
            scrape.logout()
            time.sleep(random.randint(1, 10))
        scrape.quit()

    def __find_fourth_saturday(self, year, month):
        first_day_of_month = datetime(year, month, 1)
        weekday_of_first = first_day_of_month.weekday()
        days_until_first_saturday = (5 - weekday_of_first) % 7
        first_saturday = first_day_of_month + timedelta(days=days_until_first_saturday)
        fourth_saturday = first_saturday + timedelta(weeks=3)
        return fourth_saturday.strftime("%Y%m%d")

