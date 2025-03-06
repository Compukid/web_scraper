# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install necessary dependencies for running Chrome in headless mode
RUN apt-get update && \
    apt-get install -y wget gnupg2 ca-certificates curl unzip && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    DISTRO=$(lsb_release -c | awk '{print $2}') && \
    echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" | tee -a /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get clean

# Set display to dummy value so Chrome doesn't need a GUI
ENV DISPLAY=:99

# Run the application
CMD ["python", "scraper.py"]
