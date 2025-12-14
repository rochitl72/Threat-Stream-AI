"""
Kafka utility functions
"""

from confluent_kafka import Producer, Consumer
from typing import Optional
from src.config import Config


def get_kafka_producer(config_override: Optional[dict] = None) -> Producer:
    """
    Get a configured Kafka producer
    
    Args:
        config_override: Optional dictionary to override default config
        
    Returns:
        Configured Kafka Producer instance
    """
    config = Config.get_kafka_config()
    if config_override:
        config.update(config_override)
    
    return Producer(config)


def get_kafka_consumer(
    group_id: str,
    topics: list,
    config_override: Optional[dict] = None
) -> Consumer:
    """
    Get a configured Kafka consumer
    
    Args:
        group_id: Consumer group ID
        topics: List of topics to subscribe to
        config_override: Optional dictionary to override default config
        
    Returns:
        Configured Kafka Consumer instance
    """
    config = Config.get_kafka_config()
    config["group.id"] = group_id
    config["auto.offset.reset"] = "earliest"
    
    if config_override:
        config.update(config_override)
    
    consumer = Consumer(config)
    consumer.subscribe(topics)
    
    return consumer


def delivery_callback(err, msg):
    """Callback for message delivery confirmation"""
    if err:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


