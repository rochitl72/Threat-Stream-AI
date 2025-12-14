"""
Kafka Monitoring Service
Monitors Kafka topics and provides real-time data
"""

import json
import asyncio
import time
from typing import Dict, Any, List, Optional
from collections import deque
from datetime import datetime
from loguru import logger

from confluent_kafka import Consumer, KafkaException, TopicPartition
from src.config import Config
from src.utils.kafka_utils import get_kafka_consumer


class KafkaMonitor:
    """Monitors Kafka topics and provides data access"""
    
    _instance = None
    
    def __init__(self):
        """Initialize Kafka monitor"""
        self.consumer = None
        self.running = False
        self.message_cache = {}  # Topic -> deque of recent messages
        self.metrics = {}  # Topic -> metrics dict
        self.threat_cache = deque(maxlen=1000)  # Recent threats
        self.profile_cache = deque(maxlen=500)  # Recent profiles
        self.alert_cache = deque(maxlen=200)  # Recent alerts
        self.mitre_cache = deque(maxlen=500)  # Recent MITRE mappings
        self.logger = logger.bind(component="kafka_monitor")
        
        # Initialize message caches for each topic
        for topic in [
            Config.TOPIC_TELEMETRY_RAW,
            Config.TOPIC_CODE_SAMPLES_RAW,
            Config.TOPIC_DARKWEB_FEEDS_RAW,
            Config.TOPIC_THREAT_PROFILES,
            Config.TOPIC_MITRE_ATTACK_MAPPINGS,
            Config.TOPIC_THREAT_ALERTS
        ]:
            self.message_cache[topic] = deque(maxlen=100)
            self.metrics[topic] = {
                "message_count": 0,
                "last_message_time": None,
                "messages_per_second": 0.0
            }
    
    async def start(self):
        """Start monitoring Kafka topics"""
        try:
            self.consumer = get_kafka_consumer(
                group_id="dashboard-monitor-group",
                topics=list(self.message_cache.keys())
            )
            
            self.running = True
            
            # Backfill recent messages before starting normal consumption
            await self._backfill_recent_messages(messages_per_topic=50)
            
            asyncio.create_task(self._consume_loop())
            self.logger.info("Kafka monitor started")
        except Exception as e:
            self.logger.error(f"Error starting Kafka monitor: {e}")
            raise
    
    async def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.consumer:
            self.consumer.close()
        self.logger.info("Kafka monitor stopped")
    
    def is_connected(self) -> bool:
        """Check if connected to Kafka"""
        return self.consumer is not None and self.running
    
    async def _backfill_recent_messages(self, messages_per_topic: int = 50):
        """
        Backfill recent messages from Kafka on startup
        
        Args:
            messages_per_topic: Number of recent messages to fetch per topic
        """
        self.logger.info(f"Backfilling up to {messages_per_topic} recent messages per topic...")
        
        try:
            # Create a temporary consumer for backfilling
            backfill_config = Config.get_kafka_config()
            backfill_config.update({
                "group.id": f"dashboard-backfill-{int(time.time())}",  # Unique group ID
                "auto.offset.reset": "latest",  # Start from latest
                "enable.auto.commit": False
            })
            
            backfill_consumer = Consumer(backfill_config)
            topics = list(self.message_cache.keys())
            backfill_consumer.subscribe(topics)
            
            # Wait for assignment
            await asyncio.sleep(2)
            
            # Get partition assignments
            partitions = backfill_consumer.assignment()
            
            # For each partition, seek to N messages before the end
            seek_positions = []
            for partition in partitions:
                try:
                    # Get high watermark (latest offset)
                    low, high = backfill_consumer.get_watermark_offsets(partition, timeout=5)
                    
                    # Seek to N messages before high (or low if not enough messages)
                    seek_offset = max(low, high - messages_per_topic)
                    # Update the partition offset
                    partition.offset = seek_offset
                    seek_positions.append(partition)
                    
                    self.logger.debug(f"Seeking {partition.topic}:{partition.partition} to offset {seek_offset} (high: {high})")
                except Exception as e:
                    self.logger.warning(f"Could not get offsets for {partition}: {e}")
            
            if seek_positions:
                backfill_consumer.assign(seek_positions)
            
            # Consume messages until we have enough or timeout
            messages_fetched = {topic: 0 for topic in topics}
            start_time = time.time()
            timeout = 30  # 30 second timeout
            
            self.logger.info("Consuming messages for backfill...")
            
            while time.time() - start_time < timeout:
                # Use run_in_executor to avoid blocking the event loop
                loop = asyncio.get_event_loop()
                msg = await loop.run_in_executor(None, backfill_consumer.poll, 1.0)
                
                if msg is None:
                    # Check if we've waited long enough
                    if time.time() - start_time > 5 and sum(messages_fetched.values()) > 0:
                        break
                    continue
                    
                if msg.error():
                    if msg.error().code() == KafkaException._PARTITION_EOF:
                        continue
                    self.logger.warning(f"Consumer error during backfill: {msg.error()}")
                    continue
                    
                topic = msg.topic()
                if messages_fetched[topic] < messages_per_topic:
                    await self._process_message(msg)
                    messages_fetched[topic] += 1
                    
                    if sum(messages_fetched.values()) % 10 == 0:
                        self.logger.debug(f"Backfilled {sum(messages_fetched.values())} messages so far...")
                    
                # Check if we have enough messages for all topics
                if all(count >= messages_per_topic for count in messages_fetched.values()):
                    break
            
            backfill_consumer.close()
            
            total_fetched = sum(messages_fetched.values())
            self.logger.info(f"✅ Backfilled {total_fetched} messages from Kafka")
            
            # Log per-topic counts
            for topic, count in messages_fetched.items():
                if count > 0:
                    self.logger.info(f"  - {topic}: {count} messages")
        
        except Exception as e:
            self.logger.error(f"Error backfilling messages: {e}", exc_info=True)
            # Don't fail startup if backfill fails
            self.logger.warning("Continuing without backfill - will only show new messages")
    
    async def _consume_loop(self):
        """Main consumption loop"""
        while self.running:
            try:
                # Use run_in_executor to avoid blocking the event loop
                loop = asyncio.get_event_loop()
                msg = await loop.run_in_executor(None, self.consumer.poll, 1.0)
                
                if msg is None:
                    await asyncio.sleep(0.1)
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaException._PARTITION_EOF:
                        continue
                    self.logger.error(f"Consumer error: {msg.error()}")
                    continue
                
                await self._process_message(msg)
                
            except Exception as e:
                self.logger.error(f"Error in consume loop: {e}")
                await asyncio.sleep(1)
    
    async def _process_message(self, msg):
        """Process a Kafka message"""
        try:
            topic = msg.topic()
            value = msg.value().decode('utf-8')
            data = json.loads(value)
            
            # Add to message cache
            message_entry = {
                "topic": topic,
                "key": msg.key().decode('utf-8') if msg.key() else None,
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "partition": msg.partition(),
                "offset": msg.offset()
            }
            
            self.message_cache[topic].append(message_entry)
            
            # Update metrics
            self._update_metrics(topic)
            
            # Cache specific data types
            if topic == Config.TOPIC_THREAT_PROFILES:
                self.profile_cache.append(data)
            elif topic == Config.TOPIC_THREAT_ALERTS:
                self.alert_cache.append(data)
            elif topic == Config.TOPIC_MITRE_ATTACK_MAPPINGS:
                self.mitre_cache.append(data)
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    def _update_metrics(self, topic: str):
        """Update metrics for a topic"""
        metrics = self.metrics[topic]
        metrics["message_count"] += 1
        metrics["last_message_time"] = datetime.utcnow().isoformat()
        
        # Calculate messages per second (simplified)
        # In production, use a time window
        if metrics["message_count"] % 10 == 0:
            metrics["messages_per_second"] = 10.0  # Simplified
    
    async def list_topics(self) -> List[str]:
        """List all monitored topics"""
        return list(self.message_cache.keys())
    
    async def get_topic_info(self, topic_name: str) -> Dict[str, Any]:
        """Get information about a topic"""
        if topic_name not in self.message_cache:
            return {}
        
        return {
            "name": topic_name,
            "message_count": len(self.message_cache[topic_name]),
            "metrics": self.metrics.get(topic_name, {}),
            "last_message": list(self.message_cache[topic_name])[-1] if self.message_cache[topic_name] else None
        }
    
    async def get_recent_messages(self, topic_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages from a topic"""
        if topic_name not in self.message_cache:
            return []
        
        messages = list(self.message_cache[topic_name])
        return messages[-limit:]
    
    async def get_topic_metrics(self, topic_name: str) -> Dict[str, Any]:
        """Get metrics for a topic"""
        return self.metrics.get(topic_name, {})
    
    async def get_recent_threats(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent threats"""
        return list(self.profile_cache)[-limit:]
    
    async def get_threat_details(self, threat_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific threat"""
        for threat in self.profile_cache:
            if threat.get("profile_id") == threat_id:
                return threat
        return None
    
    async def get_recent_profiles(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent threat profiles"""
        return list(self.profile_cache)[-limit:]
    
    async def get_recent_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return list(self.alert_cache)[-limit:]
    
    async def get_mitre_mappings(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get MITRE mappings"""
        return list(self.mitre_cache)[-limit:]
    
    async def get_mitre_matrix(self) -> Dict[str, Any]:
        """Get MITRE ATT&CK matrix data"""
        from src.models.mitre import MITRETactic, COMMON_AI_TECHNIQUES
        
        # Count mappings by tactic
        tactic_counts = {}
        for mapping in self.mitre_cache:
            tactic = mapping.get("primary_tactic", "unknown")
            tactic_counts[tactic] = tactic_counts.get(tactic, 0) + 1
        
        return {
            "tactics": [tactic.value for tactic in MITRETactic],
            "techniques": COMMON_AI_TECHNIQUES,
            "mapping_counts": tactic_counts,
            "total_mappings": len(self.mitre_cache)
        }
    
    async def get_live_data(self) -> Dict[str, Any]:
        """Get live data snapshot"""
        return {
            "topics": {
                topic: {
                    "message_count": len(messages),
                    "last_message": list(messages)[-1] if messages else None,
                    "metrics": self.metrics.get(topic, {})
                }
                for topic, messages in self.message_cache.items()
            },
            "threats": {
                "profiles": len(self.profile_cache),
                "alerts": len(self.alert_cache),
                "mitre_mappings": len(self.mitre_cache)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def subscribe_to_threats(self, websocket):
        """Subscribe to threat alerts via WebSocket"""
        try:
            while True:
                # Send new alerts as they arrive
                if self.alert_cache:
                    latest_alert = list(self.alert_cache)[-1]
                    await websocket.send_json({
                        "type": "threat_alert",
                        "data": latest_alert
                    })
                
                await asyncio.sleep(1)
        except Exception as e:
            self.logger.error(f"Error in threat subscription: {e}")


# Singleton instance
_kafka_monitor_instance = None


def get_kafka_monitor() -> Optional[KafkaMonitor]:
    """Get Kafka monitor instance"""
    return _kafka_monitor_instance


def set_kafka_monitor(monitor: KafkaMonitor):
    """Set Kafka monitor instance"""
    global _kafka_monitor_instance
    _kafka_monitor_instance = monitor

