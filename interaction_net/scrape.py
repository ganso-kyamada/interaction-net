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
import logging


class Scrape:
    WIN_COUNT = 4
    url = ""
    debug_mode = False
    driver = None
    user = ""

    def __init__(self, url="", webdriver_path=None, binary_location=None):
        self.url = url
        self.driver = self.__set_webdriver(webdriver_path, binary_location)
        self.initialize()
        self.width = self.driver.execute_script("return document.body.scrollWidth")
        self.height = self.driver.execute_script("return document.body.scrollHeight")

    def initialize(self):
        self.driver.get(self.url)

    def login(self, user, password):
        logging.info(f"[{user}]: Login")
        user_element = self.driver.find_element(By.ID, "userId")
        password_element = self.driver.find_element(By.ID, "pass")
        user_element.send_keys(user)
        password_element.send_keys(password)
        password_element.send_keys(Keys.ENTER)
        if self.__is_alert_present():
            logging.info(f"[{self.user}]: Not Applied")
            self.__alert_accept(30)
            return False
        self.user = user
        return True

    def apply_menu(self):
        logging.info(f"[{self.user}]: ApplyMenu")
        self.__to_home("抽選の申込み")
        try:
            self.driver.find_element(By.LINK_TEXT, "抽選の申込み").click()
        except NoSuchElementException:
            return False
        return True

    def purpose_menu(self, purpose_type, sports_type, sports_name, ground_type, ground_name):
        logging.info(f"[{self.user}]: PurposeMenu")
        self.driver.find_element(By.XPATH, f"//input[@value='{purpose_type}']").click()
        self.driver.find_element(By.LINK_TEXT, sports_type).click()
        self.driver.find_element(By.LINK_TEXT, sports_name).click()
        rows = self.driver.find_elements(By.XPATH, "//tbody/tr")
        for row in rows:
            if ground_type in row.text:
                row.find_element(By.XPATH, ".//input[@value='申込み']").click()
                break
        self.driver.find_element(By.LINK_TEXT, ground_name).click()

    def calender(self, date, since_date, until_date):
        logging.info(f"[{self.user}]: Calender {date}, {since_date}, {until_date}")
        # self.driver.find_element(By.XPATH, "//input[@value='最終週']").click()
        is_match = False
        for i in range(5):
            is_match = self.__calender_match(date, since_date, until_date)
            if is_match is True:
                break

            try:
                self.driver.find_element(By.XPATH, "//input[@value='次の週']").click()
            except NoSuchElementException:
                logging.info(f"[{self.user}]: Not Match Calender")

        if is_match is True:
            self.driver.find_element(By.XPATH, "//input[@value='申込み']").click()
        else:
            self.driver.find_element(By.LINK_TEXT, "抽選").click()
        return is_match

    def apply(self, people):
        logging.info(f"[{self.user}]: Apply")
        people_element = self.driver.find_element(By.ID, "applyPepopleNum")
        people_element.send_keys(people)
        self.driver.find_element(By.XPATH, "//input[@value='申込み']").click()

        self.__alert_accept(30)
        # 申し込み制限オーバー対策にもう一回
        return self.__alert_accept(3) is False

    def complete(self):
        logging.info(f"[{self.user}]: Complate")
        self.driver.find_element(By.LINK_TEXT, "ホーム").click()
        self.driver.find_element(By.LINK_TEXT, "抽選申込みの確認").click()
        # self.screenshot("complete")

    def result(self):
        logging.info(f"[{self.user}]: Result")
        self.__to_home("確認済の抽選結果")
        self.driver.find_element(By.LINK_TEXT, "確認済の抽選結果").click()
        if self.__is_alert_present():
            logging.info(f"[{self.user}]: Not Applied")
            self.__alert_accept(30)
            return False

        lose_elements = self.driver.find_elements(
            By.XPATH, "//*[contains(text(), '落選')]"
        )
        if len(lose_elements) == 4:
            logging.info(f"[{self.user}]: All Lose...")
            return False
        return True

    def logout(self):
        self.driver.find_element(By.XPATH, "//input[@value='ログアウト']").click()
        logging.info(f"[{self.user}]: Logout!")

    def cancel(self):
        logging.info(f"[{self.user}]: Cancel")
        self.__to_home("抽選申込みの取消")
        self.driver.find_element(By.LINK_TEXT, "抽選申込みの取消").click()
        if self.__is_alert_present():
            logging.info(f"[{self.user}]: Not Applied")
            self.__alert_accept(30)
            return False

        checkbox_ids = ["checkcancel0", "checkcancel1", "checkcancel2", "checkcancel3"]
        for checkbox_id in checkbox_ids:
            try:
                checkbox = self.driver.find_element(By.ID, checkbox_id)
                if not checkbox.is_selected():
                    checkbox.click()
            except NoSuchElementException:
                break
        self.driver.find_element(By.XPATH, "//input[@value='取消']").click()
        self.__alert_accept(30)
        return True

    def quit(self):
        self.driver.quit()

    def __set_webdriver(self, webdriver_path, binary_location):
        options = webdriver.ChromeOptions()
        options.binary_location = binary_location
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--enable-logging")
        options.add_argument("--log-level=0")
        options.add_argument("--v=99")
        options.add_argument("--single-process")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-dev-shm-usage")
        return webdriver.Chrome(webdriver_path, options=options)

    def __to_home(self, element_name):
        elements = self.driver.find_elements(By.LINK_TEXT, element_name)
        if len(elements) == 0:
            # self.screenshot('alert')
            self.driver.find_element(By.XPATH, "//input[@value='次へ']").click()

    def __calender_match(self, date, since_date, until_date):
        is_match = False
        for link_tag in self.driver.find_elements(By.TAG_NAME, "a"):
            href = link_tag.get_attribute("href")
            if href is None:
                continue

            if date in href and since_date in href and until_date in href:
                is_match = True
                logging.info(f"[{self.user}]: Calender Match!!")
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
            logging.error(f"[{self.user}]: {e}")

        return accept

    def screenshot(self, name):
        filename = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), f"images/{name}_{self.user}.png"
        )
        logging.info(f"[{self.user}]: Screenshot {filename}")
        self.driver.set_window_size(self.width, self.height)
        self.driver.save_screenshot(filename)

    def __is_alert_present(self):
        try:
            self.driver.switch_to.alert
            return True
        except NoAlertPresentException:
            return False
