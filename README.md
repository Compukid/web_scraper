# Web Scraper

This project scrapes data from a specific URL although you can try another site. 
the URL, Username and password are configurable, but in the first iteration the elements to scrape are hard coded at the moment and hope to fix it in the future.
script creates a api on port 5000 that will trigger the scrap and be able to pull the data from. 

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
