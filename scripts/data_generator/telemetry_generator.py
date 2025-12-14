"""
Telemetry Data Generator
Generates realistic network telemetry with attack patterns
"""

import random
import ipaddress
from typing import Dict, Any, Optional
from datetime import datetime

from .base_generator import BaseGenerator
from .pattern_library import (
    PORT_SCAN_PATTERNS,
    DATA_EXFILTRATION_PATTERNS,
    SUSPICIOUS_IP_RANGES,
    EXTERNAL_IP_RANGES,
    get_random_pattern
)
from loguru import logger


class TelemetryGenerator(BaseGenerator):
    """Generates network telemetry data"""
    
    def __init__(self, producer, rate_limit: float = 2.0, pattern: Optional[str] = None):
        """
        Initialize telemetry generator
        
        Args:
            producer: Kafka producer instance
            rate_limit: Messages per second
            pattern: Specific pattern to use (None for random)
        """
        super().__init__(producer, rate_limit)
        self.pattern = pattern
        self.current_pattern = None
        self.scan_progress = {}  # Track port scan progress
        self.logger = logger.bind(component="telemetry_generator")
    
    def generate(self) -> Dict[str, Any]:
        """Generate a telemetry event"""
        # Select pattern if not set
        if not self.current_pattern:
            if self.pattern:
                self.current_pattern = self._get_pattern_by_name(self.pattern)
            else:
                # Randomly select pattern type
                pattern_type = random.choice(["port_scan", "normal", "data_exfiltration"])
                if pattern_type == "port_scan":
                    self.current_pattern = random.choice(PORT_SCAN_PATTERNS)
                elif pattern_type == "data_exfiltration":
                    self.current_pattern = random.choice(DATA_EXFILTRATION_PATTERNS)
                else:
                    self.current_pattern = None
        
        # Generate based on pattern
        if self.current_pattern and "ports" in self.current_pattern:
            return self._generate_port_scan()
        elif self.current_pattern and "bytes_sent" in self.current_pattern:
            return self._generate_data_exfiltration()
        else:
            return self._generate_normal_traffic()
    
    def _generate_port_scan(self) -> Dict[str, Any]:
        """Generate port scanning telemetry"""
        pattern = self.current_pattern
        source_ip = self._generate_ip(SUSPICIOUS_IP_RANGES)
        
        # Get next port in sequence
        if source_ip not in self.scan_progress:
            self.scan_progress[source_ip] = {
                "port_index": 0,
                "start_time": datetime.utcnow()
            }
        
        progress = self.scan_progress[source_ip]
        ports = pattern["ports"]
        
        if progress["port_index"] >= len(ports):
            # Reset or switch to new source
            self.scan_progress[source_ip] = {
                "port_index": 0,
                "start_time": datetime.utcnow()
            }
            progress = self.scan_progress[source_ip]
        
        port = ports[progress["port_index"]]
        progress["port_index"] += 1
        
        # Generate destination IP (sometimes same, sometimes varied)
        if random.random() < pattern.get("source_variation", 0.1):
            destination_ip = self._generate_ip(EXTERNAL_IP_RANGES)
        else:
            # Common target for port scan
            destination_ip = self._generate_ip(EXTERNAL_IP_RANGES)
        
        return {
            "source_ip": source_ip,
            "destination_ip": destination_ip,
            "protocol": random.choice(["TCP", "UDP"]),
            "port": port,
            "bytes_sent": random.randint(64, 512),
            "bytes_received": random.randint(0, 128),
            "endpoint": f"/scan/{port}",
            "status_code": random.choice([200, 403, 404, 500]),
            "metadata": {
                "scan_type": pattern["name"],
                "user_agent": self._generate_user_agent(),
                "suspicious": True,
                "autonomous_indicator": "high_frequency_requests"
            }
        }
    
    def _generate_data_exfiltration(self) -> Dict[str, Any]:
        """Generate data exfiltration telemetry"""
        pattern = self.current_pattern
        source_ip = self._generate_ip(SUSPICIOUS_IP_RANGES)
        destination_ip = self._generate_ip(EXTERNAL_IP_RANGES)
        
        bytes_sent = pattern["bytes_sent"]()
        bytes_received = pattern["bytes_received"]()
        
        return {
            "source_ip": source_ip,
            "destination_ip": destination_ip,
            "protocol": "TCP",
            "port": random.choice([443, 8080, 8443]),
            "bytes_sent": bytes_sent,
            "bytes_received": bytes_received,
            "endpoint": "/api/data/export",
            "status_code": 200,
            "metadata": {
                "exfiltration_type": pattern["name"],
                "user_agent": self._generate_user_agent(),
                "suspicious": True,
                "large_transfer": bytes_sent > 1000000,
                "autonomous_indicator": "systematic_data_transfer"
            }
        }
    
    def _generate_normal_traffic(self) -> Dict[str, Any]:
        """Generate normal network traffic"""
        source_ip = self._generate_ip(EXTERNAL_IP_RANGES)
        destination_ip = self._generate_ip(EXTERNAL_IP_RANGES)
        
        return {
            "source_ip": source_ip,
            "destination_ip": destination_ip,
            "protocol": random.choice(["TCP", "UDP", "HTTP", "HTTPS"]),
            "port": random.choice([80, 443, 22, 53, 3306]),
            "bytes_sent": random.randint(100, 5000),
            "bytes_received": random.randint(100, 10000),
            "endpoint": random.choice(["/", "/api/users", "/api/data", "/login"]),
            "status_code": random.choice([200, 201, 301, 404]),
            "metadata": {
                "user_agent": self._generate_user_agent(),
                "suspicious": False
            }
        }
    
    def _generate_ip(self, ranges: list) -> str:
        """Generate a random IP address from given ranges"""
        template = random.choice(ranges)
        return template.format(random.randint(1, 254))
    
    def _generate_user_agent(self) -> str:
        """Generate a random user agent"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "curl/7.68.0",
            "python-requests/2.28.0",
            "Go-http-client/1.1"
        ]
        return random.choice(user_agents)
    
    def _get_pattern_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get pattern by name"""
        all_patterns = PORT_SCAN_PATTERNS + DATA_EXFILTRATION_PATTERNS
        for pattern in all_patterns:
            if pattern.get("name") == name:
                return pattern
        return None
    
    def _produce_data(self, data: Dict[str, Any]) -> bool:
        """Produce telemetry data to Kafka"""
        try:
            # Use the producer passed in constructor
            from src.models.threat import TelemetryEvent
            
            event = TelemetryEvent(**data)
            message = event.model_dump_json()
            
            self.producer.produce(
                "telemetry-raw",
                key=data.get("source_ip", "unknown"),
                value=message
            )
            self.producer.poll(0)
            return True
        except Exception as e:
            self.logger.error(f"Error producing telemetry: {e}")
            return False

