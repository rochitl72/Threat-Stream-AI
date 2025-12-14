"""
Base Generator Class
Abstract base class for all data generators
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import threading
from datetime import datetime
from loguru import logger


class BaseGenerator(ABC):
    """Base class for all data generators"""
    
    def __init__(self, producer, rate_limit: float = 1.0):
        """
        Initialize base generator
        
        Args:
            producer: Kafka producer instance
            rate_limit: Messages per second
        """
        self.producer = producer
        self.rate_limit = rate_limit
        self.running = False
        self.thread = None
        self.message_count = 0
        self.start_time = None
        self.logger = logger.bind(component="data_generator")
    
    @abstractmethod
    def generate(self) -> Dict[str, Any]:
        """
        Generate a single data record
        
        Returns:
            Dictionary containing the generated data
        """
        pass
    
    def produce(self, data: Dict[str, Any]) -> bool:
        """
        Produce data to Kafka
        
        Args:
            data: Data dictionary to produce
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add timestamp if not present
            if "timestamp" not in data:
                data["timestamp"] = datetime.utcnow().isoformat()
            
            # Call abstract method to get topic-specific production logic
            success = self._produce_data(data)
            
            if success:
                self.message_count += 1
                if self.message_count % 10 == 0:
                    self.logger.info(f"Generated {self.message_count} messages")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error producing data: {e}")
            return False
    
    @abstractmethod
    def _produce_data(self, data: Dict[str, Any]) -> bool:
        """
        Produce data to specific Kafka topic
        
        Args:
            data: Data dictionary
            
        Returns:
            True if successful
        """
        pass
    
    def start(self, duration: Optional[float] = None, count: Optional[int] = None):
        """
        Start generating data
        
        Args:
            duration: Duration in seconds (None for infinite)
            count: Number of messages to generate (None for infinite)
        """
        if self.running:
            self.logger.warning("Generator already running")
            return
        
        self.running = True
        self.start_time = time.time()
        self.message_count = 0
        
        self.thread = threading.Thread(
            target=self._run_loop,
            args=(duration, count),
            daemon=True
        )
        self.thread.start()
        self.logger.info(f"Started {self.__class__.__name__}")
    
    def _run_loop(self, duration: Optional[float], count: Optional[int]):
        """Internal run loop"""
        end_time = time.time() + duration if duration else None
        interval = 1.0 / self.rate_limit if self.rate_limit > 0 else 0
        
        while self.running:
            # Check duration limit
            if end_time and time.time() >= end_time:
                self.logger.info("Duration limit reached")
                break
            
            # Check count limit
            if count and self.message_count >= count:
                self.logger.info("Count limit reached")
                break
            
            # Generate and produce data
            data = self.generate()
            if data:
                self.produce(data)
            
            # Rate limiting
            if interval > 0:
                time.sleep(interval)
    
    def stop(self):
        """Stop generating data"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.logger.info(f"Stopped {self.__class__.__name__}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get generation statistics"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        rate = self.message_count / elapsed if elapsed > 0 else 0
        
        return {
            "message_count": self.message_count,
            "elapsed_time": elapsed,
            "messages_per_second": rate,
            "running": self.running
        }

