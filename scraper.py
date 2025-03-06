import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
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

def scrape_data():
    # Launch Chrome
    driver = webdriver.Chrome()
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
        # Scrape the required elements
        level = driver.find_element(By.CLASS_NAME, "ts_level").find_element(By.CLASS_NAME, "ts_col_val").text.split('/')[0].strip()
        days_to_quarter = driver.find_element(By.CLASS_NAME, "ts_days_to_low").find_element(By.CLASS_NAME, "ts_col_val").text.strip()
        battery = driver.find_element(By.CLASS_NAME, "ts_battery").find_element(By.CLASS_NAME, "ts_col_val").text.strip()
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
	app.run(debug=True, host='0.0.0.0', port=5000)

