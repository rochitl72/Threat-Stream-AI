"""
Pattern Library for Threat Data Generation
Predefined attack patterns and scenarios
"""

from typing import List, Dict, Any
import random

# Port scanning patterns
PORT_SCAN_PATTERNS = [
    {
        "name": "sequential_port_scan",
        "description": "Sequential port scanning from low to high",
        "ports": list(range(20, 100)),
        "interval": 0.5,
        "source_variation": 0.1
    },
    {
        "name": "common_ports_scan",
        "description": "Scanning common service ports",
        "ports": [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 3306, 3389, 5432],
        "interval": 1.0,
        "source_variation": 0.2
    },
    {
        "name": "stealth_scan",
        "description": "Slow, stealthy port scanning",
        "ports": list(range(1, 65536)),
        "interval": 5.0,
        "source_variation": 0.05
    }
]

# Data exfiltration patterns
DATA_EXFILTRATION_PATTERNS = [
    {
        "name": "large_transfer",
        "bytes_sent": lambda: random.randint(1000000, 10000000),
        "bytes_received": lambda: random.randint(100, 1000),
        "duration": lambda: random.uniform(30, 300),
        "frequency": "continuous"
    },
    {
        "name": "burst_transfer",
        "bytes_sent": lambda: random.randint(500000, 2000000),
        "bytes_received": lambda: random.randint(100, 500),
        "duration": lambda: random.uniform(5, 15),
        "frequency": "burst"
    },
    {
        "name": "slow_exfiltration",
        "bytes_sent": lambda: random.randint(10000, 100000),
        "bytes_received": lambda: random.randint(50, 200),
        "duration": lambda: random.uniform(600, 3600),
        "frequency": "slow"
    }
]

# Malicious code patterns
MALICIOUS_CODE_PATTERNS = [
    {
        "name": "rce_pattern",
        "languages": ["python", "bash", "powershell"],
        "patterns": [
            "os.system('{command}')",
            "subprocess.call(['{command}'])",
            "eval('{code}')",
            "exec('{code}')",
            "__import__('os').system('{command}')"
        ],
        "suspicious_keywords": ["rm -rf", "format", "delete", "shutdown"]
    },
    {
        "name": "sql_injection",
        "languages": ["sql", "python", "javascript"],
        "patterns": [
            "SELECT * FROM users WHERE id = '{input}'",
            "'; DROP TABLE users; --",
            "UNION SELECT * FROM passwords",
            "OR '1'='1'"
        ],
        "suspicious_keywords": ["DROP", "UNION", "OR 1=1"]
    },
    {
        "name": "data_exfiltration_code",
        "languages": ["python", "javascript", "bash"],
        "patterns": [
            "requests.post('{url}', data=file.read())",
            "curl -X POST '{url}' -d @file",
            "socket.send(data)",
            "urllib.request.urlopen('{url}')"
        ],
        "suspicious_keywords": ["post", "upload", "send", "exfiltrate"]
    },
    {
        "name": "autonomous_system",
        "languages": ["python", "javascript"],
        "patterns": [
            "while True: {action}",
            "for target in targets: {exploit}",
            "if vulnerability_found: {exploit}",
            "automated_scan()",
            "self.replicate()"
        ],
        "suspicious_keywords": ["while True", "automated", "self.replicate", "autonomous"]
    }
]

# Dark web threat patterns
DARKWEB_THREAT_PATTERNS = [
    {
        "name": "exploit_discussion",
        "keywords": ["exploit", "vulnerability", "CVE", "zero-day", "poc"],
        "content_templates": [
            "New {exploit_type} exploit for {target} available",
            "CVE-{year}-{number} proof of concept released",
            "Zero-day in {software} - selling for {price}",
            "Working exploit for {version} - contact for details"
        ]
    },
    {
        "name": "credential_dump",
        "keywords": ["credentials", "dump", "leak", "breach", "database"],
        "content_templates": [
            "Fresh credential dump from {company} - {count} accounts",
            "Database leak: {type} credentials available",
            "Bulk credentials for sale - {count} entries",
            "New breach data: {source} credentials"
        ]
    },
    {
        "name": "attack_coordination",
        "keywords": ["ddos", "attack", "target", "coordinate", "botnet"],
        "content_templates": [
            "Coordinating attack on {target} at {time}",
            "Botnet ready for {attack_type} on {target}",
            "Join the attack on {target} - instructions inside",
            "DDoS campaign against {target} starting {date}"
        ]
    },
    {
        "name": "autonomous_tool",
        "keywords": ["autonomous", "automated", "ai", "bot", "self-replicating"],
        "content_templates": [
            "Autonomous hacking tool - self-replicating and adaptive",
            "AI-powered exploit framework - learns from targets",
            "Self-propagating malware - no manual intervention needed",
            "Autonomous system for {target_type} exploitation"
        ]
    }
]

# IP address ranges for realistic generation
SUSPICIOUS_IP_RANGES = [
    "192.168.1.{}",  # Internal network
    "10.0.0.{}",     # Private network
    "172.16.0.{}",   # Private network
    "203.0.113.{}",  # Documentation range (often used in examples)
    "198.51.100.{}", # Documentation range
]

EXTERNAL_IP_RANGES = [
    "185.220.101.{}",  # Tor exit nodes (example)
    "45.33.32.{}",     # Example external
    "104.248.90.{}",   # Example external
]

# Autonomous system indicators
AUTONOMOUS_INDICATORS = [
    "high_frequency_requests",
    "pattern_based_behavior",
    "rapid_port_enumeration",
    "systematic_scanning",
    "automated_response_handling",
    "self_adapting_patterns",
    "no_human_like_delays",
    "parallel_target_processing",
    "recursive_exploration",
    "machine_learning_adaptation"
]

# Attack scenario templates
ATTACK_SCENARIOS = [
    {
        "name": "reconnaissance_to_exploitation",
        "stages": [
            {"type": "telemetry", "pattern": "port_scan", "count": 50},
            {"type": "code", "pattern": "rce_pattern", "count": 5},
            {"type": "telemetry", "pattern": "data_exfiltration", "count": 10},
            {"type": "darkweb", "pattern": "exploit_discussion", "count": 3}
        ],
        "timeline": "sequential",
        "correlation": True
    },
    {
        "name": "autonomous_hacking_system",
        "stages": [
            {"type": "telemetry", "pattern": "stealth_scan", "count": 100},
            {"type": "code", "pattern": "autonomous_system", "count": 10},
            {"type": "darkweb", "pattern": "autonomous_tool", "count": 5},
            {"type": "telemetry", "pattern": "large_transfer", "count": 20}
        ],
        "timeline": "parallel",
        "correlation": True
    },
    {
        "name": "data_breach_chain",
        "stages": [
            {"type": "code", "pattern": "sql_injection", "count": 8},
            {"type": "telemetry", "pattern": "slow_exfiltration", "count": 15},
            {"type": "darkweb", "pattern": "credential_dump", "count": 4}
        ],
        "timeline": "sequential",
        "correlation": True
    }
]

def get_pattern(pattern_name: str, pattern_type: str) -> Dict[str, Any]:
    """Get a specific pattern by name and type"""
    pattern_map = {
        "port_scan": PORT_SCAN_PATTERNS,
        "data_exfiltration": DATA_EXFILTRATION_PATTERNS,
        "code": MALICIOUS_CODE_PATTERNS,
        "darkweb": DARKWEB_THREAT_PATTERNS
    }
    
    patterns = pattern_map.get(pattern_type, [])
    for pattern in patterns:
        if pattern.get("name") == pattern_name:
            return pattern
    
    return {}

def get_random_pattern(pattern_type: str) -> Dict[str, Any]:
    """Get a random pattern of specified type"""
    pattern_map = {
        "port_scan": PORT_SCAN_PATTERNS,
        "data_exfiltration": DATA_EXFILTRATION_PATTERNS,
        "code": MALICIOUS_CODE_PATTERNS,
        "darkweb": DARKWEB_THREAT_PATTERNS
    }
    
    patterns = pattern_map.get(pattern_type, [])
    if patterns:
        return random.choice(patterns)
    return {}

