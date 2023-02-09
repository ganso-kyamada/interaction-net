from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import os
import re


class Scrape:
    user = ""

    def __init__(self):
        self.driver = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            options=webdriver.ChromeOptions(),
        )
        self.driver.get(os.environ["URL"])
        self.width = self.driver.execute_script("return document.body.scrollWidth")
        self.height = self.driver.execute_script("return document.body.scrollHeight")

    def login(self, user, password):
        print(f"INFO[{user}]: Login")
        user_element = self.driver.find_element(By.ID, "userId")
        password_element = self.driver.find_element(By.ID, "pass")
        user_element.send_keys(user)
        password_element.send_keys(password)
        password_element.send_keys(Keys.ENTER)
        self.user = user

    def apply_menu():
        print(f"INFO[{self.user}]: ApplyMenu")
        try:
            self.driver.find_element(By.LINK_TEXT, "抽選の申込み").click()
        except NoSuchElementException:
            self.driver.find_element(By.XPATH, "//input[@value='次へ']").click()
            self.driver.find_element(By.LINK_TEXT, "抽選の申込み").click()


    def purpose_menu(self, purpose_type, sports_type, sports_name, ground_name):
        print(f"INFO[{self.user}]: PurposeMenu")
        self.driver.find_element(By.XPATH, f"//input[@value='{purpose_type}']").click()
        self.driver.find_element(By.LINK_TEXT, sports_type).click()
        self.driver.find_element(By.LINK_TEXT, sports_name).click()
        self.driver.find_element(By.XPATH, "//input[@value='申込み']").click()
        self.driver.find_element(By.LINK_TEXT, ground_name).click()

    def calender(self, date, since_date, until_date):
        print(f"INFO[{self.user}]: Calender")
        # TODO: 調整が必要
        # self.driver.find_element(By.XPATH, "//input[@value='次の週']").click()
        # self.driver.find_element(By.XPATH, "//input[@value='最終週']").click()
        for link_tag in self.driver.find_elements(By.TAG_NAME, "a"):
            href = link_tag.get_attribute("href")
            if href is None:
                continue

            if date in href and since_date in href and until_date in href:
                print(f"INFO[{self.user}]: Calender Match!!")
                link_tag.click()
                break
        self.driver.find_element(By.XPATH, "//input[@value='申込み']").click()

    def apply(self, people):
        print(f"INFO[{self.user}]: Apply")
        people_element = self.driver.find_element(By.ID, "applyPepopleNum")
        people_element.send_keys(people)
        self.driver.find_element(By.XPATH, "//input[@value='申込み']").click()

        self.__alert_accept(30)
        # 申し込み制限オーバー対策にもう一回
        return self.__alert_accept(3) is False

    def complete(self):
        print(f"INFO[{self.user}]: Complate")
        self.driver.find_element(By.LINK_TEXT, "ホーム").click()
        self.driver.find_element(By.LINK_TEXT, "抽選申込みの確認").click()
        self.__screenshot("complete")

    def result(self):
        print(f"INFO[{self.user}]: Result")
        try:
            self.driver.find_element(By.LINK_TEXT, "確認済の抽選結果").click()
        except NoSuchElementException:
            self.driver.find_element(By.XPATH, "//input[@value='次へ']").click()
            self.driver.find_element(By.LINK_TEXT, "確認済の抽選結果").click()
        self.__screenshot("result")

    def logout(self):
        self.driver.find_element(By.XPATH, "//input[@value='ログアウト']").click()
        print(f"INFO[{self.user}]: Logout!")

    def quit(self):
        self.driver.quit()

    def __alert_accept(self, second):
        accept = False
        try:
            wait = WebDriverWait(self.driver, second)
            wait.until(EC.alert_is_present())
            self.driver.switch_to.alert.accept()
            accept = True
        except TimeoutException:
            pass
        except Exception as e:
            print(f"ERROR[{self.user}]: {e}")

        return accept

    def __screenshot(self, name):
        filename = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), f"images/{name}_{self.user}.png"
        )
        self.driver.set_window_size(self.width, self.height)
        self.driver.save_screenshot(filename)
