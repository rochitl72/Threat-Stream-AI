#!/usr/bin/env python3
"""
Advanced Threat Data Generator - Main Entry Point
Generates realistic threat data for demonstrations
"""

import sys
import argparse
import signal
import time
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from src.utils.kafka_utils import get_kafka_producer
from scripts.data_generator import (
    TelemetryGenerator,
    CodeGenerator,
    DarkWebGenerator,
    ScenarioEngine
)

# Configure logger
logger.add("logs/data_generator.log", rotation="10 MB", level="INFO")


class DataGeneratorCLI:
    """Command-line interface for data generator"""
    
    def __init__(self):
        """Initialize CLI"""
        self.running = True
        self.generators = []
        # Use shared Kafka producer for all generators
        kafka_producer = get_kafka_producer()
        self.producers = {
            "telemetry": kafka_producer,
            "code": kafka_producer,
            "darkweb": kafka_producer
        }
        self.scenario_engine = ScenarioEngine(self.producers)
    
    def generate_telemetry(
        self,
        count: Optional[int] = None,
        duration: Optional[float] = None,
        pattern: Optional[str] = None,
        rate: float = 2.0
    ):
        """Generate telemetry data"""
        logger.info(f"Starting telemetry generation (count={count}, duration={duration}, pattern={pattern})")
        
        generator = TelemetryGenerator(
            self.producers["telemetry"],
            rate_limit=rate,
            pattern=pattern
        )
        
        generator.start(count=count, duration=duration)
        self.generators.append(generator)
        
        return generator
    
    def generate_code(
        self,
        count: Optional[int] = None,
        duration: Optional[float] = None,
        pattern: Optional[str] = None,
        rate: float = 0.5
    ):
        """Generate code samples"""
        logger.info(f"Starting code generation (count={count}, duration={duration}, pattern={pattern})")
        
        generator = CodeGenerator(
            self.producers["code"],
            rate_limit=rate,
            pattern=pattern
        )
        
        generator.start(count=count, duration=duration)
        self.generators.append(generator)
        
        return generator
    
    def generate_darkweb(
        self,
        count: Optional[int] = None,
        duration: Optional[float] = None,
        pattern: Optional[str] = None,
        rate: float = 0.3
    ):
        """Generate dark web feeds"""
        logger.info(f"Starting dark web generation (count={count}, duration={duration}, pattern={pattern})")
        
        generator = DarkWebGenerator(
            self.producers["darkweb"],
            rate_limit=rate,
            pattern=pattern
        )
        
        generator.start(count=count, duration=duration)
        self.generators.append(generator)
        
        return generator
    
    def generate_all(
        self,
        count: Optional[int] = None,
        duration: Optional[float] = None,
        rate_multiplier: float = 1.0
    ):
        """Generate all data types simultaneously"""
        logger.info("Starting all generators")
        
        self.generate_telemetry(count=count, duration=duration, rate=2.0 * rate_multiplier)
        self.generate_code(count=count, duration=duration, rate=0.5 * rate_multiplier)
        self.generate_darkweb(count=count, duration=duration, rate=0.3 * rate_multiplier)
    
    def run_scenario(self, scenario_name: str, duration: Optional[float] = None):
        """Run a predefined attack scenario"""
        logger.info(f"Running scenario: {scenario_name}")
        self.scenario_engine.run_scenario(scenario_name, duration)
    
    def list_scenarios(self):
        """List available scenarios"""
        scenarios = self.scenario_engine.list_scenarios()
        logger.info("Available scenarios:")
        for scenario in scenarios:
            logger.info(f"  - {scenario}")
        return scenarios
    
    def stop_all(self):
        """Stop all generators"""
        logger.info("Stopping all generators...")
        for generator in self.generators:
            generator.stop()
        self.running = False
    
    def print_stats(self):
        """Print statistics for all generators"""
        logger.info("=" * 60)
        logger.info("Generation Statistics:")
        logger.info("=" * 60)
        
        for i, generator in enumerate(self.generators, 1):
            stats = generator.get_stats()
            logger.info(f"\nGenerator {i} ({generator.__class__.__name__}):")
            logger.info(f"  Messages: {stats['message_count']}")
            logger.info(f"  Elapsed: {stats['elapsed_time']:.2f}s")
            logger.info(f"  Rate: {stats['messages_per_second']:.2f} msg/s")
            logger.info(f"  Running: {stats['running']}")
        
        logger.info("=" * 60)


def signal_handler(sig, frame, cli: DataGeneratorCLI):
    """Handle shutdown signals"""
    logger.info("Shutdown signal received")
    cli.stop_all()
    cli.print_stats()
    sys.exit(0)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Advanced Threat Data Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 100 telemetry events
  python generate_demo_data.py --telemetry --count 100
  
  # Generate all data types for 5 minutes
  python generate_demo_data.py --all --duration 300
  
  # Run a specific scenario
  python generate_demo_data.py --scenario autonomous_hacking_system
  
  # Generate with specific pattern
  python generate_demo_data.py --telemetry --pattern sequential_port_scan --count 50
        """
    )
    
    # Data type selection
    parser.add_argument("--telemetry", action="store_true", help="Generate telemetry data")
    parser.add_argument("--code", action="store_true", help="Generate code samples")
    parser.add_argument("--darkweb", action="store_true", help="Generate dark web feeds")
    parser.add_argument("--all", action="store_true", help="Generate all data types")
    
    # Generation parameters
    parser.add_argument("--count", type=int, help="Number of messages to generate")
    parser.add_argument("--duration", type=float, help="Duration in seconds")
    parser.add_argument("--pattern", type=str, help="Specific pattern to use")
    parser.add_argument("--rate", type=float, default=1.0, help="Rate multiplier")
    
    # Scenario mode
    parser.add_argument("--scenario", type=str, help="Run a predefined scenario")
    parser.add_argument("--list-scenarios", action="store_true", help="List available scenarios")
    
    args = parser.parse_args()
    
    cli = DataGeneratorCLI()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, cli))
    signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s, f, cli))
    
    try:
        if args.list_scenarios:
            cli.list_scenarios()
            return
        
        if args.scenario:
            cli.run_scenario(args.scenario, args.duration)
            return
        
        if args.all:
            cli.generate_all(count=args.count, duration=args.duration, rate_multiplier=args.rate)
        else:
            if args.telemetry:
                cli.generate_telemetry(count=args.count, duration=args.duration, pattern=args.pattern, rate=args.rate * 2.0)
            
            if args.code:
                cli.generate_code(count=args.count, duration=args.duration, pattern=args.pattern, rate=args.rate * 0.5)
            
            if args.darkweb:
                cli.generate_darkweb(count=args.count, duration=args.duration, pattern=args.pattern, rate=args.rate * 0.3)
        
        # Wait for completion or keep running
        if args.duration:
            time.sleep(args.duration + 5)  # Add buffer
        elif args.count:
            # Wait for all generators to finish
            while any(gen.running for gen in cli.generators):
                time.sleep(1)
        else:
            # Run indefinitely until interrupted
            logger.info("Running indefinitely. Press Ctrl+C to stop.")
            while cli.running:
                time.sleep(1)
                # Print stats every 30 seconds
                if int(time.time()) % 30 == 0:
                    cli.print_stats()
        
        cli.print_stats()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        cli.stop_all()


if __name__ == "__main__":
    main()

