"""
Scenario Engine
Orchestrates multi-stage attack scenarios with correlation
"""

import time
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from .pattern_library import ATTACK_SCENARIOS
from .telemetry_generator import TelemetryGenerator
from .code_generator import CodeGenerator
from .darkweb_generator import DarkWebGenerator


class ScenarioEngine:
    """Orchestrates attack scenarios"""
    
    def __init__(self, producers: Dict[str, Any]):
        """
        Initialize scenario engine
        
        Args:
            producers: Dictionary of producer instances
        """
        self.producers = producers
        self.running = False
        self.active_scenarios = []
        self.logger = logger.bind(component="scenario_engine")
    
    def run_scenario(self, scenario_name: str, duration: Optional[float] = None):
        """
        Run a specific attack scenario
        
        Args:
            scenario_name: Name of scenario to run
            duration: Duration in seconds (None for scenario default)
        """
        scenario = self._get_scenario(scenario_name)
        if not scenario:
            self.logger.error(f"Scenario '{scenario_name}' not found")
            return
        
        self.logger.info(f"Starting scenario: {scenario_name}")
        
        # Create generators for each stage
        generators = []
        for stage in scenario["stages"]:
            gen = self._create_generator_for_stage(stage)
            if gen:
                generators.append(gen)
        
        # Run scenario based on timeline
        if scenario["timeline"] == "sequential":
            self._run_sequential(generators, scenario, duration)
        else:  # parallel
            self._run_parallel(generators, scenario, duration)
    
    def _create_generator_for_stage(self, stage: Dict[str, Any]) -> Optional[Any]:
        """Create generator for a scenario stage"""
        stage_type = stage["type"]
        pattern = stage.get("pattern")
        count = stage.get("count", 10)
        
        if stage_type == "telemetry":
            producer = self.producers.get("telemetry")
            if producer:
                gen = TelemetryGenerator(producer, rate_limit=2.0, pattern=pattern)
                return {"generator": gen, "count": count, "type": "telemetry"}
        
        elif stage_type == "code":
            producer = self.producers.get("code")
            if producer:
                gen = CodeGenerator(producer, rate_limit=0.5, pattern=pattern)
                return {"generator": gen, "count": count, "type": "code"}
        
        elif stage_type == "darkweb":
            producer = self.producers.get("darkweb")
            if producer:
                gen = DarkWebGenerator(producer, rate_limit=0.3, pattern=pattern)
                return {"generator": gen, "count": count, "type": "darkweb"}
        
        return None
    
    def _run_sequential(self, generators: List[Dict], scenario: Dict, duration: Optional[float]):
        """Run scenario stages sequentially"""
        for gen_info in generators:
            gen = gen_info["generator"]
            count = gen_info["count"]
            
            self.logger.info(f"Running {gen_info['type']} stage: {count} messages")
            gen.start(count=count)
            
            # Wait for completion
            while gen.running:
                time.sleep(1)
            
            # Small delay between stages
            time.sleep(2)
    
    def _run_parallel(self, generators: List[Dict], scenario: Dict, duration: Optional[float]):
        """Run scenario stages in parallel"""
        threads = []
        
        for gen_info in generators:
            gen = gen_info["generator"]
            count = gen_info["count"]
            
            thread = threading.Thread(
                target=self._run_generator,
                args=(gen, count, duration),
                daemon=True
            )
            thread.start()
            threads.append(thread)
        
        # Wait for all threads
        for thread in threads:
            thread.join()
    
    def _run_generator(self, generator: Any, count: int, duration: Optional[float]):
        """Run a generator in a thread"""
        generator.start(count=count, duration=duration)
        while generator.running:
            time.sleep(1)
    
    def _get_scenario(self, name: str) -> Optional[Dict[str, Any]]:
        """Get scenario by name"""
        for scenario in ATTACK_SCENARIOS:
            if scenario["name"] == name:
                return scenario
        return None
    
    def list_scenarios(self) -> List[str]:
        """List available scenarios"""
        return [s["name"] for s in ATTACK_SCENARIOS]

