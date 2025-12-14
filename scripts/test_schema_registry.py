#!/usr/bin/env python3
"""
Test script to verify Schema Registry connection using existing API keys
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.utils.logger import setup_logger

logger = setup_logger("test_schema_registry")


def test_schema_registry_connection():
    """Test Schema Registry connection with existing API keys"""
    
    logger.info("=" * 60)
    logger.info("Testing Schema Registry Connection")
    logger.info("=" * 60)
    
    # Check configuration
    schema_registry_url = Config.CONFLUENT_SCHEMA_REGISTRY_URL
    api_key = Config.CONFLUENT_SCHEMA_REGISTRY_API_KEY or Config.CONFLUENT_API_KEY
    api_secret = Config.CONFLUENT_SCHEMA_REGISTRY_API_SECRET or Config.CONFLUENT_API_SECRET
    
    logger.info(f"Schema Registry URL: {schema_registry_url}")
    logger.info(f"API Key: {api_key[:10]}..." if api_key else "Not set")
    logger.info(f"API Secret: {'*' * 20}" if api_secret else "Not set")
    
    if not schema_registry_url:
        logger.error("❌ Schema Registry URL not configured")
        return False
    
    if not api_key or not api_secret:
        logger.error("❌ API Key or Secret not configured")
        return False
    
    # Test connection
    try:
        from confluent_kafka.schema_registry import SchemaRegistryClient
        
        # Create Schema Registry client
        schema_registry_config = {
            "url": schema_registry_url,
            "basic.auth.user.info": f"{api_key}:{api_secret}"
        }
        
        logger.info("\nAttempting to connect to Schema Registry...")
        client = SchemaRegistryClient(schema_registry_config)
        
        # Try to get subjects (this will test authentication)
        try:
            subjects = client.get_subjects()
            logger.info(f"✅ Schema Registry connection successful!")
            logger.info(f"✅ Found {len(subjects)} subjects")
            if subjects:
                logger.info(f"   Subjects: {', '.join(subjects[:5])}")
                if len(subjects) > 5:
                    logger.info(f"   ... and {len(subjects) - 5} more")
            else:
                logger.info("   (No subjects registered yet - this is normal for a new setup)")
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                logger.error(f"❌ Authentication failed: {error_msg}")
                logger.error("   The existing API keys may not work for Schema Registry")
                logger.error("   You may need to create separate Schema Registry API keys")
                return False
            elif "404" in error_msg:
                logger.warning(f"⚠️  Connection successful but endpoint not found: {error_msg}")
                logger.warning("   This might be a URL issue")
                return False
            else:
                logger.error(f"❌ Error accessing Schema Registry: {error_msg}")
                return False
                
    except ImportError:
        logger.error("❌ confluent-kafka[schema-registry] not installed")
        logger.info("   Install with: pip install 'confluent-kafka[schema-registry]'")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to create Schema Registry client: {e}")
        return False


def test_schema_registry_basic():
    """Test basic HTTP connection to Schema Registry"""
    import requests
    
    schema_registry_url = Config.CONFLUENT_SCHEMA_REGISTRY_URL
    api_key = Config.CONFLUENT_SCHEMA_REGISTRY_API_KEY or Config.CONFLUENT_API_KEY
    api_secret = Config.CONFLUENT_SCHEMA_REGISTRY_API_SECRET or Config.CONFLUENT_API_SECRET
    
    if not schema_registry_url:
        return False
    
    try:
        # Test basic connectivity
        response = requests.get(
            f"{schema_registry_url}/subjects",
            auth=(api_key, api_secret),
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("✅ Basic HTTP connection successful")
            return True
        elif response.status_code == 401:
            logger.error("❌ Authentication failed (401 Unauthorized)")
            return False
        else:
            logger.warning(f"⚠️  Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ HTTP connection failed: {e}")
        return False


if __name__ == "__main__":
    logger.info("\nTesting Schema Registry with existing cluster API keys...\n")
    
    # Test 1: Basic HTTP connection
    logger.info("Test 1: Basic HTTP Connection")
    http_ok = test_schema_registry_basic()
    logger.info("")
    
    # Test 2: Full Schema Registry client
    logger.info("Test 2: Schema Registry Client Connection")
    client_ok = test_schema_registry_connection()
    logger.info("")
    
    # Summary
    logger.info("=" * 60)
    logger.info("Test Summary:")
    logger.info(f"  HTTP Connection: {'✅ PASS' if http_ok else '❌ FAIL'}")
    logger.info(f"  Schema Registry Client: {'✅ PASS' if client_ok else '❌ FAIL'}")
    logger.info("=" * 60)
    
    if http_ok and client_ok:
        logger.info("\n🎉 SUCCESS! Your existing API keys work with Schema Registry!")
        logger.info("   You can use the same keys for both Kafka and Schema Registry.")
        sys.exit(0)
    elif http_ok:
        logger.info("\n⚠️  HTTP connection works but client test failed.")
        logger.info("   This might be a library issue. Check dependencies.")
        sys.exit(1)
    else:
        logger.info("\n❌ The existing API keys don't work with Schema Registry.")
        logger.info("   You'll need to create separate Schema Registry API keys.")
        sys.exit(1)


