# Big Data Project

This document outlines the steps required for the Big Data project.

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

## Starting Zookeeper

Run the following command to start Zookeeper:
```bash
zookeeper-server-start.sh /Users/mustafayilmaz/Desktop/bigdata/kafka_2.13-3.6.2/config zookeeper.properties
```
