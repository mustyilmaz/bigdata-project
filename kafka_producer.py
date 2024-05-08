import requests
import json
import time
import os

from kafka import KafkaProducer
from dotenv import load_dotenv


#GET api key from .env file
load_dotenv()
API_KEY = os.getenv("CMP_API_KEY")
print(API_KEY)


