"""Kafka consumers for threat processing"""

from .threat_consumer import ThreatConsumer
from .alert_consumer import AlertConsumer

__all__ = ["ThreatConsumer", "AlertConsumer"]


