import os
import time
import json
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, jsonify

# Load environment variables
dotenv_path = os.getenv('DOTENV_PATH', '.env')
load_dotenv(dotenv_path)

# Get credentials
website_url = os.getenv("WEBSITE_URL")
username = os.getenv("USER_NAME")
password = os.getenv("PASSWORD")
port = int(os.getenv("PORT", 5000))
sleep = int(os.getenv("SLEEP", 5))

# Flask app setup
app = Flask(__name__)

#disable Flask's logging
import logging
startup_log = logging.getLogger('werkzeug')
startup_log.disabled = True  # Disable startup logs

@app.before_request
def enable_request_logging():
    startup_log.disabled = False  # Re-enable logging for requests

def scrape_smart_oil_gauge():
    # Set up Chromium options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without GUI
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--v=1")
    service = Service('/usr/bin/chromedriver')
    
    # Access website
    driver = webdriver.Chrome(service=service, options=chrome_options)    
    driver.get(website_url)

    # Login
    driver.find_element(By.NAME, "username").send_keys(username)
    password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "inputPassword")))
    password_field.send_keys(password)
    login_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))
    login_button.click()
    
    # Wait for data to load
    time.sleep(sleep)

    # Check if the login is successful by looking for an element only visible after login
    try:
        level_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "ts_level")))
        days_to_quarter_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "ts_days_to_low")))
        battery_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "ts_battery")))

        # Scrape the required elements
        level = level_element.find_element(By.CLASS_NAME, "ts_col_val").text.split('/')[0].strip()
        days_to_quarter = days_to_quarter_element.find_element(By.CLASS_NAME, "ts_col_val").text.strip()
        battery = battery_element.find_element(By.CLASS_NAME, "ts_col_val").text.strip()
        
        scraped_data = {
            "level": level,
            "days_to_quarter": days_to_quarter,
            "battery": battery
        }
    except Exception as e:
        driver.quit()
        return {"error": "Login failed or elements not found", "message": str(e)}

    driver.quit()
    return scraped_data

@app.route('/data', methods=['GET'])
def get_data():
    try:
        data = scrape_smart_oil_gauge()
        return jsonify({"scrapped_data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    host = "0.0.0.0"
    print(f"Smart Oil Gauge scraper running at http://{host}:{port}")
    app.run(debug=False, host=host, port=port)
