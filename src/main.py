import click
import asyncio
import time
from utils import ErrorCounter
from data_fetcher import CryptoDataFetcher
from datetime import datetime, timedelta
from logger import *
from config import CONCURRENT_REQUESTS, REQUEST_DELAY

setup_logging()

@click.group()
def cli():
    """Command group for the CLI application"""
    pass

@cli.command() # Subcommand for fetching a single day's data
@click.option("--date", required=True, help="Date in ISO8601 format (e.g., 2017-12-30)")
@click.option("--coin", required=True, help="Coin identifier (e.g., bitcoin)")
@click.option("--load-to-db", is_flag=True, help="Load data to database")
def fetch(date, coin, load_to_db):
    """Fetches and saves cryptocurrency data for a specific date"""
    try:
        datetime.strptime(date, "%Y-%m-%d") # Validate the date format
    except ValueError:
        raise click.BadParameter("The date must be in ISO8601 format (e.g., 2017-12-30)")

    # Setup error tracking and fetching logic
    error_counter = ErrorCounter()
    fetcher = CryptoDataFetcher(coin, date, error_counter, load_to_db)
    asyncio.run(fetcher.fetch_data())
    error_counter.print_summary()

@cli.command() # Subcommand for fetching data over a date range
@click.option("--start-date", required=True, help="Start date in ISO8601 format (e.g., 2017-12-01)")
@click.option("--end-date", required=True, help="End date in ISO8601 format (e.g., 2017-12-30)")
@click.option("--coin", required=True, help="Coin identifier (e.g., bitcoin)")
@click.option("--concurrent", is_flag=True, default=False, help="Enable concurrent fetching")
@click.option("--load-to-db", is_flag=True, help="Load data to database")
def bulk_fetch(start_date, end_date, coin, concurrent, load_to_db):
    """Fetches and saves cryptocurrency data over a range of dates."""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise click.BadParameter("The dates must be in ISO8601 format (e.g., 2017-12-01)")

    error_counter = ErrorCounter()
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    all_dates = [start + timedelta(days=x) for x in range(0, (end - start).days + 1)]
    total_dates = len(all_dates)
    processed_dates = 0
    
    async def _process_batch(date_batch):
        """Asynchronous function to process a batch of dates concurrently"""
        tasks = []
        nonlocal processed_dates
        for date in date_batch:
            async with semaphore:
                fetcher = CryptoDataFetcher(coin, date.strftime("%Y-%m-%d"), error_counter, load_to_db)
                tasks.append(fetcher.fetch_data())  # Use the existing retry logic in fetch_data
                if not concurrent:
                    await asyncio.sleep(REQUEST_DELAY)
        results = await asyncio.gather(*tasks)
        processed_dates += len(results)
        logging.info(f"Progress: {processed_dates}/{total_dates} dates processed")

    if concurrent:
        batch_size = CONCURRENT_REQUESTS  # Adjust batch size if needed
        for i in range(0, len(all_dates), batch_size):
            batch = all_dates[i : i + batch_size]
            asyncio.run(_process_batch(batch))
    else:
        for date in all_dates:
            fetcher = CryptoDataFetcher(coin, date.strftime("%Y-%m-%d"), error_counter, load_to_db)
            asyncio.run(fetcher.fetch_data())  # Use the existing retry logic in fetch_data
            time.sleep(REQUEST_DELAY)  
    error_counter.print_summary()

if __name__ == "__main__":
    cli()