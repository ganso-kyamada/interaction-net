import time
import random
from scrape import Scrape
from storage import Storage


def execute():
    scrape = Scrape()
    storage = Storage()
    for user in storage.csv("users"):
        scrape.login(user["id"], user["pass"])
        for ground in storage.csv("grounds"):
            target_type = "利用目的から"
            for schedule in storage.csv("schedules"):
                scrape.menu(
                    target_type,
                    ground["sports_type"],
                    ground["sports_name"],
                    ground["name"],
                )
                scrape.calender(schedule["date"], schedule["start"], schedule["end"])
                if scrape.apply(schedule["people"]) is False:
                    break
                target_type = "目的から"
        scrape.complete()
        time.sleep(random.randint(1, 10))
    scrape.quit()


if __name__ == "__main__":
    execute()
