import os
import time
import json
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
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


    elements = os.getenv('SCRAPER_ELEMENTS', '{}')
    elements = json.loads(elements)
    
    # Set up Chromium options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without GUI
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--v=1")
    #chrome_options.binary_location = "/usr/bin/chromium-browser"
    service = Service('/usr/bin/chromedriver')
    
    # Launch Chromium
    #driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(website_url)

    # Log in
    if username and password:
        print("Attempting login")
        driver.find_element(By.NAME, "username").send_keys(username)
        password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "inputPassword")))
        password_field.send_keys(password)
        login_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))
        login_button.click()
    else:
        print("Skipping login")

    #Wait for page to load
    sleep = int(os.getenv('SLEEP', 3))
    time.sleep(sleep)
    
    
    scraped_data = {}
    
    # Loop through elements and scrape data
    for elem in elements.get('elements', []):
        method = elem.get('method', '').lower()
        value = elem.get('value', '')
        name = elem.get('name', '')

        try:
            if method in ['class_name', 'tag_name']:
                locator = (By.CLASS_NAME, value) if method == 'class_name' else (By.TAG_NAME, value)
                element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

                scraped_data[name] = element.text
            else:
                scraped_data[name] = "Unsupported method"
        except Exception as e:
            scraped_data[name] = f"Error: {str(e)}"

    driver.quit()
    
    result = {
    
        "website": website_url,
        "scrapped_data": scraped_data
    }

    return jsonify(result)

@app.route('/data', methods=['GET'])
def get_data():
    data = scrape_data()
    return scrape_data()
    
port = int(os.getenv('PORT', 5000))

if __name__ == '__main__':
    host = "0.0.0.0"
    print(f"Web scraper API started. Listening on http://{host}:{port}")
    app.run(debug=False, host=host, port=port)
