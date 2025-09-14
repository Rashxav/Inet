import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import WebDriverException, TimeoutException
from config.config import LOGIN_URL, PHONE_FIELD, PASSWORD_FIELD, LOGIN_BUTTON
from phone_normalizer import PhoneNormalizer


CHECK_URL = "https://www.google.com"


def load_credentials():
    config_path = os.path.join("config", "config.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError("Файл config.json не найден. Введите телефон и пароль через приложение.")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_webdriver(browser="firefox"):
    if browser == "firefox":
        options = FirefoxOptions()

    elif browser == "chrome":
        options = ChromeOptions()

    elif browser == "edge":
        options = EdgeOptions()

    else:
        return None

    options.headless = False
    try:
        if browser == "firefox":
            return webdriver.Firefox(options=options)

        elif browser == "chrome":
            return webdriver.Chrome(options=options)

        elif browser == "edge":
            return webdriver.Edge(options=options)

    except WebDriverException:
        return None


def internet_is_available() -> bool:
    for browser in ["firefox", "chrome", "edge"]:
        driver = get_webdriver(browser)
        if driver:
            try:
                driver.set_page_load_timeout(5)
                driver.get(CHECK_URL)
                driver.quit()
                return True
            except (WebDriverException, TimeoutException):
                driver.quit()
    return False


def reconnect():
    creds = load_credentials()
    phone = creds.get("phone")
    password = creds.get("password")

    normalizer = PhoneNormalizer()
    phone = normalizer.normalize(phone)

    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} ⚠ Попытка переподключения...")

    driver = None
    for browser in ["firefox", "chrome", "edge"]:
        driver = get_webdriver(browser)
        if driver:
            break

    if not driver:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} ❌ Нет доступных браузеров")
        return

    driver.get(LOGIN_URL)
    time.sleep(1)

    phone_input = driver.find_element(By.ID, PHONE_FIELD)
    phone_input.clear()
    phone_input.send_keys(phone)

    pwd_input = driver.find_element(By.ID, PASSWORD_FIELD)
    pwd_input.clear()
    pwd_input.send_keys(password)

    driver.find_element(By.ID, LOGIN_BUTTON).click()
    time.sleep(5)
    driver.quit()

    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} ✅ Переподключение завершено")
