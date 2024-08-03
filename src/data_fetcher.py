import aiohttp
import json
import logging
import os
from datetime import datetime
from utils import fetch_with_retry
from database import Database
from config import API_BASE_URL

class CryptoDataFetcher:
    """Fetches historical cryptocurrency data from an API and optionally saves to file/DB"""
    def __init__(self, coin, date, error_counter, load_to_db=False):
        self.coin = coin
        self.date = date
        self.error_counter = error_counter
        self.load_to_db = load_to_db

    async def fetch_data(self):
        formatted_date = datetime.strptime(self.date, "%Y-%m-%d").strftime("%d-%m-%Y") # API's expected format
        url = f"{API_BASE_URL}/coins/{self.coin}/history?date={formatted_date}"
        async with aiohttp.ClientSession() as session: # Create an HTTP session
            try:
                data = await fetch_with_retry(session, url)  # get data
                self.save_to_file(data)  # save to file
                
                if self.load_to_db: # optional database loading
                    Database.load_data_to_db(self.coin, self.date, data)
                self.error_counter.increment_success() # Track successful fetch
                
            except aiohttp.ClientResponseError as e:
                logging.error(f"Error obtaining data for {self.coin} on {self.date}: {e}") # Specific API error handling
                self.error_counter.increment_error(self.coin, self.date)
                
            except Exception as e:  # Catch-all for unexpected errors
                logging.error(f"Unexpected error: {e}")
                self.error_counter.increment_error(self.coin, self.date)

    def save_to_file(self, data):
        """Saves fetched JSON data to a file in the specified directory."""
        file_name = f"../data/coins/{self.coin}/{self.date}.json" # ../ is relative to script location
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, "w") as file:
            json.dump(data, file)
        logging.info(f"Data for {self.coin} on {self.date} saved to {file_name}")
