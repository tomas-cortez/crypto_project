import psycopg2
import json
import logging
from datetime import datetime
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

class Database:
    """Handles interactions with the PostgreSQL database for storing cryptocurrency data"""
    @staticmethod
    def load_data_to_db(coin, date, data):
        """Loads cryptocurrency data into the database
        
        Handles both daily coin data and aggregated monthly min/max prices
        """
        conn = psycopg2.connect( # Establish connection
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # Prepare data for insertion (coin, date, price, full json data)
        coin_data = (
            coin,
            datetime.strptime(date, "%Y-%m-%d").date(),
            data["market_data"]["current_price"]["usd"],
            json.dumps(data)
        )
        
        # Insert or ignore if data for this coin/date already exists
        cursor.execute(
            """
            INSERT INTO coin_data (coin, date, price, json)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (coin, date) DO NOTHING
            """,
            coin_data
        )
        
        # Extract year, month, and price for monthly aggregation
        year = coin_data[1].year
        month = coin_data[1].month
        price = coin_data[2]
        
        # Insert or update monthly min/max prices
        cursor.execute(
            """
            INSERT INTO coin_month_data (coin, year, month, min_price, max_price)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (coin, year, month) DO UPDATE SET
                min_price = LEAST(coin_month_data.min_price, EXCLUDED.min_price),
                max_price = GREATEST(coin_month_data.max_price, EXCLUDED.max_price)
            """,
            (coin, year, month, price, price)
        )

        conn.commit() # Save changes
        cursor.close()
        conn.close()
        logging.info(f"Data for {coin} on {date} loaded to database")
