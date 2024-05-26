from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, unix_timestamp
from pyspark.sql.types import StructType, StringType, DoubleType
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler
from pymongo import MongoClient
from datetime import datetime, timezone
import pytz
import requests
import json
import os

python_path = "/Users/mustafayilmaz/opt/anaconda3/bin/python3.9"
os.environ["PYSPARK_PYTHON"] = python_path
os.environ["PYSPARK_DRIVER_PYTHON"] = python_path

# Create SparkSession
spark = SparkSession.builder \
    .appName("CoinDataStreaming") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0") \
    .getOrCreate()

# Kafka configuration
kafka_bootstrap_servers = "localhost:9092"
kafka_topic_name = "coin_data"

# MongoDB configuration
mongo_client = MongoClient('localhost', 27017)
mongo_db = mongo_client['crypto_db']
mongo_collection = mongo_db['crypto_prices']

# Flask API URL
flask_api_url = "http://127.0.0.1:5000/update_data"
prediction_api_url = "http://127.0.0.1:5000/update_prediction"

# Schema
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

# Read data from Kafka
kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", kafka_topic_name) \
    .load()

# Convert JSON string to DataFrame
parsed_df = kafka_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", schema).alias("data")) \
    .select("data.*")

# Function to train model and predict
def train_and_predict(df):
    # Convert timestamp to numeric format
    df = df.withColumn("timestamp", unix_timestamp(col("timestamp"), "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'").cast(DoubleType()))
    predictions = {}
    try:
        distinct_timestamps = df.select("timestamp").distinct().orderBy("timestamp").collect()
        if not distinct_timestamps:
            raise ValueError("No distinct timestamps found in the dataframe")

        current_time = distinct_timestamps[-1][0]
        future_time = current_time + 300
        
        tz = pytz.timezone('Etc/GMT-3')  # Note: 'Etc/GMT-3' is used for GMT+3
        future_time_utc = datetime.fromtimestamp(future_time, tz=timezone.utc).astimezone(tz)
        future_time_formatted = future_time_utc.strftime('%Y-%m-%dT%H:%M:%SZ')

        predictions["timestamp"] = future_time_formatted

        for coin in ["bitcoin", "ethereum", "bnb", "solana", "ripple", "dogecoin"]:
            coin_df = df.select("timestamp", f"{coin}.price").dropna()
            if coin_df.count() == 0:
                raise ValueError(f"No data available for {coin}")

            coin_df = coin_df.withColumnRenamed(f"{coin}.price", "price")
            print(f"coin_df content for {coin}:")
            coin_df.show()

            # Prepare data for model
            assembler = VectorAssembler(inputCols=["timestamp"], outputCol="features")
            train_data = assembler.transform(coin_df)

            # Train model
            lr = LinearRegression(featuresCol='features', labelCol='price')
            model = lr.fit(train_data)

            # Make predictions
            future_df = spark.createDataFrame([(future_time,)], ["timestamp"])
            future_data = assembler.transform(future_df)

            prediction = model.transform(future_data).select("prediction").collect()[0][0]
            predictions[coin] = {"price": prediction}
    except Exception as e:
        print(f"Error in train_and_predict: {e}")
        predictions = {}
    
    return predictions

# Send data to Flask API
def send_to_flask(df, epoch_id):
    try:
        data = df.toJSON().map(lambda j: json.loads(j)).collect()
        for entry in data:
            response = requests.post(flask_api_url, json=entry)
            if response.status_code == 200:
                print(f"Successfully sent data to Flask API: {entry}")
            else:
                print(f"Failed to send data to Flask API: {entry}")

        # Convert MongoDB data to DataFrame
        mongo_data = mongo_collection.find()
        mongo_df = spark.createDataFrame(mongo_data, schema=schema)
        # Get predictions
        predictions = train_and_predict(mongo_df)
        prediction_response = requests.post(prediction_api_url, json=predictions)
        if prediction_response.status_code == 200:
            print(f"Successfully sent predictions to Flask API: {predictions}")
        else:
            print(f"Failed to send predictions to Flask API: {predictions}")
    except Exception as e:
        print(f"Error in send_to_flask: {e}")

# Write stream to Flask
query = parsed_df.writeStream.foreachBatch(send_to_flask).start()

query.awaitTermination()
