# Use official Python image from DockerHub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the necessary files into the container
COPY scraper.py . 
COPY requirements.txt .
COPY .env .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add Google Chrome and Chromedriver
RUN apt-get update && apt-get install -y wget gnupg unzip \
    && wget -qO- https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && wget -N https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.35/linux64/chromedriver-linux64.zip \
    && unzip chromedriver-linux64.zip -d /usr/bin \
    && cp /usr/bin/chromedriver-linux64/chromedriver /usr/bin \
    && chmod +x /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver-linux64/chromedriver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Flask
ENV FLASK_APP=scraper.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Expose port 5000 to the outside world
EXPOSE 5000

# Run the Flask app
CMD ["python", "scraper.py"]

