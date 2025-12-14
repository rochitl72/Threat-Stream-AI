"""
Configuration management for ThreatStream AI
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    """Application configuration"""
    
    # Confluent Cloud Configuration
    CONFLUENT_BOOTSTRAP_SERVERS = os.getenv(
        "CONFLUENT_BOOTSTRAP_SERVERS",
        "pkc-n3603.us-central1.gcp.confluent.cloud:9092"
    )
    CONFLUENT_API_KEY = os.getenv("CONFLUENT_API_KEY", "")
    CONFLUENT_API_SECRET = os.getenv("CONFLUENT_API_SECRET", "")
    CONFLUENT_CLUSTER_ID = os.getenv("CONFLUENT_CLUSTER_ID", "lkc-jjqrk8")
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "animus-481019")
    # Use ADC if service account key doesn't exist
    _default_creds = "./credentials/animus-key.json"
    if not os.path.exists(_default_creds) or (os.path.exists(_default_creds) and os.path.getsize(_default_creds) == 0):
        # Use Application Default Credentials
        GOOGLE_APPLICATION_CREDENTIALS = None  # Will use ADC
        # Also unset from environment if it points to empty file
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") == _default_creds:
            os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
    else:
        GOOGLE_APPLICATION_CREDENTIALS = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS",
            _default_creds
        )
    GCP_REGION = os.getenv("GCP_REGION", "us-central1")
    VERTEX_AI_LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")
    
    # Kafka Topics
    TOPIC_TELEMETRY_RAW = "telemetry-raw"
    TOPIC_CODE_SAMPLES_RAW = "code-samples-raw"
    TOPIC_DARKWEB_FEEDS_RAW = "darkweb-feeds-raw"
    TOPIC_THREAT_PROFILES = "threat-profiles"
    TOPIC_MITRE_ATTACK_MAPPINGS = "mitre-attack-mappings"
    TOPIC_THREAT_ALERTS = "threat-alerts"
    
    # Schema Registry Configuration
    CONFLUENT_SCHEMA_REGISTRY_URL = os.getenv("CONFLUENT_SCHEMA_REGISTRY_URL", "")
    CONFLUENT_SCHEMA_REGISTRY_API_KEY = os.getenv(
        "CONFLUENT_SCHEMA_REGISTRY_API_KEY",
        ""  # Falls back to cluster API key if not set
    )
    CONFLUENT_SCHEMA_REGISTRY_API_SECRET = os.getenv(
        "CONFLUENT_SCHEMA_REGISTRY_API_SECRET",
        ""  # Falls back to cluster API secret if not set
    )
    
    # Application Configuration
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_kafka_config(cls) -> dict:
        """Get Kafka producer/consumer configuration"""
        return {
            "bootstrap.servers": cls.CONFLUENT_BOOTSTRAP_SERVERS,
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": "PLAIN",
            "sasl.username": cls.CONFLUENT_API_KEY,
            "sasl.password": cls.CONFLUENT_API_SECRET,
            "client.id": "threatstream-ai-client"
        }
    
    @classmethod
    def get_schema_registry_config(cls) -> dict:
        """Get Schema Registry configuration"""
        # Use Schema Registry specific keys if set, otherwise fall back to cluster keys
        api_key = cls.CONFLUENT_SCHEMA_REGISTRY_API_KEY or cls.CONFLUENT_API_KEY
        api_secret = cls.CONFLUENT_SCHEMA_REGISTRY_API_SECRET or cls.CONFLUENT_API_SECRET
        
        if not cls.CONFLUENT_SCHEMA_REGISTRY_URL or not api_key or not api_secret:
            return {}
        
        return {
            "url": cls.CONFLUENT_SCHEMA_REGISTRY_URL,
            "basic.auth.user.info": f"{api_key}:{api_secret}"
        }
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present"""
        required = [
            cls.CONFLUENT_BOOTSTRAP_SERVERS,
            cls.CONFLUENT_API_KEY,
            cls.CONFLUENT_API_SECRET,
            cls.GOOGLE_CLOUD_PROJECT,
        ]
        return all(required)

