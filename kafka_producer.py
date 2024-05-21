import requests
import json
import time
import os
import logging
from kafka import KafkaProducer
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MongoDB cfg
client = MongoClient('localhost', 27017)
db = client['crypto_db']
collection = db['crypto_prices']

# Kafka cfg
kafka_bootstrap_servers = 'localhost:9092'
kafka_topic_name = 'coin_data'

# Create producer
producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers,
                         value_serializer=lambda x: json.dumps(x).encode('utf-8'))

# GET API key from .env file
load_dotenv()
API_KEY = os.getenv("CMP_API_KEY")
API_URL_LATEST = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
API_URL_HISTORICAL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/historical'

coin_info = {
    1: {'slug': 'bitcoin', 'symbol': 'BTC'},
    1027: {'slug': 'ethereum', 'symbol': 'ETH'},
    1839: {'slug': 'bnb', 'symbol': 'BNB'},
    5426: {'slug': 'solana', 'symbol': 'SOL'},
    52: {'slug': 'ripple', 'symbol': 'XRP'},
    74: {'slug': 'dogecoin', 'symbol': 'DOGE'}
}

def fetch_historical_data():
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=245)
    
    timestamps_data = {} 

    def fetch_data(coin_id, coin):
        parameters = {
            'id': coin_id,
            'time_start': int(start_time.timestamp()),
            'time_end': int(end_time.timestamp()),
            'interval': '5m' 
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': API_KEY,
        }
        response = requests.get(API_URL_HISTORICAL, headers=headers, params=parameters)
        return response.json(), coin

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(fetch_data, coin_id, coin) for coin_id, coin in coin_info.items()]
        for future in as_completed(futures):
            try:
                data, coin = future.result()
                if 'status' in data and data['status']['error_message']:
                    logging.error(f"Error fetching data for {coin['slug']}: {data['status']['error_message']}")
                    continue
                for quote in data['data']['quotes']:
                    timestamp = quote['timestamp']
                    price = quote['quote']['USD']['price']
                    if timestamp not in timestamps_data:
                        timestamps_data[timestamp] = {'timestamp': timestamp}
                    timestamps_data[timestamp][coin['slug']] = {'symbol': coin['symbol'], 'price': price}
            except Exception as e:
                logging.error(f"Exception occurred: {e}")

    historical_data = list(timestamps_data.values())
    collection.insert_many(historical_data)

def fetch_coin_prices():
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY,
    }
    parameters = {
        'start': '1',
        'limit': '10',
        'convert': 'USD'
    }
    response = requests.get(API_URL_LATEST, headers=headers, params=parameters)
    data = response.json()
    
    if 'status' in data and data['status']['error_message']:
        logging.error(f"Error fetching latest data: {data['status']['error_message']}")
        return None
    
    coin_instant_data = {}
    timestamp = data['status']['timestamp']
    coin_instant_data['timestamp'] = timestamp
    for coin in data['data']:
        if coin['id'] in coin_info:
            coin_slug = coin_info[coin['id']]['slug']
            coin_symbol = coin_info[coin['id']]['symbol']
            coin_price = coin['quote']['USD']['price']
            coin_instant_data[coin_slug] = {'symbol': coin_symbol, 'price': coin_price}
    
    return coin_instant_data


def update_mongo(coin_data):
    if coin_data:
        if collection.count_documents({}) >= 50:
            oldest = list(collection.find().sort("timestamp", 1).limit(1))
            if oldest:
                collection.delete_one({"_id": oldest[0]['_id']})
        collection.insert_one(coin_data)


# Clear collection before starting
collection.delete_many({})
# Fetch historical data once
fetch_historical_data()

# Continuously fetch latest data and update MongoDB
while True:
    coin_data = fetch_coin_prices()
    if coin_data:
        logging.info(f"Fetched latest coin data: {coin_data}")
        producer.send(kafka_topic_name, value=coin_data)
        update_mongo(coin_data)
    time.sleep(300)  # every 300 seconds / 5 minutes
