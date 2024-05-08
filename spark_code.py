from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, DoubleType

# create SparkSession
spark = SparkSession.builder \
    .appName("CoinDataStreaming") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0") \
    .getOrCreate()
    
kafka_bootstrap_servers = "localhost:9092"
kafka_topic_name = "coin_data"

# read data from kafka
kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", kafka_topic_name) \
    .load()

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

# json to df
parsed_df = kafka_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", schema).alias("data")) \
    .select("data.*")

# structured stream
stream = parsed_df \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

# stream
stream.awaitTermination()
