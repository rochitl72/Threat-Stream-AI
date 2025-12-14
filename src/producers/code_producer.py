"""
Code Sample Producer
Produces code samples to Kafka for analysis
"""

import json
import hashlib
from typing import Dict, Any
from confluent_kafka import Producer

from src.config import Config
from src.models.threat import CodeSample
from src.utils.kafka_utils import get_kafka_producer, delivery_callback
from src.utils.logger import setup_logger

logger = setup_logger("code_producer")


class CodeProducer:
    """Produces code samples to Kafka"""
    
    def __init__(self):
        """Initialize code producer"""
        self.producer = get_kafka_producer()
        self.topic = Config.TOPIC_CODE_SAMPLES_RAW
        self.logger = logger
        self.logger.info(f"Code producer initialized for topic: {self.topic}")
    
    def produce_code_sample(self, code_data: Dict[str, Any]) -> bool:
        """
        Produce code sample to Kafka
        
        Args:
            code_data: Code sample data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate hash if not provided
            if "hash" not in code_data and "code_content" in code_data:
                code_data["hash"] = hashlib.sha256(
                    code_data["code_content"].encode()
                ).hexdigest()
            
            # Create code sample event
            event = CodeSample(**code_data)
            
            # Serialize to JSON
            message = event.model_dump_json()
            
            # Use hash as key for deduplication
            key = event.hash or event.file_name or "unknown"
            
            # Produce to Kafka
            self.producer.produce(
                self.topic,
                key=key,
                value=message,
                callback=delivery_callback
            )
            
            self.producer.poll(0)
            
            self.logger.debug(f"Produced code sample: {key[:16]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"Error producing code sample: {e}")
            return False
    
    def close(self):
        """Close the producer"""
        self.producer.flush()
        self.logger.info("Code producer closed")


if __name__ == "__main__":
    # Example usage
    producer = CodeProducer()
    
    # Sample code data
    sample_code = {
        "source": "github",
        "code_content": "import os; os.system('rm -rf /')",
        "language": "python",
        "file_name": "suspicious.py",
        "metadata": {"repo": "test/repo"}
    }
    
    producer.produce_code_sample(sample_code)
    producer.close()


