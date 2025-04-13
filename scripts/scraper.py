import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config.logging_config import setup_logging
from scripts.postgresdb import PostgresConnector

class OfferSearch():
    def __init__(self, data: str, consumer):
        self.subject = data['subject']
        self.webhook_url = data['webhook_url']

        self.url = f"https://www.vinted.fr/catalog?search_text={self.subject}&order=newest_first"
        
        self.logger = setup_logging()
        self.consumer = consumer

        self._original_listings = []
        self.postgresconn = PostgresConnector()

    def _create_embed(self, title, url, price, src):
        embed = {
            "title": title,
            "url": url,
            "color": 3447003,  # Blue
            "fields": [
                {"name": "💰 Price", "value": price, "inline": False}
            ],
            "image": {"url": src}
        }

        self.payload = {"embeds": [embed]}

    def _setup_selenium_session(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless=new")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--remote-debugging-port=9222")

        self.service = Service("/usr/bin/chromedriver")

    def _start_selenium_session(self):
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)

    def _close_session(self):
        self.driver.close()

    def _scrape_subject(self):
        try:
            self.driver.get(self.url)

            overlay_elements = WebDriverWait(self.driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.u-position-relative.u-min-height-none.u-flex-auto.new-item-box__image-container'))
            )

            listings = []

            for item in overlay_elements[0:3]:
                img_element = item.find_element(By.CSS_SELECTOR, 'img.web_ui__Image__content')
                src = img_element.get_attribute('src')

                listings.append(src)

                if src not in self._original_listings:
                    self._original_listings.append(src)
                    infos_element = item.find_element(By.CSS_SELECTOR, 'a.new-item-box__overlay.new-item-box__overlay--clickable')
                    data = infos_element.get_attribute('title').split(',')

                    title = data[0]
                    raw_price = next((data[i-1].strip() + "." + data[i].strip() for i in range(1, len(data)) if "€" in data[i]), None)
                    clean_price = raw_price.replace(" €", "").strip()
                    price = float(clean_price)

                    self.logger.info(f"raw_price: {raw_price}")
                    self.logger.info(f"clean_price: {clean_price}")
                    self.logger.info(f"price: {price}")

                    url = infos_element.get_attribute('href')

                    self._create_embed(title, url, raw_price, src)
                    requests.post(self.webhook_url, json=self.payload)
                    self.postgresconn.inject_offer(title, price, url, src) #injecter la nouvelle offre dans la db postgresql

            self._original_listings = listings
            self.consumer.poll(timeout=0)

        except Exception as e:
            self.logger.error(f"Error detected: {e}")

    def start_scraping(self):
        self.logger.info(f"Scraping starting for {self.subject}")
        
        self._setup_selenium_session()
        
        self._start_selenium_session()

        while True:
            try:
                self._scrape_subject()

            except Exception as e:
                self.logger.error(f"Error detected: {e}")
                
                self._close_session()
                self._start_selenium_session() #redémarrer la session selenium en cas d'erreur



if __name__ == "__main__":
    data = {
        #"subjects": ["hippodocus niv x", "simiabraz niv x", "dialga palkia niv x"],
        "subjects": ["carte pokemon"],
        "webhook_url": "https://discord.com/api/webhooks/1353569311205359686/Xs9e8bwVqUeR-CEsBct8CRSKqvAswN7Ea50rrpYVwsjL2iPFQkWVvocCANAx63n37NLV"
    }
    instance = OfferSearch(data, "consumer")
    instance.start_scraping()