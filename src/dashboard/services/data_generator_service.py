"""
Data Generator Service
Programmatic interface for data generation
"""

import asyncio
import subprocess
import threading
from typing import Dict, Any, Optional
from loguru import logger
from pathlib import Path


class DataGeneratorService:
    """Service for triggering data generation from API"""
    
    _instance = None
    
    def __init__(self):
        """Initialize data generator service"""
        self.active_generators = {}  # task_id -> process info
        self.script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "generate_demo_data.py"
        self.logger = logger.bind(component="data_generator_service")
    
    async def generate_all(self, duration: Optional[float] = None, count: Optional[int] = None) -> Dict[str, Any]:
        """Generate all data types"""
        # #region agent log
        import json, time; log_data = {"location": "data_generator_service.py:25", "message": "generate_all called", "data": {"duration": duration, "count": count, "script_path": str(self.script_path), "script_exists": self.script_path.exists()}, "timestamp": time.time() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "L"}; open("/Users/rochitlen/Downloads/animus/.cursor/debug.log", "a").write(json.dumps(log_data) + "\n")
        # #endregion
        
        cmd = ["python", str(self.script_path), "--all"]
        
        if duration:
            cmd.extend(["--duration", str(duration)])
        if count:
            cmd.extend(["--count", str(count)])
        
        # #region agent log
        log_data = {"location": "data_generator_service.py:34", "message": "Command prepared", "data": {"cmd": cmd}, "timestamp": time.time() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "M"}; open("/Users/rochitlen/Downloads/animus/.cursor/debug.log", "a").write(json.dumps(log_data) + "\n")
        # #endregion
        
        return await self._run_generator("generate_all", cmd)
    
    async def generate_telemetry(
        self,
        count: Optional[int] = None,
        duration: Optional[float] = None,
        pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate telemetry data"""
        cmd = ["python", str(self.script_path), "--telemetry"]
        
        if count:
            cmd.extend(["--count", str(count)])
        if duration:
            cmd.extend(["--duration", str(duration)])
        if pattern:
            cmd.extend(["--pattern", pattern])
        
        return await self._run_generator("generate_telemetry", cmd)
    
    async def generate_code(
        self,
        count: Optional[int] = None,
        duration: Optional[float] = None,
        pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate code samples"""
        cmd = ["python", str(self.script_path), "--code"]
        
        if count:
            cmd.extend(["--count", str(count)])
        if duration:
            cmd.extend(["--duration", str(duration)])
        if pattern:
            cmd.extend(["--pattern", pattern])
        
        return await self._run_generator("generate_code", cmd)
    
    async def generate_darkweb(
        self,
        count: Optional[int] = None,
        duration: Optional[float] = None,
        pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate dark web feeds"""
        cmd = ["python", str(self.script_path), "--darkweb"]
        
        if count:
            cmd.extend(["--count", str(count)])
        if duration:
            cmd.extend(["--duration", str(duration)])
        if pattern:
            cmd.extend(["--pattern", pattern])
        
        return await self._run_generator("generate_darkweb", cmd)
    
    async def run_scenario(self, scenario_name: str, duration: Optional[float] = None) -> Dict[str, Any]:
        """Run a predefined attack scenario"""
        cmd = ["python", str(self.script_path), "--scenario", scenario_name]
        
        if duration:
            cmd.extend(["--duration", str(duration)])
        
        return await self._run_generator(f"scenario_{scenario_name}", cmd)
    
    async def list_scenarios(self) -> Dict[str, Any]:
        """List available scenarios"""
        cmd = ["python", str(self.script_path), "--list-scenarios"]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(self.script_path.parent)
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            self.logger.error(f"Error listing scenarios: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _run_generator(self, task_id: str, cmd: list) -> Dict[str, Any]:
        """Run generator command in background"""
        # #region agent log
        import json, time; log_data = {"location": "data_generator_service.py:120", "message": "_run_generator called", "data": {"task_id": task_id, "cmd": cmd, "cwd": str(self.script_path.parent.parent)}, "timestamp": time.time() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "N"}; open("/Users/rochitlen/Downloads/animus/.cursor/debug.log", "a").write(json.dumps(log_data) + "\n")
        # #endregion
        
        try:
            # Check if already running
            if task_id in self.active_generators:
                # #region agent log
                log_data = {"location": "data_generator_service.py:125", "message": "Generator already running", "data": {"task_id": task_id}, "timestamp": time.time() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "O"}; open("/Users/rochitlen/Downloads/animus/.cursor/debug.log", "a").write(json.dumps(log_data) + "\n")
                # #endregion
                return {
                    "success": False,
                    "error": f"Generator '{task_id}' is already running",
                    "task_id": task_id
                }
            
            # #region agent log
            log_data = {"location": "data_generator_service.py:135", "message": "Starting subprocess", "data": {"cmd": cmd, "cwd": str(self.script_path.parent.parent)}, "timestamp": time.time() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "P"}; open("/Users/rochitlen/Downloads/animus/.cursor/debug.log", "a").write(json.dumps(log_data) + "\n")
            # #endregion
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.script_path.parent.parent)
            )
            
            # #region agent log
            log_data = {"location": "data_generator_service.py:145", "message": "Subprocess started", "data": {"pid": process.pid, "returncode": process.returncode}, "timestamp": time.time() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "Q"}; open("/Users/rochitlen/Downloads/animus/.cursor/debug.log", "a").write(json.dumps(log_data) + "\n")
            # #endregion
            
            # Store process info
            self.active_generators[task_id] = {
                "process": process,
                "cmd": " ".join(cmd),
                "started_at": asyncio.get_event_loop().time()
            }
            
            # Monitor process in background
            asyncio.create_task(self._monitor_process(task_id, process))
            
            # #region agent log
            log_data = {"location": "data_generator_service.py:158", "message": "Returning success", "data": {"task_id": task_id, "pid": process.pid}, "timestamp": time.time() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "R"}; open("/Users/rochitlen/Downloads/animus/.cursor/debug.log", "a").write(json.dumps(log_data) + "\n")
            # #endregion
            
            return {
                "success": True,
                "task_id": task_id,
                "message": f"Generator '{task_id}' started",
                "pid": process.pid
            }
            
        except Exception as e:
            # #region agent log
            log_data = {"location": "data_generator_service.py:168", "message": "Exception in _run_generator", "data": {"error": str(e), "error_type": type(e).__name__, "traceback": __import__("traceback").format_exc()[:500]}, "timestamp": time.time() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "S"}; open("/Users/rochitlen/Downloads/animus/.cursor/debug.log", "a").write(json.dumps(log_data) + "\n")
            # #endregion
            self.logger.error(f"Error running generator: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _monitor_process(self, task_id: str, process: subprocess.Popen):
        """Monitor generator process"""
        try:
            # Wait for process to complete
            stdout, stderr = await asyncio.to_thread(process.communicate)
            
            # Remove from active generators
            if task_id in self.active_generators:
                del self.active_generators[task_id]
            
            self.logger.info(f"Generator '{task_id}' completed")
            
        except Exception as e:
            self.logger.error(f"Error monitoring process: {e}")
            if task_id in self.active_generators:
                del self.active_generators[task_id]
    
    def get_active_generators(self) -> Dict[str, Any]:
        """Get list of active generators"""
        active = {}
        for task_id, info in self.active_generators.items():
            process = info["process"]
            if process.poll() is None:  # Still running
                active[task_id] = {
                    "pid": process.pid,
                    "cmd": info["cmd"],
                    "started_at": info["started_at"]
                }
            else:
                # Process finished, remove it
                del self.active_generators[task_id]
        
        return active
    
    def stop_generator(self, task_id: str) -> Dict[str, Any]:
        """Stop a running generator"""
        if task_id not in self.active_generators:
            return {
                "success": False,
                "error": f"Generator '{task_id}' not found"
            }
        
        try:
            process = self.active_generators[task_id]["process"]
            process.terminate()
            
            # Wait a bit, then kill if still running
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            
            del self.active_generators[task_id]
            
            return {
                "success": True,
                "message": f"Generator '{task_id}' stopped"
            }
        except Exception as e:
            self.logger.error(f"Error stopping generator: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
_data_generator_service = None


def get_data_generator_service() -> Optional[DataGeneratorService]:
    """Get data generator service instance"""
    return _data_generator_service


def set_data_generator_service(service: DataGeneratorService):
    """Set data generator service instance"""
    global _data_generator_service
    _data_generator_service = service

