from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import WebDriverException, TimeoutException


CHECK_URL = "https://www.google.com"


def get_webdriver(browser="firefox"):
    try:
        if browser == "firefox":
            options = FirefoxOptions()
            options.headless = True
            return webdriver.Firefox(options=options)

        elif browser == "chrome":
            options = ChromeOptions()
            options.headless = True
            return webdriver.Chrome(options=options)

        elif browser == "edge":
            options = EdgeOptions()
            options.headless = True
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
