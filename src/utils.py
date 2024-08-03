import asyncio
import aiohttp
import backoff
import logging
from config import MAX_RETRIES

@backoff.on_exception(backoff.expo, (aiohttp.ClientError,), max_tries=MAX_RETRIES)
async def fetch_with_retry(session, url):
    """Fetches data from the given URL with exponential backoff retry"""
    async with session.get(url) as response:
        if response.status == 429: # Rate limit exceeded
            retry_after = response.headers.get("Retry-After", 1)
            logging.warning(f"Rate limited, retrying after {retry_after} seconds")
            await asyncio.sleep(float(retry_after))
            return await fetch_with_retry(session, url) # Retry
        response.raise_for_status() # Raise exception for other HTTP errors
        return await response.json()

class ErrorCounter:
    """Simple counter for tracking successes and errors during data fetching."""
    def __init__(self):
        self.errors = 0
        self.successes = 0
        self.failed_requests = []

    def increment_error(self, coin, date):
        self.errors += 1
        self.failed_requests.append((coin, date))

    def increment_success(self):
        self.successes += 1

    def print_summary(self):
        print(f"Successes: {self.successes}/{self.successes + self.errors}")
