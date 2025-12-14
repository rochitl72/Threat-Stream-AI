"""
Telemetry Producer
Produces telemetry events to Kafka
"""

import json
import time
from typing import Dict, Any
from confluent_kafka import Producer

from src.config import Config
from src.models.threat import TelemetryEvent
from src.utils.kafka_utils import get_kafka_producer, delivery_callback
from src.utils.logger import setup_logger

logger = setup_logger("telemetry_producer")


class TelemetryProducer:
    """Produces telemetry events to Kafka"""
    
    def __init__(self):
        """Initialize telemetry producer"""
        self.producer = get_kafka_producer()
        self.topic = Config.TOPIC_TELEMETRY_RAW
        self.logger = logger
        self.logger.info(f"Telemetry producer initialized for topic: {self.topic}")
    
    def produce_telemetry(self, telemetry_data: Dict[str, Any]) -> bool:
        """
        Produce telemetry event to Kafka
        
        Args:
            telemetry_data: Telemetry event data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create telemetry event
            event = TelemetryEvent(**telemetry_data)
            
            # Serialize to JSON
            message = event.model_dump_json()
            
            # Produce to Kafka
            self.producer.produce(
                self.topic,
                key=event.source_ip,
                value=message,
                callback=delivery_callback
            )
            
            # Flush to ensure delivery
            self.producer.poll(0)
            
            self.logger.debug(f"Produced telemetry event: {event.source_ip}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error producing telemetry: {e}")
            return False
    
    def produce_batch(self, telemetry_list: list[Dict[str, Any]]) -> int:
        """
        Produce multiple telemetry events
        
        Args:
            telemetry_list: List of telemetry event data
            
        Returns:
            Number of successfully produced events
        """
        success_count = 0
        for telemetry in telemetry_list:
            if self.produce_telemetry(telemetry):
                success_count += 1
        
        # Flush all messages
        self.producer.flush()
        
        self.logger.info(f"Produced {success_count}/{len(telemetry_list)} telemetry events")
        return success_count
    
    def close(self):
        """Close the producer"""
        self.producer.flush()
        self.logger.info("Telemetry producer closed")


if __name__ == "__main__":
    # Example usage
    producer = TelemetryProducer()
    
    # Sample telemetry data
    sample_telemetry = {
        "source_ip": "192.168.1.100",
        "destination_ip": "10.0.0.1",
        "protocol": "TCP",
        "port": 443,
        "bytes_sent": 1024,
        "bytes_received": 2048,
        "endpoint": "/api/v1/data",
        "status_code": 200,
        "metadata": {"user_agent": "Mozilla/5.0"}
    }
    
    producer.produce_telemetry(sample_telemetry)
    producer.close()


