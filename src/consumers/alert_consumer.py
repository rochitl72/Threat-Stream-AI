"""
Alert Consumer
Consumes threat alerts for dashboard/notification
"""

import json
import signal
import sys

from src.config import Config
from src.utils.kafka_utils import get_kafka_consumer
from src.utils.logger import setup_logger

logger = setup_logger("alert_consumer")


class AlertConsumer:
    """Consumes threat alerts"""
    
    def __init__(self):
        """Initialize alert consumer"""
        self.logger = logger
        self.consumer = get_kafka_consumer(
            group_id="alert-consumer-group",
            topics=[Config.TOPIC_THREAT_ALERTS]
        )
        self.running = True
        self.logger.info("Alert consumer initialized")
    
    def process_alert(self, alert_data: dict) -> None:
        """
        Process a threat alert
        
        Args:
            alert_data: Alert data
        """
        self.logger.warning(
            f"🚨 ALERT: {alert_data.get('severity', 'unknown').upper()} - "
            f"{alert_data.get('threat_type', 'unknown')} - "
            f"{alert_data.get('description', 'No description')}"
        )
        self.logger.info(f"MITRE: {alert_data.get('mitre_tactic')} / {alert_data.get('mitre_technique')}")
    
    def run(self):
        """Run the consumer loop"""
        self.logger.info("Starting alert consumer...")
        
        try:
            while self.running:
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    self.logger.error(f"Consumer error: {msg.error()}")
                    continue
                
                alert_data = json.loads(msg.value().decode('utf-8'))
                self.process_alert(alert_data)
                
        except KeyboardInterrupt:
            self.logger.info("Shutting down alert consumer...")
        finally:
            self.close()
    
    def close(self):
        """Close consumer"""
        self.consumer.close()
        self.logger.info("Alert consumer closed")


def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Shutdown signal received")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    consumer = AlertConsumer()
    consumer.run()

