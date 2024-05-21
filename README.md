# Big Data Project

## IMPORTANT
Before starting the installation process,ensure that Java is installed on your system by running the following command in your Terminal:
```bash
    java -version
```
If not, download and install it from the [official Java website](https://www.oracle.com/java/technologies/javase-jdk11-downloads.html) according to your operating system.

## Apache Kafka Installation (Mac)

Follow the instructions at [this link](https://www.conduktor.io/kafka/how-to-install-apache-kafka-on-mac/) to install Kafka on Mac.

1. Open Terminal and run the command:
    ```bash
    nano ~/.zshrc
    ```

2. Add the following line:
    ```bash
    export PATH="$PATH:/Users/mustafayilmaz/Desktop/bigdata/kafka_2.13-3.6.2/bin"
    ```

3. To save the changes, press `CTRL+X`, then `Y` to confirm.

4. Update the `.zshrc` file by running the following command in the terminal:
    ```bash
    source ~/.zshrc
    ```
5. Now you can proceed with starting Kafka and creating a topic.

## Starting Kafka and Creating a Topic

1. **Starting Zookeeper:** Run the following command to start Zookeeper:
    ```bash
    zookeeper-server-start.sh /Users/mustafayilmaz/Desktop/bigdata/kafka_2.13-3.6.2/config/zookeeper.properties
    ```

2. **Starting Kafka:** Run the following command to start Kafka:
    ```bash
    kafka-server-start.sh /Users/mustafayilmaz/Desktop/bigdata/kafka_2.13-3.6.2/config/server.properties
    ```

3. **Creating a Topic:** To create a topic named `coin_data`, use the following command:
    ```bash
    kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic coin_data
    ```

## Apache Spark Installation (with pip)

1. **Install Apache Spark:** Install Apache Spark using pip by running the following command in your Terminal:
    ```bash
    pip install pyspark
    ```

2. **Start Using Apache Spark:** Once the installation is complete, you can start using Apache Spark in your Python environment.

## Kafka-Python Installation

1. **Install Kafka-Python:** To interact with Kafka from Python, you can use the kafka-python library. Install it using pip by running the following command in your Terminal:
    ```bash
    pip install kafka-python
    ```

2. **Start Using Kafka-Python:** Once the installation is complete, you can start using Kafka-Python to produce and consume messages from Kafka topics in your Python scripts.

