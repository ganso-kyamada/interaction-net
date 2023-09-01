import time
import random
import sys, getopt
from scrape import Scrape
from storage import Storage


def lottery_apply():
    scrape = Scrape()
    storage = Storage()
    for user in storage.csv("users"):
        scrape.login(user["id"], user["pass"])
        if scrape.apply_menu() is False:
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
                if scrape.calender(schedule["date"], schedule["start"], schedule["end"]) is False:
                    continue

                if scrape.apply(schedule["people"]) is False:
                    break
                purpose_type = "目的から"
        scrape.complete()
        scrape.logout()
        time.sleep(random.randint(1, 10))
    scrape.quit()

def lottery_result():
    scrape = Scrape()
    storage = Storage()
    for user in storage.csv("users"):
        scrape.login(user["id"], user["pass"])
        scrape.result()
        scrape.logout()
        time.sleep(random.randint(1, 10))
    scrape.quit()

def main(argv):
    opts, args = getopt.getopt(argv,"har",["apply","result"])
    for opt, arg in opts:
      if opt == '-h':
         print ('./interaction-net/__main__.py [-a|-r]')
         sys.exit()
      elif opt in ("-a", "--apply"):
         lottery_apply()
      elif opt in ("-r", "--result"):
         lottery_result()

if __name__ == "__main__":
    main(sys.argv[1:])
