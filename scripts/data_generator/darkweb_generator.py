"""
Dark Web Feed Generator
Generates threat intelligence from dark web sources
"""

import random
from typing import Dict, Any, Optional
from datetime import datetime

from .base_generator import BaseGenerator
from .pattern_library import DARKWEB_THREAT_PATTERNS, get_random_pattern
from loguru import logger


class DarkWebGenerator(BaseGenerator):
    """Generates dark web feed data"""
    
    def __init__(self, producer, rate_limit: float = 0.3, pattern: Optional[str] = None):
        """
        Initialize dark web generator
        
        Args:
            producer: Kafka producer instance
            rate_limit: Messages per second
            pattern: Specific pattern to use (None for random)
        """
        super().__init__(producer, rate_limit)
        self.pattern = pattern
        self.current_pattern = None
        self.logger = logger.bind(component="darkweb_generator")
    
    def generate(self) -> Dict[str, Any]:
        """Generate a dark web feed"""
        # Select pattern if not set
        if not self.current_pattern:
            if self.pattern:
                self.current_pattern = self._get_pattern_by_name(self.pattern)
            else:
                self.current_pattern = random.choice(DARKWEB_THREAT_PATTERNS)
        
        pattern = self.current_pattern
        template = random.choice(pattern["content_templates"])
        
        # Generate content from template
        content = self._generate_content(template, pattern)
        
        # Generate URL (simulated .onion address)
        url = self._generate_onion_url()
        
        return {
            "source": random.choice(["darkweb_forum", "tor_marketplace", "hacker_chat", "exploit_db"]),
            "content": content,
            "url": url,
            "keywords": pattern["keywords"] + self._generate_additional_keywords(pattern),
            "metadata": {
                "pattern_type": pattern["name"],
                "threat_level": self._determine_threat_level(pattern),
                "autonomous_indicator": "autonomous_tool" if "autonomous" in pattern["name"] else None,
                "detected_at": datetime.utcnow().isoformat()
            }
        }
    
    def _generate_content(self, template: str, pattern: Dict[str, Any]) -> str:
        """Generate content from template"""
        content = template
        
        # Replace placeholders
        if "{exploit_type}" in content:
            exploit_types = ["RCE", "SQLi", "XSS", "LFI", "RFI", "SSRF"]
            content = content.replace("{exploit_type}", random.choice(exploit_types))
        
        if "{target}" in content:
            targets = ["WordPress", "Joomla", "Apache", "nginx", "MySQL", "PostgreSQL"]
            content = content.replace("{target}", random.choice(targets))
        
        if "{year}" in content:
            content = content.replace("{year}", str(random.randint(2020, 2024)))
        
        if "{number}" in content:
            content = content.replace("{number}", str(random.randint(1000, 9999)))
        
        if "{software}" in content:
            software = ["Windows", "Linux", "Apache", "nginx", "WordPress"]
            content = content.replace("{software}", random.choice(software))
        
        if "{price}" in content:
            prices = ["$5000", "$10000", "0.5 BTC", "1 BTC", "negotiable"]
            content = content.replace("{price}", random.choice(prices))
        
        if "{version}" in content:
            versions = ["1.0", "2.0", "3.5", "4.2", "latest"]
            content = content.replace("{version}", random.choice(versions))
        
        if "{company}" in content:
            companies = ["TechCorp", "DataSys", "CloudInc", "SecureNet"]
            content = content.replace("{company}", random.choice(companies))
        
        if "{count}" in content:
            count = random.randint(1000, 100000)
            content = content.replace("{count}", str(count))
        
        if "{type}" in content:
            types = ["email", "password", "credit_card", "SSN", "API_key"]
            content = content.replace("{type}", random.choice(types))
        
        if "{target}" in content:
            targets = ["example.com", "target.org", "victim.net"]
            content = content.replace("{target}", random.choice(targets))
        
        if "{attack_type}" in content:
            attack_types = ["DDoS", "SQL injection", "XSS", "brute force"]
            content = content.replace("{attack_type}", random.choice(attack_types))
        
        if "{time}" in content:
            times = ["2024-01-15 14:00 UTC", "tomorrow 12:00", "next week"]
            content = content.replace("{time}", random.choice(times))
        
        if "{date}" in content:
            dates = ["2024-01-20", "next Monday", "end of month"]
            content = content.replace("{date}", random.choice(dates))
        
        if "{target_type}" in content:
            target_types = ["web applications", "databases", "APIs", "servers"]
            content = content.replace("{target_type}", random.choice(target_types))
        
        # Add some additional context
        content = f"[{random.choice(['URGENT', 'NEW', 'FRESH', 'HOT'])}] {content}"
        
        return content
    
    def _generate_onion_url(self) -> str:
        """Generate a simulated .onion URL"""
        # Generate random 16-character base32 string (simplified)
        chars = "abcdefghijklmnopqrstuvwxyz234567"
        onion_id = ''.join(random.choice(chars) for _ in range(16))
        return f"http://{onion_id}.onion/post/{random.randint(1000, 9999)}"
    
    def _generate_additional_keywords(self, pattern: Dict[str, Any]) -> list:
        """Generate additional relevant keywords"""
        base_keywords = pattern["keywords"]
        additional = []
        
        keyword_groups = {
            "exploit": ["poc", "payload", "shellcode", "bypass"],
            "credentials": ["leak", "breach", "dump", "database"],
            "attack": ["botnet", "ddos", "coordinate", "campaign"],
            "autonomous": ["ai", "ml", "automated", "self-replicating"]
        }
        
        for group, keywords in keyword_groups.items():
            if any(k in base_keywords for k in keyword_groups.get(group, [])):
                additional.extend(random.sample(keywords, min(2, len(keywords))))
        
        return list(set(additional))  # Remove duplicates
    
    def _determine_threat_level(self, pattern: Dict[str, Any]) -> str:
        """Determine threat level based on pattern"""
        high_threat_patterns = ["exploit_discussion", "autonomous_tool", "attack_coordination"]
        if pattern["name"] in high_threat_patterns:
            return "high"
        return "medium"
    
    def _get_pattern_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get pattern by name"""
        for pattern in DARKWEB_THREAT_PATTERNS:
            if pattern.get("name") == name:
                return pattern
        return None
    
    def _produce_data(self, data: Dict[str, Any]) -> bool:
        """Produce dark web feed to Kafka"""
        try:
            # Use the producer passed in constructor
            from src.models.threat import DarkWebFeed
            
            event = DarkWebFeed(**data)
            message = event.model_dump_json()
            
            self.producer.produce(
                "darkweb-feeds-raw",
                key=data.get("source", "unknown"),
                value=message
            )
            self.producer.poll(0)
            return True
        except Exception as e:
            self.logger.error(f"Error producing dark web feed: {e}")
            return False

