from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
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

    def apply_menu(self):
        apply_elements = self.driver.find_elements(By.LINK_TEXT, "抽選の申込み")
        print(f"INFO[{self.user}]: ApplyMenu {len(apply_elements)}")
        if len(apply_elements) == 0:
            self.__screenshot('alert')
            self.driver.find_element(By.XPATH, "//input[@value='次へ']").click()

        try:
            self.driver.find_element(By.LINK_TEXT, "抽選の申込み").click()
        except NoSuchElementException:
            return False
        return True


    def purpose_menu(self, purpose_type, sports_type, sports_name, ground_name):
        print(f"INFO[{self.user}]: PurposeMenu")
        self.driver.find_element(By.XPATH, f"//input[@value='{purpose_type}']").click()
        self.driver.find_element(By.LINK_TEXT, sports_type).click()
        self.driver.find_element(By.LINK_TEXT, sports_name).click()
        self.driver.find_element(By.XPATH, "//input[@value='申込み']").click()
        self.driver.find_element(By.LINK_TEXT, ground_name).click()

    def calender(self, date, since_date, until_date):
        print(f"INFO[{self.user}]: Calender")
        self.driver.find_element(By.XPATH, "//input[@value='最終週']").click()
        is_match = False
        for i in range(4):
            is_match = self.__calender_match(date, since_date, until_date)
            if is_match is True:
                break

            try:
                self.driver.find_element(By.XPATH, "//input[@value='前の週']").click()
            except NoSuchElementException:
                print(f"INFO[{self.user}]: Not Match Calender")

        if is_match is True:
            self.driver.find_element(By.XPATH, "//input[@value='申込み']").click()
        else:
            self.driver.find_element(By.LINK_TEXT, "抽選").click()
        return is_match

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
        result_elements = self.driver.find_elements(By.LINK_TEXT, "確認済の抽選結果")
        if len(result_elements) == 0:
            self.__screenshot('alert')
            self.driver.find_element(By.XPATH, "//input[@value='次へ']").click()

        self.driver.find_element(By.LINK_TEXT, "確認済の抽選結果").click()
        if self.__is_alert_present():
            print(f"INFO[{self.user}]: Not Applied")
            self.__alert_accept(30)
            return

        lose_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '落選')]")
        if len(lose_elements) == 4:
            print(f"INFO[{self.user}]: All Lose...")
            return
        self.__screenshot("result")

    def logout(self):
        self.driver.find_element(By.XPATH, "//input[@value='ログアウト']").click()
        print(f"INFO[{self.user}]: Logout!")

    def quit(self):
        self.driver.quit()

    def __calender_match(self, date, since_date, until_date):
        is_match = False
        for link_tag in self.driver.find_elements(By.TAG_NAME, "a"):
            href = link_tag.get_attribute("href")
            if href is None:
                continue

            if date in href and since_date in href and until_date in href:
                is_match = True
                print(f"INFO[{self.user}]: Calender Match!!")
                link_tag.click()
                break

        return is_match

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

    def __is_alert_present(self):
        try:
            self.driver.switch_to.alert
            return True
        except NoAlertPresentException:
            return False