import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


class Spider:
    def __init__(self, base_url=None, talkative=False):
        self.base_url = base_url
        self.session = requests.Session()
        self.memory = pd.DataFrame(columns=['url', 'content'])
        self.data_accumulator = []
        self.talkative = talkative
        self.accumulator_max_size = 10  # Adjust this value as needed

    def set_landing(self, base_url):
        self.base_url = base_url

    def get_response(self, url):
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def spidy_trip(self, url, depth=1):
        if depth == 0 or url in self.memory['url'].values:
            return

        response = self.get_response(url)
        if not response:
            return

        if self.talkative:
            print(f"Scraping: {url}")

        soup = BeautifulSoup(response.text, 'html.parser')
        self.data_accumulator.append({'url': url, 'content': soup.prettify()})

        if len(self.data_accumulator) >= self.accumulator_max_size:
            self.update_memory()

        threads = soup.find_all('a')

        if self.talkative:
            print(f"Found {len(threads)} threads at depth {depth}")

        for thread in threads:
            href = thread.get('href')
            if href:
                next_url = self.validate_url(href)
                self.spidy_trip(next_url, depth - 1)

    def update_memory(self):
        new_data = pd.DataFrame(self.data_accumulator)
        self.memory = pd.concat([self.memory, new_data], ignore_index=True)
        self.data_accumulator = []  # Reset the accumulator

    def validate_url(self, href):
        if href.startswith('http'):
            return href
        elif href.startswith('//'):
            return 'https:' + href
        elif href.startswith('/'):
            return f"{self.base_url}{href}"
        else:
            return f"{self.base_url}/{href}"

    def save_memory(self, file_name):
        self.update_memory()  # Ensure all accumulated data is added to memory before saving
        self.memory.to_csv(file_name, index=False)


def spidy_stroll():
    start_url = "https://apnews.com/"
    spider = Spider(talkative=True)
    spider.set_landing(start_url)
    spider.spidy_trip(start_url, depth=2)
    spider.save_memory('spider_memory.csv')


# Example usage
if __name__ == "__main__":
    last_stroll = pd.read_csv('spider_memory.csv')
    print(last_stroll.describe())
