import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, jsonify

# Load environment variables
load_dotenv()

# Get credentials
website_url = os.getenv("WEBSITE_URL")
username = os.getenv("USER_NAME")
password = os.getenv("PASSWORD")

# Flask app setup
app = Flask(__name__)

#disable Flask's logging
import logging
startup_log = logging.getLogger('werkzeug')
startup_log.disabled = True  # Disable startup logs
#log.setLevel(logging.ERROR)

@app.before_request
def enable_request_logging():
    startup_log.disabled = False  # Re-enable logging for requests

def wait_for_element(driver, by, value, timeout=30, retries=3):
    for _ in range(retries):
        try:
            return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))
        except TimeoutException:
            print(f"Retrying to find {value}...")
            time.sleep(2)  # Short wait before retrying
    return None

def scrape_data():
    # Set up Chromium options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without GUI
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--v=1")
    chrome_options.binary_location = "/usr/bin/chromium-browser"

    # Launch Chromium
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(website_url)

    # Log in
    driver.find_element(By.NAME, "username").send_keys(username)
    password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "inputPassword")))
    password_field.send_keys(password)
    login_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))
    login_button.click()

    # Wait for the page to load (can adjust timing based on your page)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ts_days_to_low")))
    time.sleep(5)

    # Check if the login is successful by looking for an element only visible after login
    try:
        level_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "ts_level")))
        days_to_quarter_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "ts_days_to_low")))
        battery_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "ts_battery")))

        # Scrape the required elements
        level = level_element.find_element(By.CLASS_NAME, "ts_col_val").text.split('/')[0].strip()
        days_to_quarter = days_to_quarter_element.find_element(By.CLASS_NAME, "ts_col_val").text.strip()
        battery = battery_element.find_element(By.CLASS_NAME, "ts_col_val").text.strip()
    except Exception as e:
        driver.quit()
        return {"error": "Login failed or elements not found", "message": str(e)}

    driver.quit()

    return {
        "Level": level,
        "Days_to_Quarter": days_to_quarter,
        "Battery": battery
    }

@app.route('/data', methods=['GET'])
def get_data():
    data = scrape_data()
    return jsonify(data)

if __name__ == '__main__':
    host = "0.0.0.0"
    port = 5000
    print(f"Web scraper API started. Listening on http://{host}:{port}")
    app.run(debug=False, host=host, port=port)
