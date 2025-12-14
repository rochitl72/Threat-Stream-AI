#!/usr/bin/env python3
"""
Script to create Kafka topics in Confluent Cloud
"""

from confluent_kafka.admin import AdminClient, NewTopic
from src.config import Config
from src.utils.logger import setup_logger

logger = setup_logger("create_topics")


def create_topics():
    """Create all required Kafka topics"""
    
    # Get Kafka config
    kafka_config = Config.get_kafka_config()
    
    # Create admin client
    admin_client = AdminClient(kafka_config)
    
    # Define topics
    topics = [
        NewTopic(Config.TOPIC_TELEMETRY_RAW, num_partitions=3, replication_factor=3),
        NewTopic(Config.TOPIC_CODE_SAMPLES_RAW, num_partitions=3, replication_factor=3),
        NewTopic(Config.TOPIC_DARKWEB_FEEDS_RAW, num_partitions=3, replication_factor=3),
        NewTopic(Config.TOPIC_THREAT_PROFILES, num_partitions=3, replication_factor=3),
        NewTopic(Config.TOPIC_MITRE_ATTACK_MAPPINGS, num_partitions=3, replication_factor=3),
        NewTopic(Config.TOPIC_THREAT_ALERTS, num_partitions=3, replication_factor=3),
    ]
    
    # Create topics
    logger.info("Creating Kafka topics...")
    futures = admin_client.create_topics(topics)
    
    # Wait for results
    for topic, future in futures.items():
        try:
            future.result()  # Wait for topic creation
            logger.info(f"✅ Topic '{topic}' created successfully")
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info(f"ℹ️  Topic '{topic}' already exists")
            else:
                logger.error(f"❌ Failed to create topic '{topic}': {e}")


if __name__ == "__main__":
    create_topics()


