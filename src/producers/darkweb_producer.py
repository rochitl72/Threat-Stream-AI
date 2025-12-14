"""
Dark Web Feed Producer
Produces dark web feed data to Kafka
"""

import json
from typing import Dict, Any, List
from confluent_kafka import Producer

from src.config import Config
from src.models.threat import DarkWebFeed
from src.utils.kafka_utils import get_kafka_producer, delivery_callback
from src.utils.logger import setup_logger

logger = setup_logger("darkweb_producer")


class DarkWebProducer:
    """Produces dark web feed data to Kafka"""
    
    def __init__(self):
        """Initialize dark web producer"""
        self.producer = get_kafka_producer()
        self.topic = Config.TOPIC_DARKWEB_FEEDS_RAW
        self.logger = logger
        self.logger.info(f"Dark web producer initialized for topic: {self.topic}")
    
    def produce_feed(self, feed_data: Dict[str, Any]) -> bool:
        """
        Produce dark web feed to Kafka
        
        Args:
            feed_data: Dark web feed data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create dark web feed event
            event = DarkWebFeed(**feed_data)
            
            # Serialize to JSON
            message = event.model_dump_json()
            
            # Use source as key
            key = event.source
            
            # Produce to Kafka
            self.producer.produce(
                self.topic,
                key=key,
                value=message,
                callback=delivery_callback
            )
            
            self.producer.poll(0)
            
            self.logger.debug(f"Produced dark web feed: {key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error producing dark web feed: {e}")
            return False
    
    def close(self):
        """Close the producer"""
        self.producer.flush()
        self.logger.info("Dark web producer closed")


if __name__ == "__main__":
    # Example usage
    producer = DarkWebProducer()
    
    # Sample dark web feed data
    sample_feed = {
        "source": "darkweb_forum",
        "content": "Selling stolen credentials and exploit tools",
        "url": "http://example.onion/post/123",
        "keywords": ["credentials", "exploit", "hacking"],
        "metadata": {"forum": "hacker_forum"}
    }
    
    producer.produce_feed(sample_feed)
    producer.close()


