# src/selenium_scraper.py

from datetime import datetime, timezone
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def parse_web_timestamp(ts):
    """Parses timestamp from website format to UTC datetime object."""
    dt = datetime.strptime(ts, "%b %d, %Y - %I:%M %p")
    return dt.replace(tzinfo=timezone.utc)


def parse_api_timestamp(ts):
    """Parses ISO 8601 UTC timestamp string from n8n to UTC datetime object."""
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)


def main(start_date_str):
    # Convert API input to UTC datetime
    cutoff_date = parse_api_timestamp(start_date_str)

    # Headless Chrome options
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    filtered_data = []

    try:
        wait = WebDriverWait(driver, 90)
        driver.get("https://app.dyme.earth/")

        # Login process
        email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]')))
        email_input.send_keys("chloe@dyme.travel")
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "Button"))).click()

        password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]')))
        password_input.send_keys("zRvyy89wduD5K2L")
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "Button"))).click()

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "bgImgContainer")))

        # Navigate to searches page
        driver.get("https://booking.dyme.earth/searches")

        while True:
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "custom-advance-table-body")))
            rows = driver.find_element(By.CLASS_NAME, "custom-advance-table-body").find_elements(By.TAG_NAME, "tr")

            stop_scraping = False

            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 7:
                    ts_str = tds[6].text.strip()
                    try:
                        ts = parse_web_timestamp(ts_str)
                    except Exception:
                        continue

                    if ts > cutoff_date:
                        data = {
                            "email": tds[0].text.strip(),
                            "customer_name": tds[1].text.strip(),
                            "searched_location": tds[2].text.strip(),
                            "from_date": tds[3].text.strip(),
                            "to_date": tds[4].text.strip(),
                            "type": tds[5].text.strip(),
                            "timestamp": ts_str,
                        }
                        filtered_data.append(data)
                    else:
                        stop_scraping = True
                        break

            if stop_scraping:
                break

            # Try clicking the last pagination button
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                pagination_buttons = driver.find_elements(By.CLASS_NAME, "custom-pagination-btn")
                if pagination_buttons:
                    pagination_buttons[-1].click()
                    time.sleep(2)
                else:
                    break
            except:
                break

    finally:
        driver.quit()

    return filtered_data