"""
Background Worker: Handles autonomous self-iteration and evolution.

Implements background processing for continuous organism improvement.
"""

import time
import threading
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WorkerTask:
    """Represents a background task."""
    name: str
    function: Callable
    interval: float  # seconds
    enabled: bool = True
    last_run: Optional[datetime] = None
    run_count: int = 0
    

class BackgroundWorker:
    """
    Background worker for autonomous self-iteration and evolution.
    
    Manages periodic tasks that run in the background to enable
    continuous organism improvement and adaptation.
    """
    
    def __init__(self):
        self.tasks: Dict[str, WorkerTask] = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
    def add_task(self, name: str, function: Callable, interval: float) -> None:
        """
        Add a periodic task to the worker.
        
        Args:
            name: Task identifier
            function: Function to call periodically
            interval: Time between executions (seconds)
        """
        with self._lock:
            task = WorkerTask(
                name=name,
                function=function,
                interval=interval
            )
            self.tasks[name] = task
            logger.info(f"Added task '{name}' with interval {interval}s")
            
    def remove_task(self, name: str) -> bool:
        """
        Remove a task from the worker.
        
        Args:
            name: Task identifier
            
        Returns:
            True if task was removed, False if not found
        """
        with self._lock:
            if name in self.tasks:
                del self.tasks[name]
                logger.info(f"Removed task '{name}'")
                return True
            return False
            
    def enable_task(self, name: str) -> bool:
        """Enable a task."""
        with self._lock:
            if name in self.tasks:
                self.tasks[name].enabled = True
                return True
            return False
            
    def disable_task(self, name: str) -> bool:
        """Disable a task without removing it."""
        with self._lock:
            if name in self.tasks:
                self.tasks[name].enabled = False
                return True
            return False
            
    def _worker_loop(self) -> None:
        """Main worker loop that executes tasks."""
        logger.info("Background worker started")
        
        while self.running:
            current_time = datetime.now()
            
            with self._lock:
                for task_name, task in self.tasks.items():
                    if not task.enabled:
                        continue
                        
                    # Check if it's time to run the task
                    should_run = False
                    if task.last_run is None:
                        should_run = True
                    else:
                        elapsed = (current_time - task.last_run).total_seconds()
                        should_run = elapsed >= task.interval
                        
                    if should_run:
                        try:
                            logger.info(f"Executing task '{task_name}'")
                            task.function()
                            task.last_run = current_time
                            task.run_count += 1
                        except Exception as e:
                            logger.error(f"Error in task '{task_name}': {e}")
                            
            # Sleep briefly to avoid busy waiting
            time.sleep(0.1)
            
        logger.info("Background worker stopped")
        
    def start(self) -> None:
        """Start the background worker."""
        if self.running:
            logger.warning("Worker already running")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.thread.start()
        logger.info("Background worker thread started")
        
    def stop(self, timeout: float = 5.0) -> None:
        """
        Stop the background worker.
        
        Args:
            timeout: Maximum time to wait for worker to stop
        """
        if not self.running:
            return
            
        self.running = False
        if self.thread:
            self.thread.join(timeout=timeout)
            self.thread = None
        logger.info("Background worker stopped")
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get current worker status.
        
        Returns:
            Dictionary with worker status information
        """
        with self._lock:
            task_status = []
            for name, task in self.tasks.items():
                task_status.append({
                    'name': name,
                    'enabled': task.enabled,
                    'interval': task.interval,
                    'run_count': task.run_count,
                    'last_run': task.last_run.isoformat() if task.last_run else None
                })
                
            return {
                'running': self.running,
                'num_tasks': len(self.tasks),
                'tasks': task_status
            }
            
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
