from apify import Actor
import asyncio
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
    if ts is None:
        return datetime.now(timezone.utc)
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)


def scrape_dyme_searches(start_date_str):
    cutoff_date = parse_api_timestamp(start_date_str)
    print(f"Starting scrape with cutoff date: {cutoff_date}")

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
        print("Loaded login page")

        # Login process
        email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]')))
        email_input.send_keys("chloe@dyme.travel")
        print("Entered email")
        
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "Button"))).click()
        print("Clicked login button 1")

        password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]')))
        password_input.send_keys("zRvyy89wduD5K2L")
        print("Entered password")
        
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "Button"))).click()
        print("Clicked login button 2")

        # Wait for SSO redirect to complete
        print("Waiting for SSO redirect...")
        try:
            wait.until(lambda d: "login" not in d.current_url.lower())
            print(f"Redirected to: {driver.current_url}")
        except:
            print("No redirect detected")
        
        # Wait for SSO token processing
        if 'sso?token=' in driver.current_url:
            print("SSO token detected, waiting for processing...")
            time.sleep(5)
            
            try:
                wait.until(lambda d: 'sso?token=' not in d.current_url)
                print(f"SSO processed, now at: {driver.current_url}")
            except:
                print("SSO redirect may still be processing")
        
        time.sleep(3)
        print(f"Final URL before navigation: {driver.current_url}")

        # Navigate to searches page
        driver.get("https://booking.dyme.earth/searches")
        print("Navigated to searches page")
        time.sleep(5)

        # Wait for the table to load
        print("Waiting for table to load...")
        try:
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "custom-advance-table-body")))
            print("Table loaded successfully")
        except:
            print("ERROR: Table not found. Debugging...")
            driver.save_screenshot("searches_page_error.png")
            print(f"Current URL: {driver.current_url}")
            print(f"Page title: {driver.title}")
            
            page_text = driver.find_element(By.TAG_NAME, "body").text
            print(f"Page content preview: {page_text[:500]}")
            
            raise Exception("Table element 'custom-advance-table-body' not found on searches page")

        # Scrape the data
        while True:
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "custom-advance-table-body")))
            rows = driver.find_element(By.CLASS_NAME, "custom-advance-table-body").find_elements(By.TAG_NAME, "tr")
            
            print(f"Processing {len(rows)} rows on current page")

            stop_scraping = False

            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 7:
                    ts_str = tds[6].text.strip()
                    try:
                        ts = parse_web_timestamp(ts_str)
                    except Exception as e:
                        print(f"Failed to parse timestamp: {ts_str}, error: {e}")
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
                        print(f"Added record: {data['customer_name']} - {ts_str}")
                    else:
                        print(f"Reached cutoff date at: {ts_str}")
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
                    print("Clicking next page button")
                    pagination_buttons[-1].click()
                    time.sleep(3)
                else:
                    print("No more pagination buttons found")
                    break
            except Exception as e:
                print(f"Pagination failed: {e}")
                break

    except Exception as e:
        print(f"Error during scraping: {e}")
        raise
    finally:
        driver.quit()

    print(f"Scraping complete. Found {len(filtered_data)} records")
    return filtered_data


async def main():
    async with Actor:
        input_data = await Actor.get_input() or {}
        start_date = input_data.get("start_date")
        
        if not start_date:
            start_date = "2025-10-03T00:00:00.000Z"

        # Run scraping in a separate thread
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, scrape_dyme_searches, start_date)

        # Push filtered results to dataset
        if result:
            await Actor.push_data(result)
        
        Actor.log.info(f"Successfully scraped {len(result)} records")


if __name__ == "__main__":
    asyncio.run(main())