# Web Scraper

This project was created with chatgpt. The python script scrapes data from a specific URL app.smartoilgauge.com. 
The URL, Username and password are configurable with a .env file. The script creates an api on port 5000 that will trigger the scrap and be able to pull the data from. 
This can be run directly on a linux computer or as a docker image --> [https://hub.docker.com/repository/docker/compukid/smartoilgauge-scraper/general](url)

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/your-repository-name.git
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up a `.env` file with the following variables:
   ```text
   WEBSITE_URL=https://url.com/page
   USER_NAME=your_username
   PASSWORD=your_password
   ```

4. Run the scraper:
   ```bash
   python scraper.py
   ```

## License

MIT
