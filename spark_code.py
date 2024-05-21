from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, DoubleType
import requests
import json
import os 

python_path = "/Users/mustafayilmaz/opt/anaconda3/bin/python3.9"
os.environ["PYSPARK_PYTHON"] = python_path
os.environ["PYSPARK_DRIVER_PYTHON"] = python_path

# create SparkSession
spark = SparkSession.builder \
    .appName("CoinDataStreaming") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0") \
    .getOrCreate()

kafka_bootstrap_servers = "localhost:9092"
kafka_topic_name = "coin_data"

# Flask API URL
flask_api_url = "http://127.0.0.1:5000/update_data"

# schema
schema = StructType() \
    .add("timestamp", StringType()) \
    .add("bitcoin", StructType()
         .add("symbol", StringType())
         .add("price", DoubleType())) \
    .add("ethereum", StructType()
         .add("symbol", StringType())
         .add("price", DoubleType())) \
    .add("bnb", StructType()
         .add("symbol", StringType())
         .add("price", DoubleType())) \
    .add("solana", StructType()
         .add("symbol", StringType())
         .add("price", DoubleType())) \
    .add("ripple", StructType()
         .add("symbol", StringType())
         .add("price", DoubleType())) \
    .add("dogecoin", StructType()
         .add("symbol", StringType())
         .add("price", DoubleType()))

# read data from kafka
kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", kafka_topic_name) \
    .load()

# json to df
parsed_df = kafka_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", schema).alias("data")) \
    .select("data.*")

# Send data to Flask API
def send_to_flask(df, epoch_id):
    data = df.toJSON().map(lambda j: json.loads(j)).collect()
    for entry in data:
        response = requests.post(flask_api_url, json=entry)
        if response.status_code == 200:
            print(f"Successfully sent data to Flask API: {entry}")
        else:
            print(f"Failed to send data to Flask API: {entry}")

query = parsed_df.writeStream.foreachBatch(send_to_flask).start()

query.awaitTermination()
