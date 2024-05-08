import requests
import json
import time
import os

from kafka import KafkaProducer
from dotenv import load_dotenv

#kafka cfg
kafka_bootstrap_servers = 'localhost:9092'
kafka_topic_name = 'coin_data'

#create producer
producer = KafkaProducer(bootstrap_servers = kafka_bootstrap_servers,
                         value_serializer = lambda x:json.dumps(x).encode('utf-8'))

#GET api key from .env file
load_dotenv()
API_KEY = os.getenv("CMP_API_KEY")
API_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
coin_info = {
    1: {'slug': 'bitcoin', 'symbol': 'BTC'},
    1027: {'slug': 'ethereum', 'symbol': 'ETH'},
    1839: {'slug': 'bnb', 'symbol': 'BNB'},
    5426: {'slug': 'solana', 'symbol': 'SOL'},
    52: {'slug': 'ripple', 'symbol': 'XRP'},
    74: {'slug': 'dogecoin', 'symbol': 'DOGE'}
}


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
    response = requests.get(API_URL,headers=headers,params=parameters)
    data = response.json()
    
    if 'status' in data and 'error_message' in data['status'] and data['status']['error_message'] is not None:
        error_code = data['status']['error_code']
        error_message = data['status']['error_message']
        print(f"There is a error! Error code: {error_code}, Error message: {error_message}")
        return None
    
    coin_instant_data = {}
    timestamp = data['status']['timestamp']
    for coin in data['data']:
        if coin['id'] in coin_info:
            coin_id = coin['id']
            coin_slug = coin_info[coin_id]['slug']
            coin_symbol = coin_info[coin_id]['symbol']
            coin_price = coin['quote']['USD']['price']
            coin_instant_data[coin_slug] = {'symbol': coin_symbol, 'price': coin_price, 'timestamp': timestamp}
            
    return coin_instant_data

while True:
    coin_data = fetch_coin_prices()
    producer.send(kafka_topic_name,value=coin_data)
    time.sleep(10) #every 10 second

