"""
Threat Consumer
Consumes raw threat data, analyzes it, and produces threat profiles
"""

import json
import signal
import sys
from typing import Dict, Any

from confluent_kafka import Consumer, Producer

from src.config import Config
from src.models.threat import TelemetryEvent, CodeSample, DarkWebFeed, ThreatEvent
from src.processors.threat_analyzer import ThreatAnalyzer
from src.processors.mitre_mapper import MITREMapper
from src.utils.kafka_utils import get_kafka_consumer, get_kafka_producer
from src.utils.logger import setup_logger

logger = setup_logger("threat_consumer")


class ThreatConsumer:
    """Consumes and processes threat data"""
    
    def __init__(self):
        """Initialize threat consumer"""
        self.logger = logger
        self.analyzer = ThreatAnalyzer()
        self.mitre_mapper = MITREMapper()
        
        # Consumer for raw data
        self.consumer = get_kafka_consumer(
            group_id="threat-analyzer-group",
            topics=[
                Config.TOPIC_TELEMETRY_RAW,
                Config.TOPIC_CODE_SAMPLES_RAW,
                Config.TOPIC_DARKWEB_FEEDS_RAW
            ]
        )
        
        # Producer for processed data
        self.producer = get_kafka_producer()
        
        self.running = True
        self.logger.info("Threat consumer initialized")
    
    def process_message(self, msg) -> None:
        """
        Process a single message
        
        Args:
            msg: Kafka message
        """
        try:
            # Parse message
            data = json.loads(msg.value().decode('utf-8'))
            topic = msg.topic()
            
            self.logger.info(f"Processing message from topic: {topic}")
            
            # Analyze based on topic
            threat_event = None
            if topic == Config.TOPIC_TELEMETRY_RAW:
                threat_event = self.analyzer.analyze_telemetry(data)
            elif topic == Config.TOPIC_CODE_SAMPLES_RAW:
                threat_event = self.analyzer.analyze_code_sample(data)
            elif topic == Config.TOPIC_DARKWEB_FEEDS_RAW:
                threat_event = self.analyzer.analyze_darkweb_feed(data)
            
            # If threat detected, create profile and map to MITRE
            if threat_event:
                self.logger.info(f"Threat detected: {threat_event.threat_type.value}")
                
                # Create threat profile
                profile = self.analyzer.create_threat_profile([threat_event])
                
                if profile:
                    # Produce threat profile
                    self.producer.produce(
                        Config.TOPIC_THREAT_PROFILES,
                        key=profile.profile_id,
                        value=profile.model_dump_json()
                    )
                    
                    # Map to MITRE ATT&CK
                    mitre_mapping = self.mitre_mapper.map_threat_profile(profile)
                    
                    # Produce MITRE mapping
                    self.producer.produce(
                        Config.TOPIC_MITRE_ATTACK_MAPPINGS,
                        key=mitre_mapping.mapping_id,
                        value=mitre_mapping.model_dump_json()
                    )
                    
                    # If high severity, produce alert
                    if profile.severity.value in ["high", "critical"]:
                        alert = {
                            "alert_id": profile.profile_id,
                            "timestamp": profile.timestamp.isoformat(),
                            "severity": profile.severity.value,
                            "threat_type": profile.threat_type.value,
                            "description": profile.ai_analysis.get("summary", "High severity threat detected"),
                            "mitre_tactic": mitre_mapping.primary_tactic,
                            "mitre_technique": mitre_mapping.primary_technique
                        }
                        
                        self.producer.produce(
                            Config.TOPIC_THREAT_ALERTS,
                            key=alert["alert_id"],
                            value=json.dumps(alert)
                        )
                    
                    self.producer.poll(0)
                    self.logger.info(f"Threat profile created: {profile.profile_id}")
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    def run(self):
        """Run the consumer loop"""
        self.logger.info("Starting threat consumer...")
        
        try:
            while self.running:
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    self.logger.error(f"Consumer error: {msg.error()}")
                    continue
                
                self.process_message(msg)
                
        except KeyboardInterrupt:
            self.logger.info("Shutting down threat consumer...")
        finally:
            self.close()
    
    def close(self):
        """Close consumer and producer"""
        self.consumer.close()
        self.producer.flush()
        self.logger.info("Threat consumer closed")


def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Shutdown signal received")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    consumer = ThreatConsumer()
    consumer.run()


