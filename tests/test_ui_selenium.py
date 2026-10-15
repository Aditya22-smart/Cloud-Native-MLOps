import os
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.getenv(
    "APP_BASE_URL", "http://host.docker.internal:5000"
)
SELENIUM_REMOTE_URL = os.getenv(
    "SELENIUM_REMOTE_URL", "http://127.0.0.1:4444"
)
SCREENSHOT_DIR = Path("reports/screenshots")


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.set_capability("acceptInsecureCerts", True)

    browser = webdriver.Remote(
        command_executor=SELENIUM_REMOTE_URL,
        options=options,
    )
    browser.set_window_size(1280, 900)
    yield browser
    browser.quit()


def test_pricing_form_predicts_price(driver):
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    driver.get(BASE_URL)

    try:
        assert driver.find_element(By.ID, "pricing-form")

        fields = {
            "Base_Price": "100",
            "Competitor_Price": "95",
            "Inventory_Level": "250",
            "Units_Sold_Past_7D": "80",
            "Discount_Pct": "10",
            "Seasonal_Trend": "1.1",
        }
        for field_id, value in fields.items():
            field = driver.find_element(By.ID, field_id)
            field.clear()
            field.send_keys(value)

        driver.find_element(
            By.CSS_SELECTOR, "#pricing-form button[type='submit']"
        ).click()

        WebDriverWait(driver, 15).until(
            lambda browser: browser.find_element(By.ID, "result")
            .text.startswith("Predicted price:")
        )
        assert "Predicted price:" in driver.find_element(
            By.ID, "result"
        ).text

    except Exception:
        driver.save_screenshot(
            str(SCREENSHOT_DIR / "test_pricing_form_failure.png")
        )
        raise
