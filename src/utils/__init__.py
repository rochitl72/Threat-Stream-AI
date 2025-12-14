"""Utility modules"""

from .kafka_utils import get_kafka_producer, get_kafka_consumer
from .logger import setup_logger

__all__ = ["get_kafka_producer", "get_kafka_consumer", "setup_logger"]


