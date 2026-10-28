"""
OASIS Simulation Runner
Runs simulations in the background and records Agent actions with real-time monitoring
"""

import os
import sys
import json
import time
import asyncio
import threading
import subprocess
import signal
import atexit
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from queue import Queue

from ..config import Config
from ..utils.logger import get_logger
from ..utils.locale import get_locale, set_locale
from ..utils.zep import (
    ZEP_HTTP_REQUEST_TIMEOUT_SECONDS,
    ZEP_INGESTION_WAIT_TIMEOUT_SECONDS,
)
from .zep_graph_memory_updater import ZepGraphMemoryManager
from .simulation_ipc import SimulationIPCClient, CommandType, IPCResponse

logger = get_logger('lokantra.simulation_runner')

# Flag tracking if cleanup handlers are registered
_cleanup_registered = False

# Platform detection
IS_WINDOWS = sys.platform == 'win32'


class RunnerStatus(str, Enum):
    """Runner status"""
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationStopPending(TimeoutError):
    """The monitor still owns a bounded graph-ingestion finalization."""


@dataclass
class AgentAction:
    """Agent action record"""
    round_num: int
    timestamp: str
    platform: str  # twitter / reddit
    agent_id: int
    agent_name: str
    action_type: str  # CREATE_POST, LIKE_POST, etc.
    action_args: Dict[str, Any] = field(default_factory=dict)
    result: Optional[str] = None
    success: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "round_num": self.round_num,
            "timestamp": self.timestamp,
            "platform": self.platform,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "action_type": self.action_type,
            "action_args": self.action_args,
            "result": self.result,
            "success": self.success,
        }


@dataclass
class RoundSummary:
    """Round summary"""
    round_num: int
    start_time: str
    end_time: Optional[str] = None
    simulated_hour: int = 0
    twitter_actions: int = 0
    reddit_actions: int = 0
    active_agents: List[int] = field(default_factory=list)
    actions: List[AgentAction] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "round_num": self.round_num,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "simulated_hour": self.simulated_hour,
            "twitter_actions": self.twitter_actions,
            "reddit_actions": self.reddit_actions,
            "active_agents": self.active_agents,
            "actions_count": len(self.actions),
            "actions": [a.to_dict() for a in self.actions],
        }


@dataclass
class SimulationRunState:
    """Simulation run state (real-time)"""
    simulation_id: str
    runner_status: RunnerStatus = RunnerStatus.IDLE
    
    # Progress info
    current_round: int = 0
    total_rounds: int = 0
    simulated_hours: int = 0
    total_simulation_hours: int = 0
    
    # Per-platform round and simulated time (for parallel dual-platform display)
    twitter_current_round: int = 0
    reddit_current_round: int = 0
    twitter_simulated_hours: int = 0
    reddit_simulated_hours: int = 0
    
    # Platform status
    twitter_running: bool = False
    reddit_running: bool = False
    twitter_actions_count: int = 0
    reddit_actions_count: int = 0
    
    # Platform completion status (detected via simulation_end events in actions.jsonl)
    twitter_completed: bool = False
    reddit_completed: bool = False
    
    # Round summaries
    rounds: List[RoundSummary] = field(default_factory=list)
    
    # Recent actions (for real-time frontend display)
    recent_actions: List[AgentAction] = field(default_factory=list)
    max_recent_actions: int = 50
    
    # Timestamps
    started_at: Optional[str] = None
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    
    # Error info
    error: Optional[str] = None
    
    # Process ID (for termination)
    process_pid: Optional[int] = None
    
    def add_action(self, action: AgentAction):
        """Add action to recent actions list"""
        self.recent_actions.insert(0, action)
        if len(self.recent_actions) > self.max_recent_actions:
            self.recent_actions = self.recent_actions[:self.max_recent_actions]
        
        if action.platform == "twitter":
            self.twitter_actions_count += 1
        else:
            self.reddit_actions_count += 1
        
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "runner_status": self.runner_status.value,
            "current_round": self.current_round,
            "total_rounds": self.total_rounds,
            "simulated_hours": self.simulated_hours,
            "total_simulation_hours": self.total_simulation_hours,
            "progress_percent": round(self.current_round / max(self.total_rounds, 1) * 100, 1),
            # Independent rounds and timestamps per platform
            "twitter_current_round": self.twitter_current_round,
            "reddit_current_round": self.reddit_current_round,
            "twitter_simulated_hours": self.twitter_simulated_hours,
            "reddit_simulated_hours": self.reddit_simulated_hours,
            "twitter_running": self.twitter_running,
            "reddit_running": self.reddit_running,
            "twitter_completed": self.twitter_completed,
            "reddit_completed": self.reddit_completed,
            "twitter_actions_count": self.twitter_actions_count,
            "reddit_actions_count": self.reddit_actions_count,
            "total_actions_count": self.twitter_actions_count + self.reddit_actions_count,
            "started_at": self.started_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "error": self.error,
            "process_pid": self.process_pid,
        }
    
    def to_detail_dict(self) -> Dict[str, Any]:
        """Detailed info including recent actions and cognitive telemetry"""
        result = self.to_dict()
        result["recent_actions"] = [a.to_dict() for a in self.recent_actions]
        result["rounds_count"] = len(self.rounds)
        
        # Attach cognitive swarm router telemetry if available
        telemetry_file = os.path.join(os.path.dirname(__file__), '../../uploads/simulations', self.simulation_id, 'telemetry.json')
        if os.path.exists(telemetry_file):
            try:
                with open(telemetry_file, 'r', encoding='utf-8') as tf:
                    result["cognitive_telemetry"] = json.load(tf)
            except Exception:
                pass
                
        return result


class SimulationRunner:
    """
    Simulation Runner
    
    Responsible for:
    1. Running OASIS simulations in background processes
    2. Parsing execution logs and recording Agent actions
    3. Providing real-time state query endpoints
    4. Supporting pause/stop/resume operations
    """
    
    # Runtime state storage directory
    RUN_STATE_DIR = os.path.join(
        os.path.dirname(__file__),
        '../../uploads/simulations'
    )
    
    # Scripts directory
    SCRIPTS_DIR = os.path.join(
        os.path.dirname(__file__),
        '../../scripts'
    )
    
    # In-memory runtime states
    _run_states: Dict[str, SimulationRunState] = {}
    _processes: Dict[str, subprocess.Popen] = {}
    _action_queues: Dict[str, Queue] = {}
    _monitor_threads: Dict[str, threading.Thread] = {}
    _stdout_files: Dict[str, Any] = {}  # stdout file handles
    _stderr_files: Dict[str, Any] = {}  # stderr file handles
    
    # Graph memory update configuration
    _graph_memory_enabled: Dict[str, bool] = {}  # simulation_id -> enabled
    _finalization_locks: Dict[str, threading.Lock] = {}
    _finalization_locks_guard = threading.Lock()
    _manual_stop_requests: set[str] = set()

    @classmethod
    def _finalization_lock(cls, simulation_id: str) -> threading.Lock:
        with cls._finalization_locks_guard:
            return cls._finalization_locks.setdefault(
                simulation_id, threading.Lock()
            )

    @classmethod
    def _sync_simulation_status(
        cls,
        simulation_id: str,
        runner_status: RunnerStatus,
        error: str | None = None,
    ) -> None:
        """Keep persisted simulation metadata aligned with run_state.json."""

        from .simulation_manager import SimulationManager, SimulationStatus

        status_map = {
            RunnerStatus.RUNNING: SimulationStatus.RUNNING,
            RunnerStatus.STOPPING: SimulationStatus.STOPPING,
            RunnerStatus.STOPPED: SimulationStatus.STOPPED,
            RunnerStatus.COMPLETED: SimulationStatus.COMPLETED,
            RunnerStatus.FAILED: SimulationStatus.FAILED,
        }
        status = status_map.get(runner_status)
        if status is None:
            return
        try:
            manager = SimulationManager()
            simulation = manager.get_simulation(simulation_id)
            if simulation is None:
                return
            simulation.status = status
            simulation.error = error
            manager._save_simulation_state(simulation)
        except Exception as sync_error:
            # state.json is a secondary projection. Never let a projection
            # failure skip the authoritative run-state finalization or Zep
            # ingestion drain.
            logger.error(
                "Failed to synchronize simulation state: simulation_id=%s, status=%s, error=%s",
                simulation_id,
                runner_status.value,
                sync_error,
            )
    
    @classmethod
    def get_run_state(cls, simulation_id: str) -> Optional[SimulationRunState]:
        """Get runtime state"""
        if simulation_id in cls._run_states:
            return cls._run_states[simulation_id]
        
        # Attempt loading from file
        state = cls._load_run_state(simulation_id)
        if state:
            cls._run_states[simulation_id] = state
        return state
    
    @classmethod
    def _load_run_state(cls, simulation_id: str) -> Optional[SimulationRunState]:
        """Load runtime state from file"""
        state_file = os.path.join(cls.RUN_STATE_DIR, simulation_id, "run_state.json")
        if not os.path.exists(state_file):
            return None
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            state = SimulationRunState(
                simulation_id=simulation_id,
                runner_status=RunnerStatus(data.get("runner_status", "idle")),
                current_round=data.get("current_round", 0),
                total_rounds=data.get("total_rounds", 0),
                simulated_hours=data.get("simulated_hours", 0),
                total_simulation_hours=data.get("total_simulation_hours", 0),
                # Independent rounds and timestamps per platform
                twitter_current_round=data.get("twitter_current_round", 0),
                reddit_current_round=data.get("reddit_current_round", 0),
                twitter_simulated_hours=data.get("twitter_simulated_hours", 0),
                reddit_simulated_hours=data.get("reddit_simulated_hours", 0),
                twitter_running=data.get("twitter_running", False),
                reddit_running=data.get("reddit_running", False),
                twitter_completed=data.get("twitter_completed", False),
                reddit_completed=data.get("reddit_completed", False),
                twitter_actions_count=data.get("twitter_actions_count", 0),
                reddit_actions_count=data.get("reddit_actions_count", 0),
                started_at=data.get("started_at"),
                updated_at=data.get("updated_at", datetime.now().isoformat()),
                completed_at=data.get("completed_at"),
                error=data.get("error"),
                process_pid=data.get("process_pid"),
            )
            
            # Load recent actions
            actions_data = data.get("recent_actions", [])
            for a in actions_data:
                state.recent_actions.append(AgentAction(
                    round_num=a.get("round_num", 0),
                    timestamp=a.get("timestamp", ""),
                    platform=a.get("platform", ""),
                    agent_id=a.get("agent_id", 0),
                    agent_name=a.get("agent_name", ""),
                    action_type=a.get("action_type", ""),
                    action_args=a.get("action_args", {}),
                    result=a.get("result"),
                    success=a.get("success", True),
                ))
            
            return state
        except Exception as e:
            logger.error(f"Failed to load runtime state: {str(e)}")
            return None
    
    @classmethod
    def _save_run_state(cls, state: SimulationRunState):
        """Save runtime state to file"""
        sim_dir = os.path.join(cls.RUN_STATE_DIR, state.simulation_id)
        os.makedirs(sim_dir, exist_ok=True)
        state_file = os.path.join(sim_dir, "run_state.json")
        
        data = state.to_detail_dict()
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        cls._run_states[state.simulation_id] = state
    
    @classmethod
    def start_simulation(
        cls,
        simulation_id: str,
        platform: str = "parallel",  # twitter / reddit / parallel
        max_rounds: int = None,  # Maximum simulation rounds (optional, caps duration)
        enable_graph_memory_update: bool = False,  # Whether to update activities to Zep graph
        graph_id: str = None  # Zep graph ID (required when graph update enabled)
    ) -> SimulationRunState:
        """
        Start simulation
        
        Args:
            simulation_id: Simulation ID
            platform: Execution platform (twitter/reddit/parallel)
            max_rounds: Maximum simulation rounds (optional, caps duration)
            enable_graph_memory_update: Whether to dynamically update Agent activities into Zep graph
            graph_id: Zep graph ID (required when graph update enabled)
            
        Returns:
            SimulationRunState
        """
        # Load simulation config
        sim_dir = os.path.join(cls.RUN_STATE_DIR, simulation_id)
        config_path = os.path.join(sim_dir, "simulation_config.json")
        
        if not os.path.exists(config_path):
            raise ValueError("Simulation configuration does not exist; call /prepare endpoint first")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Initialize runtime state
        time_config = config.get("time_config", {})
        total_hours = time_config.get("total_simulation_hours", 72)
        minutes_per_round = time_config.get("minutes_per_round", 30)
        total_rounds = int(total_hours * 60 / minutes_per_round)
        
        # Truncate if max_rounds specified
        if max_rounds is not None and max_rounds > 0:
            original_rounds = total_rounds
            total_rounds = min(total_rounds, max_rounds)
            if total_rounds < original_rounds:
                logger.info(f"Rounds truncated: {original_rounds} -> {total_rounds} (max_rounds={max_rounds})")
        
        state = SimulationRunState(
            simulation_id=simulation_id,
            runner_status=RunnerStatus.STARTING,
            total_rounds=total_rounds,
            total_simulation_hours=total_hours,
            started_at=datetime.now().isoformat(),
        )
        
        # Atomically claim this simulation ID. The expensive updater/process
        # startup happens after releasing the lock, while the persisted
        # STARTING state makes every concurrent start fail closed.
        with cls._finalization_lock(simulation_id):
            existing = cls.get_run_state(simulation_id)
            active_statuses = {
                RunnerStatus.STARTING,
                RunnerStatus.RUNNING,
                RunnerStatus.PAUSED,
                RunnerStatus.STOPPING,
            }
            if (
                existing and existing.runner_status in active_statuses
            ) or ZepGraphMemoryManager.get_updater(simulation_id) is not None:
                raise ValueError(f"Simulation is already running or finalizing: {simulation_id}")
            cls._save_run_state(state)
        
        # If graph memory update is enabled, create updater
        if enable_graph_memory_update:
            if not graph_id:
                raise ValueError("graph_id must be provided when graph memory update is enabled")
            
            try:
                ZepGraphMemoryManager.create_updater(simulation_id, graph_id)
                cls._graph_memory_enabled[simulation_id] = True
                logger.info(f"Graph memory update enabled: simulation_id={simulation_id}, graph_id={graph_id}")
            except Exception as e:
                logger.error(f"Failed to create graph memory updater: {e}")
                cls._graph_memory_enabled[simulation_id] = False
                state.runner_status = RunnerStatus.FAILED
                state.error = f"Zep graph updater initialization failed: {e}"
                with cls._finalization_lock(simulation_id):
                    cls._save_run_state(state)
                    cls._sync_simulation_status(
                        simulation_id,
                        RunnerStatus.FAILED,
                        state.error,
                    )
                raise RuntimeError(state.error) from e
        else:
            cls._graph_memory_enabled[simulation_id] = False
        
        # Determine which script to run (located in backend/scripts/ directory)
        if platform == "twitter":
            script_name = "run_twitter_simulation.py"
            state.twitter_running = True
        elif platform == "reddit":
            script_name = "run_reddit_simulation.py"
            state.reddit_running = True
        else:
            script_name = "run_parallel_simulation.py"
            state.twitter_running = True
            state.reddit_running = True
        
        script_path = os.path.join(cls.SCRIPTS_DIR, script_name)
        
        if not os.path.exists(script_path):
            cleanup_error = None
            if cls._graph_memory_enabled.get(simulation_id, False):
                try:
                    ZepGraphMemoryManager.stop_updater(simulation_id)
                    cls._graph_memory_enabled.pop(simulation_id, None)
                except Exception as error:
                    cleanup_error = error
            state.runner_status = RunnerStatus.FAILED
            state.twitter_running = False
            state.reddit_running = False
            state.error = f"Script does not exist: {script_path}"
            if cleanup_error is not None:
                state.error += f"; Zep graph cleanup failed: {cleanup_error}"
            with cls._finalization_lock(simulation_id):
                cls._save_run_state(state)
                cls._sync_simulation_status(
                    simulation_id,
                    RunnerStatus.FAILED,
                    state.error,
                )
            raise ValueError(state.error)
        
        # Create action queue
        action_queue = Queue()
        cls._action_queues[simulation_id] = action_queue

        process = None
        main_log_file = None

        # Start simulation process
        try:
            # Build run command with absolute paths
            # New log structure:
            #   twitter/actions.jsonl - Twitter action log
            #   reddit/actions.jsonl  - Reddit action log
            #   simulation.log        - Main process log
            
            cmd = [
                sys.executable,  # Python interpreter
                script_path,
                "--config", config_path,  # Use complete config file path
            ]
            
            # If max_rounds specified, append to command line args
            if max_rounds is not None and max_rounds > 0:
                cmd.extend(["--max-rounds", str(max_rounds)])
            
            # Create main log file to prevent process blocking from pipe buffer overflow
            main_log_path = os.path.join(sim_dir, "simulation.log")
            main_log_file = open(main_log_path, 'w', encoding='utf-8')
            
            # Set child process environment variables to ensure UTF-8 encoding on Windows
            # This fixes issues where third-party libraries (e.g., OASIS) read files without specifying encoding
            env = os.environ.copy()
            env['PYTHONUTF8'] = '1'  # Force open() default UTF-8
            env['PYTHONIOENCODING'] = 'utf-8'  # Ensure stdout/stderr uses UTF-8
            
            # Set working directory to simulation folder (databases created here)
            # Use start_new_session=True to ensure child process group termination
            process = subprocess.Popen(
                cmd,
                cwd=sim_dir,
                stdout=main_log_file,
                stderr=subprocess.STDOUT,  # Redirect stderr to same file
                text=True,
                encoding='utf-8',  # Explicitly specify encoding
                bufsize=1,
                env=env,  # Pass environment variables with UTF-8 configuration
                start_new_session=True,  # Create process group to ensure clean termination on shutdown
            )
            
            # Capture locale before spawning monitor thread
            current_locale = get_locale()

            monitor_thread = threading.Thread(
                target=cls._monitor_simulation,
                args=(simulation_id, current_locale),
                daemon=True
            )

            # Atomically publish every resource needed by stop/finalization.
            # The monitor is registered before start; if it exits immediately,
            # it waits on the same lock until RUNNING is fully visible.
            with cls._finalization_lock(simulation_id):
                cls._stdout_files[simulation_id] = main_log_file
                cls._stderr_files[simulation_id] = None
                state.process_pid = process.pid
                state.runner_status = RunnerStatus.RUNNING
                cls._processes[simulation_id] = process
                cls._monitor_threads[simulation_id] = monitor_thread
                cls._save_run_state(state)
                cls._sync_simulation_status(
                    simulation_id,
                    RunnerStatus.RUNNING,
                )
                monitor_thread.start()
            
            logger.info(f"Simulation started successfully: {simulation_id}, pid={process.pid}, platform={platform}")
            
        except Exception as e:
            cleanup_errors = []
            if process is not None and process.poll() is None:
                try:
                    cls._terminate_process(process, simulation_id)
                except Exception as error:
                    cleanup_errors.append(f"Failed to terminate child process: {error}")
            cls._processes.pop(simulation_id, None)
            cls._monitor_threads.pop(simulation_id, None)
            cls._action_queues.pop(simulation_id, None)
            cls._stdout_files.pop(simulation_id, None)
            cls._stderr_files.pop(simulation_id, None)
            if main_log_file is not None:
                try:
                    main_log_file.close()
                except Exception as error:
                    cleanup_errors.append(f"Failed to close log handle: {error}")
            if cls._graph_memory_enabled.get(simulation_id, False):
                try:
                    ZepGraphMemoryManager.stop_updater(simulation_id)
                    cls._graph_memory_enabled.pop(simulation_id, None)
                except Exception as error:
                    cleanup_errors.append(f"Failed to clean up Zep graph writes: {error}")
            state.runner_status = RunnerStatus.FAILED
            state.twitter_running = False
            state.reddit_running = False
            state.error = str(e)
            if cleanup_errors:
                state.error += "; " + "; ".join(cleanup_errors)
            with cls._finalization_lock(simulation_id):
                cls._save_run_state(state)
                cls._sync_simulation_status(
                    simulation_id,
                    RunnerStatus.FAILED,
                    state.error,
                )
            raise
        
        return state
    
    @classmethod
    def _monitor_simulation(cls, simulation_id: str, locale: str = 'zh'):
        """Monitor simulation process and parse action logs"""
        set_locale(locale)
        sim_dir = os.path.join(cls.RUN_STATE_DIR, simulation_id)
        
        # Action logs grouped by platform
        twitter_actions_log = os.path.join(sim_dir, "twitter", "actions.jsonl")
        reddit_actions_log = os.path.join(sim_dir, "reddit", "actions.jsonl")
        
        process = cls._processes.get(simulation_id)
        state = cls.get_run_state(simulation_id)
        
        if not process or not state:
            return
        
        twitter_position = 0
        reddit_position = 0
        close_requested = False

        monitor_error: Exception | None = None
        exit_code: int | None = None
        try:
            while process.poll() is None:  # Process is running
                # Read Twitter action log
                if os.path.exists(twitter_actions_log):
                    twitter_position = cls._read_action_log(
                        twitter_actions_log, twitter_position, state, "twitter"
                    )
                
                # Read Reddit action log
                if os.path.exists(reddit_actions_log):
                    reddit_position = cls._read_action_log(
                        reddit_actions_log, reddit_position, state, "reddit"
                    )

                # The preset scripts remain alive after the platform simulations
                # finish so they can accept interview commands. Once all
                # simulation_end events have been observed, close that command
                # loop so the process can reach the normal completion path.
                if (
                    not close_requested
                    and cls._check_all_platforms_completed(state)
                    and simulation_id not in cls._manual_stop_requests
                ):
                    close_requested = True
                    try:
                        response = SimulationIPCClient(sim_dir).send_close_env(
                            timeout=10.0
                        )
                        if response.status.value != "completed":
                            logger.warning(
                                "Close environment command was not completed: "
                                "simulation_id=%s, status=%s, error=%s",
                                simulation_id,
                                response.status.value,
                                response.error,
                            )
                    except Exception as error:
                        # The process may already be exiting; the monitor will
                        # still observe that exit and finalize the run.
                        logger.warning(
                            "Failed to request environment shutdown: "
                            "simulation_id=%s, error=%s",
                            simulation_id,
                            error,
                        )

                # Update status
                cls._save_run_state(state)
                time.sleep(2)
            
            # Read logs one last time after process terminates
            if os.path.exists(twitter_actions_log):
                cls._read_action_log(twitter_actions_log, twitter_position, state, "twitter")
            if os.path.exists(reddit_actions_log):
                cls._read_action_log(reddit_actions_log, reddit_position, state, "reddit")
            
            exit_code = process.returncode
            
        except Exception as e:
            logger.error(f"Monitor thread exception: {simulation_id}, error={str(e)}")
            monitor_error = e
        
        finally:
            # Manual stop and natural completion can observe the same process
            # exit. Serialize terminal state and updater drain so only one path
            # owns the final result.
            with cls._finalization_lock(simulation_id):
                latest_state = cls.get_run_state(simulation_id)
                if latest_state is not None:
                    state = latest_state

                if state.runner_status not in {
                    RunnerStatus.STOPPED,
                    RunnerStatus.FAILED,
                }:
                    manual_stop = simulation_id in cls._manual_stop_requests
                    desired_status = (
                        RunnerStatus.STOPPED
                        if manual_stop
                        else RunnerStatus.COMPLETED
                    )
                    error_message = None
                    if not manual_stop and monitor_error is not None:
                        desired_status = RunnerStatus.FAILED
                        error_message = str(monitor_error)
                    elif not manual_stop and exit_code != 0:
                        desired_status = RunnerStatus.FAILED
                        main_log_path = os.path.join(sim_dir, "simulation.log")
                        error_info = ""
                        try:
                            if os.path.exists(main_log_path):
                                with open(main_log_path, 'r', encoding='utf-8') as f:
                                    error_info = f.read()[-2000:]
                        except Exception:
                            pass
                        error_message = (
                            f"Process exit code: {exit_code}, error: {error_info}"
                        )

                    state.twitter_running = False
                    state.reddit_running = False

                    if cls._graph_memory_enabled.get(simulation_id, False):
                        # STOPPING is a non-terminal ingestion barrier. The UI
                        # and report API must not observe COMPLETED until every
                        # accepted episode is processed by Zep Cloud.
                        state.runner_status = RunnerStatus.STOPPING
                        cls._save_run_state(state)
                        cls._sync_simulation_status(
                            simulation_id,
                            RunnerStatus.STOPPING,
                        )
                        try:
                            ZepGraphMemoryManager.stop_updater(simulation_id)
                            cls._graph_memory_enabled.pop(simulation_id, None)
                            logger.info(
                                "Stopped graph memory updates: simulation_id=%s",
                                simulation_id,
                            )
                        except TimeoutError as timeout_err:
                            logger.warning(
                                f"Graph memory ingestion wait timed out for simulation {simulation_id}: {timeout_err}. "
                                f"All batches were submitted to Zep Cloud and will complete indexing asynchronously. "
                                f"Marking simulation as completed."
                            )
                            ZepGraphMemoryManager.force_remove_updater(simulation_id)
                            cls._graph_memory_enabled.pop(simulation_id, None)
                            desired_status = (
                                RunnerStatus.STOPPED
                                if simulation_id in cls._manual_stop_requests
                                else RunnerStatus.COMPLETED
                            )
                            error_message = None
                        except Exception as error:
                            logger.error(f"Failed to stop graph memory updater: {error}")
                            desired_status = RunnerStatus.FAILED
                            error_message = f"Zep graph writes incomplete: {error}"

                    state.runner_status = desired_status
                    state.error = error_message
                    state.completed_at = datetime.now().isoformat()
                    cls._save_run_state(state)
                    cls._sync_simulation_status(
                        simulation_id,
                        desired_status,
                        error_message,
                    )
                    if desired_status == RunnerStatus.COMPLETED:
                        logger.info(f"Simulation completed: {simulation_id}")
                    else:
                        logger.error(f"Simulation failed: {simulation_id}, error={state.error}")
                cls._manual_stop_requests.discard(simulation_id)
            
            # Clean up process resources
            cls._processes.pop(simulation_id, None)
            cls._action_queues.pop(simulation_id, None)
            cls._monitor_threads.pop(simulation_id, None)
            
            # Close log file handles
            if simulation_id in cls._stdout_files:
                try:
                    cls._stdout_files[simulation_id].close()
                except Exception:
                    pass
                cls._stdout_files.pop(simulation_id, None)
            if simulation_id in cls._stderr_files and cls._stderr_files[simulation_id]:
                try:
                    cls._stderr_files[simulation_id].close()
                except Exception:
                    pass
                cls._stderr_files.pop(simulation_id, None)
    
    @classmethod
    def _read_action_log(
        cls, 
        log_path: str, 
        position: int, 
        state: SimulationRunState,
        platform: str
    ) -> int:
        """
        Read action log file
        
        Args:
            log_path: Log file path
            position: Previous read position
            state: Run state object
            platform: Platform name (twitter/reddit)
            
        Returns:
            New read position
        """
        # Check if graph memory updating is enabled
        graph_memory_enabled = cls._graph_memory_enabled.get(state.simulation_id, False)
        graph_updater = None
        if graph_memory_enabled:
            graph_updater = ZepGraphMemoryManager.get_updater(state.simulation_id)
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                f.seek(position)
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            action_data = json.loads(line)
                            
                            # Process event-type entries
                            if "event_type" in action_data:
                                event_type = action_data.get("event_type")
                                
                                # Detect simulation_end event and mark platform completed
                                if event_type == "simulation_end":
                                    if platform == "twitter":
                                        state.twitter_completed = True
                                        state.twitter_running = False
                                        logger.info(f"Twitter simulation completed: {state.simulation_id}, total_rounds={action_data.get('total_rounds')}, total_actions={action_data.get('total_actions')}")
                                    elif platform == "reddit":
                                        state.reddit_completed = True
                                        state.reddit_running = False
                                        logger.info(f"Reddit simulation completed: {state.simulation_id}, total_rounds={action_data.get('total_rounds')}, total_actions={action_data.get('total_actions')}")
                                    
                                    # Check if all enabled platforms have completed
                                    # If only one platform is running, check only that platform
                                    # If both platforms are running, both must complete
                                    all_completed = cls._check_all_platforms_completed(state)
                                    if all_completed:
                                        # Platform completion is only an input
                                        # signal. The monitor publishes the
                                        # terminal status after the process has
                                        # exited and Zep ingestion has drained.
                                        logger.info(
                                            f"All platforms completed, waiting for process and graph memory ingestion: "
                                            f"{state.simulation_id}"
                                        )
                                
                                # Update round info (from round_end event)
                                elif event_type == "round_end":
                                    round_num = action_data.get("round", 0)
                                    simulated_hours = action_data.get("simulated_hours", 0)
                                    
                                    # Update separate round and time for each platform
                                    if platform == "twitter":
                                        if round_num > state.twitter_current_round:
                                            state.twitter_current_round = round_num
                                        state.twitter_simulated_hours = simulated_hours
                                    elif platform == "reddit":
                                        if round_num > state.reddit_current_round:
                                            state.reddit_current_round = round_num
                                        state.reddit_simulated_hours = simulated_hours
                                    
                                    # Overall round takes the max of both platforms
                                    if round_num > state.current_round:
                                        state.current_round = round_num
                                    # Overall time takes the max of both platforms
                                    state.simulated_hours = max(state.twitter_simulated_hours, state.reddit_simulated_hours)
                                
                                continue
                            
                            action = AgentAction(
                                round_num=action_data.get("round", 0),
                                timestamp=action_data.get("timestamp", datetime.now().isoformat()),
                                platform=platform,
                                agent_id=action_data.get("agent_id", 0),
                                agent_name=action_data.get("agent_name", ""),
                                action_type=action_data.get("action_type", ""),
                                action_args=action_data.get("action_args", {}),
                                result=action_data.get("result"),
                                success=action_data.get("success", True),
                            )
                            state.add_action(action)
                            
                            # Update round
                            if action.round_num and action.round_num > state.current_round:
                                state.current_round = action.round_num
                            
                            # If graph memory update is enabled, send activities to Zep
                            if graph_updater:
                                graph_updater.add_activity_from_dict(action_data, platform)
                            
                        except json.JSONDecodeError:
                            pass
                return f.tell()
        except Exception as e:
            logger.warning(f"Failed to read action log: {log_path}, error={e}")
            return position
    
    @classmethod
    def _check_all_platforms_completed(cls, state: SimulationRunState) -> bool:
        """
        Check if all enabled platforms have completed simulation.
        
        Determines if a platform is enabled by checking if the corresponding actions.jsonl file exists.
        
        Returns:
            True if all enabled platforms are completed
        """
        sim_dir = os.path.join(cls.RUN_STATE_DIR, state.simulation_id)
        twitter_log = os.path.join(sim_dir, "twitter", "actions.jsonl")
        reddit_log = os.path.join(sim_dir, "reddit", "actions.jsonl")
        
        # Check which platforms are enabled (determined by file existence)
        twitter_enabled = os.path.exists(twitter_log)
        reddit_enabled = os.path.exists(reddit_log)
        
        # If a platform is enabled but not completed, return False
        if twitter_enabled and not state.twitter_completed:
            return False
        if reddit_enabled and not state.reddit_completed:
            return False
        
        # At least one platform is enabled and completed
        return twitter_enabled or reddit_enabled
    
    @classmethod
    def _terminate_process(cls, process: subprocess.Popen, simulation_id: str, timeout: int = 10):
        """
        Cross-platform termination of a process and its child processes.
        
        Args:
            process: Process to terminate
            simulation_id: Simulation ID (for logging)
            timeout: Timeout in seconds waiting for process exit
        """
        if IS_WINDOWS:
            # Windows: Use taskkill command to terminate process tree
            # /F = Force terminate, /T = Terminate process tree (including children)
            logger.info(f"Terminating process tree (Windows): simulation={simulation_id}, pid={process.pid}")
            try:
                # First try graceful termination
                subprocess.run(
                    ['taskkill', '/PID', str(process.pid), '/T'],
                    capture_output=True,
                    timeout=5
                )
                try:
                    process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    # Force termination
                    logger.warning(f"Process did not respond, force terminating: {simulation_id}")
                    subprocess.run(
                        ['taskkill', '/F', '/PID', str(process.pid), '/T'],
                        capture_output=True,
                        timeout=5
                    )
                    process.wait(timeout=5)
            except Exception as e:
                logger.warning(f"taskkill failed, attempting terminate: {e}")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        else:
            # Unix: Terminate using process group
            # Because start_new_session=True was used, process group ID equals main process PID
            pgid = os.getpgid(process.pid)
            logger.info(f"Terminating process group (Unix): simulation={simulation_id}, pgid={pgid}")
            
            # First send SIGTERM to the entire process group
            os.killpg(pgid, signal.SIGTERM)
            
            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                # If not exited after timeout, force send SIGKILL
                logger.warning(f"Process group did not respond to SIGTERM, force killing: {simulation_id}")
                os.killpg(pgid, signal.SIGKILL)
                process.wait(timeout=5)
    
    @classmethod
    def stop_simulation(cls, simulation_id: str) -> SimulationRunState:
        """Stop simulation"""
        with cls._finalization_lock(simulation_id):
            state = cls.get_run_state(simulation_id)
            if not state:
                raise ValueError(f"Simulation does not exist: {simulation_id}")
            if state.runner_status == RunnerStatus.STOPPED:
                return state

            pending_updater = ZepGraphMemoryManager.get_updater(simulation_id)
            retrying_finalization = (
                pending_updater is not None
                and state.runner_status in {
                    RunnerStatus.STOPPING,
                    RunnerStatus.FAILED,
                }
            )
            if (
                state.runner_status not in [
                    RunnerStatus.STARTING,
                    RunnerStatus.RUNNING,
                    RunnerStatus.PAUSED,
                    RunnerStatus.STOPPING,
                ]
                and not retrying_finalization
            ):
                raise ValueError(
                    f"Simulation is not running: {simulation_id}, status={state.runner_status}"
                )

            state.runner_status = RunnerStatus.STOPPING
            cls._manual_stop_requests.add(simulation_id)
            cls._save_run_state(state)
            cls._sync_simulation_status(simulation_id, RunnerStatus.STOPPING)

            # Terminate process
            process = cls._processes.get(simulation_id)
            if process and process.poll() is None:
                try:
                    cls._terminate_process(process, simulation_id)
                except ProcessLookupError:
                    pass
                except Exception as e:
                    logger.error(f"Failed to terminate process group: {simulation_id}, error={e}")
                    try:
                        process.terminate()
                        process.wait(timeout=5)
                    except Exception:
                        process.kill()

        # Let the monitor consume the final action-log tail and own the single
        # updater drain. It will publish STOPPED (rather than COMPLETED) because
        # the manual-stop marker is set above.
        monitor = cls._monitor_threads.get(simulation_id)
        if (
            not retrying_finalization
            and
            monitor is not None
            and monitor is not threading.current_thread()
            and monitor.is_alive()
        ):
            wait_timeout = max(
                30.0,
                ZEP_INGESTION_WAIT_TIMEOUT_SECONDS
                + ZEP_HTTP_REQUEST_TIMEOUT_SECONDS
                + 5,
            )
            monitor.join(timeout=wait_timeout)
            if monitor.is_alive():
                # The monitor still owns finalization and may be inside one
                # bounded HTTP request. Do not block on or overwrite its lock;
                # leave the observable state as STOPPING and let polling expose
                # the eventual STOPPED/FAILED result.
                raise SimulationStopPending(
                    f"Simulation still stopping; graph memory ingestion not completed within {wait_timeout:.0f}s"
                )
        else:
            # Restart recovery or tests may have no monitor thread. Complete
            # the same barrier synchronously in this request.
            with cls._finalization_lock(simulation_id):
                state = cls.get_run_state(simulation_id) or state
                if cls._graph_memory_enabled.get(simulation_id, False):
                    try:
                        ZepGraphMemoryManager.stop_updater(simulation_id)
                        cls._graph_memory_enabled.pop(simulation_id, None)
                    except TimeoutError as timeout_err:
                        logger.warning(
                            f"Zep graph memory updater timed out during manual stop: {timeout_err}. "
                            f"All batches were submitted to Zep Cloud. Marking simulation as stopped."
                        )
                        ZepGraphMemoryManager.force_remove_updater(simulation_id)
                        cls._graph_memory_enabled.pop(simulation_id, None)
                    except Exception as error:
                        state.runner_status = RunnerStatus.FAILED
                        state.twitter_running = False
                        state.reddit_running = False
                        state.completed_at = datetime.now().isoformat()
                        state.error = f"Zep graph memory ingestion did not complete cleanly: {error}"
                        cls._save_run_state(state)
                        cls._sync_simulation_status(
                            simulation_id,
                            RunnerStatus.FAILED,
                            state.error,
                        )
                        raise RuntimeError(state.error) from error
                state.runner_status = RunnerStatus.STOPPED
                state.twitter_running = False
                state.reddit_running = False
                state.completed_at = datetime.now().isoformat()
                state.error = None
                cls._save_run_state(state)
                cls._sync_simulation_status(
                    simulation_id,
                    RunnerStatus.STOPPED,
                )
                cls._manual_stop_requests.discard(simulation_id)

        state = cls.get_run_state(simulation_id) or state
        if state.runner_status == RunnerStatus.FAILED:
            raise RuntimeError(state.error or "Failed to stop simulation")
        if state.runner_status != RunnerStatus.STOPPED:
            raise RuntimeError(
                f"Simulation stop did not reach terminal state: {simulation_id}, status={state.runner_status}"
            )

        logger.info(f"Simulation stopped: {simulation_id}")
        return state

    @classmethod
    def _read_actions_from_file(
        cls,
        file_path: str,
        default_platform: Optional[str] = None,
        platform_filter: Optional[str] = None,
        agent_id: Optional[int] = None,
        round_num: Optional[int] = None
    ) -> List[AgentAction]:
        """
        Read actions from a single action file.
        
        Args:
            file_path: Action log file path
            default_platform: Default platform (used when action record lacks platform field)
            platform_filter: Platform filter
            agent_id: Agent ID filter
            round_num: Round number filter
        """
        if not os.path.exists(file_path):
            return []
        
        actions = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    
                    # Skip non-action records (such as simulation_start, round_start, round_end events)
                    if "event_type" in data:
                        continue
                    
                    # Skip records without agent_id (non-agent actions)
                    if "agent_id" not in data:
                        continue
                    
                    # Get platform: prefer platform in record, otherwise use default platform
                    record_platform = data.get("platform") or default_platform or ""
                    
                    # Filter
                    if platform_filter and record_platform != platform_filter:
                        continue
                    if agent_id is not None and data.get("agent_id") != agent_id:
                        continue
                    if round_num is not None and data.get("round") != round_num:
                        continue
                    
                    actions.append(AgentAction(
                        round_num=data.get("round", 0),
                        timestamp=data.get("timestamp", ""),
                        platform=record_platform,
                        agent_id=data.get("agent_id", 0),
                        agent_name=data.get("agent_name", ""),
                        action_type=data.get("action_type", ""),
                        action_args=data.get("action_args", {}),
                        result=data.get("result"),
                        success=data.get("success", True),
                    ))
                    
                except json.JSONDecodeError:
                    continue
        
        return actions
    
    @classmethod
    def get_all_actions(
        cls,
        simulation_id: str,
        platform: Optional[str] = None,
        agent_id: Optional[int] = None,
        round_num: Optional[int] = None
    ) -> List[AgentAction]:
        """
        Get complete action history for all platforms (no pagination limit)
        
        Args:
            simulation_id: Simulation ID
            platform: Platform filter (twitter/reddit)
            agent_id: Agent filter
            round_num: Round number filter
            
        Returns:
            Complete action list (sorted by timestamp, newest first)
        """
        sim_dir = os.path.join(cls.RUN_STATE_DIR, simulation_id)
        actions = []
        
        # Read Twitter action file (automatically set platform to twitter based on file path)
        twitter_actions_log = os.path.join(sim_dir, "twitter", "actions.jsonl")
        if not platform or platform == "twitter":
            actions.extend(cls._read_actions_from_file(
                twitter_actions_log,
                default_platform="twitter",  # Automatically fill platform field
                platform_filter=platform,
                agent_id=agent_id, 
                round_num=round_num
            ))
        
        # Read Reddit action file (automatically set platform to reddit based on file path)
        reddit_actions_log = os.path.join(sim_dir, "reddit", "actions.jsonl")
        if not platform or platform == "reddit":
            actions.extend(cls._read_actions_from_file(
                reddit_actions_log,
                default_platform="reddit",  # Automatically fill platform field
                platform_filter=platform,
                agent_id=agent_id,
                round_num=round_num
            ))
        
        # If per-platform files do not exist, try reading legacy single file format
        if not actions:
            actions_log = os.path.join(sim_dir, "actions.jsonl")
            actions = cls._read_actions_from_file(
                actions_log,
                default_platform=None,  # Legacy format file should contain platform field
                platform_filter=platform,
                agent_id=agent_id,
                round_num=round_num
            )
        
        # Sort by timestamp (newest first)
        actions.sort(key=lambda x: x.timestamp, reverse=True)
        
        return actions
    
    @classmethod
    def get_actions(
        cls,
        simulation_id: str,
        limit: int = 100,
        offset: int = 0,
        platform: Optional[str] = None,
        agent_id: Optional[int] = None,
        round_num: Optional[int] = None
    ) -> List[AgentAction]:
        """
        Get action history (with pagination)
        
        Args:
            simulation_id: Simulation ID
            limit: Maximum items to return
            offset: Offset
            platform: Platform filter
            agent_id: Agent filter
            round_num: Round number filter
            
        Returns:
            Action list
        """
        actions = cls.get_all_actions(
            simulation_id=simulation_id,
            platform=platform,
            agent_id=agent_id,
            round_num=round_num
        )
        
        # Pagination
        return actions[offset:offset + limit]
    
    @classmethod
    def get_timeline(
        cls,
        simulation_id: str,
        start_round: int = 0,
        end_round: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get simulation timeline (aggregated by round)
        
        Args:
            simulation_id: Simulation ID
            start_round: Starting round
            end_round: Ending round
            
        Returns:
            Summary information for each round
        """
        actions = cls.get_actions(simulation_id, limit=10000)
        
        # Group by round
        rounds: Dict[int, Dict[str, Any]] = {}
        
        for action in actions:
            round_num = action.round_num
            
            if round_num < start_round:
                continue
            if end_round is not None and round_num > end_round:
                continue
            
            if round_num not in rounds:
                rounds[round_num] = {
                    "round_num": round_num,
                    "twitter_actions": 0,
                    "reddit_actions": 0,
                    "active_agents": set(),
                    "action_types": {},
                    "first_action_time": action.timestamp,
                    "last_action_time": action.timestamp,
                }
            
            r = rounds[round_num]
            
            if action.platform == "twitter":
                r["twitter_actions"] += 1
            else:
                r["reddit_actions"] += 1
            
            r["active_agents"].add(action.agent_id)
            r["action_types"][action.action_type] = r["action_types"].get(action.action_type, 0) + 1
            r["last_action_time"] = action.timestamp
        
        # Convert to list
        result = []
        for round_num in sorted(rounds.keys()):
            r = rounds[round_num]
            result.append({
                "round_num": round_num,
                "twitter_actions": r["twitter_actions"],
                "reddit_actions": r["reddit_actions"],
                "total_actions": r["twitter_actions"] + r["reddit_actions"],
                "active_agents_count": len(r["active_agents"]),
                "active_agents": list(r["active_agents"]),
                "action_types": r["action_types"],
                "first_action_time": r["first_action_time"],
                "last_action_time": r["last_action_time"],
            })
        
        return result
    
    @classmethod
    def get_agent_stats(cls, simulation_id: str) -> List[Dict[str, Any]]:
        """
        Get statistics for each agent.
        
        Returns:
            Agent statistics list
        """
        actions = cls.get_actions(simulation_id, limit=10000)
        
        agent_stats: Dict[int, Dict[str, Any]] = {}
        
        for action in actions:
            agent_id = action.agent_id
            
            if agent_id not in agent_stats:
                agent_stats[agent_id] = {
                    "agent_id": agent_id,
                    "agent_name": action.agent_name,
                    "total_actions": 0,
                    "twitter_actions": 0,
                    "reddit_actions": 0,
                    "action_types": {},
                    "first_action_time": action.timestamp,
                    "last_action_time": action.timestamp,
                }
            
            stats = agent_stats[agent_id]
            stats["total_actions"] += 1
            
            if action.platform == "twitter":
                stats["twitter_actions"] += 1
            else:
                stats["reddit_actions"] += 1
            
            stats["action_types"][action.action_type] = stats["action_types"].get(action.action_type, 0) + 1
            stats["last_action_time"] = action.timestamp
        
        # Sort by total actions
        result = sorted(agent_stats.values(), key=lambda x: x["total_actions"], reverse=True)
        
        return result
    
    @classmethod
    def cleanup_simulation_logs(cls, simulation_id: str) -> Dict[str, Any]:
        """
        Clean simulation run logs (used to force-restart simulation)
        
        Deletes the following files:
        - run_state.json
        - twitter/actions.jsonl
        - reddit/actions.jsonl
        - simulation.log
        - stdout.log / stderr.log
        - twitter_simulation.db (simulation database)
        - reddit_simulation.db (simulation database)
        - env_status.json (environment status)
        
        Note: Configuration files (simulation_config.json) and profile files are not deleted.
        
        Args:
            simulation_id: Simulation ID
            
        Returns:
            Cleanup result information
        """
        import shutil
        
        sim_dir = os.path.join(cls.RUN_STATE_DIR, simulation_id)
        
        if not os.path.exists(sim_dir):
            return {"success": True, "message": "Simulation directory does not exist, no cleanup needed"}
        
        cleaned_files = []
        errors = []
        
        # Files to delete (including database files)
        files_to_delete = [
            "run_state.json",
            "simulation.log",
            "stdout.log",
            "stderr.log",
            "twitter_simulation.db",  # Twitter platform database
            "reddit_simulation.db",   # Reddit platform database
            "env_status.json",        # Environment status file
        ]
        
        # Directories to delete (containing action logs)
        dirs_to_clean = ["twitter", "reddit"]
        
        # Delete files
        for filename in files_to_delete:
            file_path = os.path.join(sim_dir, filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    cleaned_files.append(filename)
                except Exception as e:
                    errors.append(f"Failed to delete {filename}: {str(e)}")
        
        # Clean action logs in platform directories
        for dir_name in dirs_to_clean:
            dir_path = os.path.join(sim_dir, dir_name)
            if os.path.exists(dir_path):
                actions_file = os.path.join(dir_path, "actions.jsonl")
                if os.path.exists(actions_file):
                    try:
                        os.remove(actions_file)
                        cleaned_files.append(f"{dir_name}/actions.jsonl")
                    except Exception as e:
                        errors.append(f"Failed to delete {dir_name}/actions.jsonl: {str(e)}")
        
        # Clean in-memory runtime state
        if simulation_id in cls._run_states:
            del cls._run_states[simulation_id]
        
        logger.info(f"Simulation log cleanup completed: {simulation_id}, deleted files: {cleaned_files}")
        
        return {
            "success": len(errors) == 0,
            "cleaned_files": cleaned_files,
            "errors": errors if errors else None
        }
    
    # Flag to prevent repeated cleanup
    _cleanup_done = False
    
    @classmethod
    def cleanup_all_simulations(cls):
        """
        Clean up all running simulation processes.
        
        Called during server shutdown to ensure all child processes are terminated.
        """
        # Prevent repeated cleanup
        if cls._cleanup_done:
            return
        cls._cleanup_done = True

        updater_ids = set(ZepGraphMemoryManager.get_simulation_ids())
        simulation_ids = sorted(
            set(cls._processes)
            | set(cls._graph_memory_enabled)
            | updater_ids
        )
        if not simulation_ids:
            return

        logger.info("Safely terminating all simulation processes and draining graph memory ingestion...")
        cleanup_failed = False

        # Each simulation follows the normal stop/finalization path: terminate
        # its producer, let the monitor consume the final action-log tail, and
        # only then drain Zep. This avoids dropping actions emitted during
        # SIGTERM handling.
        for simulation_id in simulation_ids:
            try:
                state = cls.get_run_state(simulation_id)
                updater = ZepGraphMemoryManager.get_updater(simulation_id)
                process = cls._processes.get(simulation_id)

                if state is None:
                    # Missing/corrupt state is exceptional, but retain the
                    # critical producer-before-consumer shutdown ordering.
                    if process is not None and process.poll() is None:
                        cls._terminate_process(process, simulation_id, timeout=5)
                    if updater is not None:
                        ZepGraphMemoryManager.stop_updater(simulation_id)
                    continue

                if updater is not None:
                    cls._graph_memory_enabled[simulation_id] = True
                    if state.runner_status in {
                        RunnerStatus.IDLE,
                        RunnerStatus.STOPPED,
                        RunnerStatus.COMPLETED,
                    }:
                        # A retained updater means the old terminal projection
                        # was premature. Restore the ingestion barrier first.
                        state.runner_status = RunnerStatus.STOPPING
                        cls._save_run_state(state)
                        cls._sync_simulation_status(
                            simulation_id,
                            RunnerStatus.STOPPING,
                        )

                needs_finalization = bool(
                    (process is not None and process.poll() is None)
                    or updater is not None
                    or state.runner_status in {
                        RunnerStatus.STARTING,
                        RunnerStatus.RUNNING,
                        RunnerStatus.PAUSED,
                        RunnerStatus.STOPPING,
                    }
                )
                if needs_finalization:
                    cls.stop_simulation(simulation_id)

                # A recovery path without a monitor does not run the monitor's
                # resource cleanup block. Release only successfully stopped
                # resources; FAILED/STOPPING resources remain retryable.
                latest = cls.get_run_state(simulation_id)
                if latest and latest.runner_status == RunnerStatus.STOPPED:
                    stopped_process = cls._processes.get(simulation_id)
                    if stopped_process is None or stopped_process.poll() is not None:
                        cls._processes.pop(simulation_id, None)
                        cls._action_queues.pop(simulation_id, None)
                        cls._monitor_threads.pop(simulation_id, None)
                        for file_map in (cls._stdout_files, cls._stderr_files):
                            file_handle = file_map.pop(simulation_id, None)
                            if file_handle:
                                try:
                                    file_handle.close()
                                except Exception:
                                    pass
            except Exception as error:
                cleanup_failed = True
                logger.error(
                    "Simulation cleanup failed, retaining state for retry: simulation_id=%s, error=%s",
                    simulation_id,
                    error,
                )

        if cleanup_failed:
            # Retained updaters and FAILED run states continue to block report
            # generation and graph deletion. Permit an explicit retry.
            cls._cleanup_done = False
            logger.error("Some simulations failed to finish cleanup safely")
        else:
            logger.info("Simulation process and graph write cleanup completed")
    
    @classmethod
    def register_cleanup(cls):
        """
        Register cleanup handlers
        
        Called at Flask app startup to ensure all simulation processes are cleaned up on server shutdown
        """
        global _cleanup_registered
        
        if _cleanup_registered:
            return
        
        # Under Flask debug mode, only register cleanup in the reloader child process (the one actually running the app)
        # WERKZEUG_RUN_MAIN=true indicates the reloader child process
        # If not debug mode, this env var won't exist, and cleanup still needs to be registered
        is_reloader_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
        is_debug_mode = os.environ.get('FLASK_DEBUG') == '1' or os.environ.get('WERKZEUG_RUN_MAIN') is not None
        
        # Register cleanup handler
        if is_debug_mode and not is_reloader_process:
            _cleanup_registered = True  # Flag registered
            return
        
        # Save original signal handlers
        original_sigint = signal.getsignal(signal.SIGINT)
        original_sigterm = signal.getsignal(signal.SIGTERM)
        # SIGHUP only exists on Unix (macOS/Linux), not Windows
        original_sighup = None
        has_sighup = hasattr(signal, 'SIGHUP')
        if has_sighup:
            original_sighup = signal.getsignal(signal.SIGHUP)
        
        def cleanup_handler(signum=None, frame=None):
            """Signal handler: clean up simulation processes before calling original handler"""
            # Only log if processes exist to clean up
            if cls._processes or cls._graph_memory_enabled:
                logger.info(f"Received signal {signum}, initiating cleanup...")
            cls.cleanup_all_simulations()
            
            # Call original signal handler for graceful Flask exit
            if signum == signal.SIGINT and callable(original_sigint):
                original_sigint(signum, frame)
            elif signum == signal.SIGTERM and callable(original_sigterm):
                original_sigterm(signum, frame)
            elif has_sighup and signum == signal.SIGHUP:
                # SIGHUP: Sent when terminal closes
                if callable(original_sighup):
                    original_sighup(signum, frame)
                else:
                    # Default behavior: exit cleanly
                    sys.exit(0)
            else:
                # If original handler is not callable, use default exit
                raise KeyboardInterrupt
        
        # Register atexit handler (as fallback)
        atexit.register(cls.cleanup_all_simulations)
        
        # Register signal handler (main thread only)
        try:
            # SIGTERM: Default termination signal
            signal.signal(signal.SIGTERM, cleanup_handler)
            # SIGINT: Ctrl+C
            signal.signal(signal.SIGINT, cleanup_handler)
            # SIGHUP: Terminal closed (Unix only)
            if has_sighup:
                signal.signal(signal.SIGHUP, cleanup_handler)
        except ValueError:
            # Not in main thread, using atexit
            logger.warning("Cannot register signal handlers (not main thread), using atexit only")
        
        _cleanup_registered = True
    
    @classmethod
    def get_running_simulations(cls) -> List[str]:
        """
        Get list of all currently running simulation IDs
        """
        running = []
        for sim_id, process in cls._processes.items():
            if process.poll() is None:
                running.append(sim_id)
        return running
    
    # ============== Interview Features ==============
    
    @classmethod
    def check_env_alive(cls, simulation_id: str) -> bool:
        """
        Check if simulation environment is active (can accept Interview commands)

        Args:
            simulation_id: Simulation ID

        Returns:
            True if environment is active, False if closed
        """
        sim_dir = os.path.join(cls.RUN_STATE_DIR, simulation_id)
        if not os.path.exists(sim_dir):
            return False

        ipc_client = SimulationIPCClient(sim_dir)
        return ipc_client.check_env_alive()

    @classmethod
    def get_env_status_detail(cls, simulation_id: str) -> Dict[str, Any]:
        """
        Get detailed status info of simulation environment

        Args:
            simulation_id: Simulation ID

        Returns:
            Status details dictionary with status, twitter_available, reddit_available, timestamp
        """
        sim_dir = os.path.join(cls.RUN_STATE_DIR, simulation_id)
        status_file = os.path.join(sim_dir, "env_status.json")
        
        default_status = {
            "status": "stopped",
            "twitter_available": False,
            "reddit_available": False,
            "timestamp": None
        }
        
        if not os.path.exists(status_file):
            return default_status
        
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)
            return {
                "status": status.get("status", "stopped"),
                "twitter_available": status.get("twitter_available", False),
                "reddit_available": status.get("reddit_available", False),
                "timestamp": status.get("timestamp")
            }
        except (json.JSONDecodeError, OSError):
            return default_status

    @classmethod
    def interview_agent(
        cls,
        simulation_id: str,
        agent_id: int,
        prompt: str,
        platform: str = None,
        timeout: float = 60.0
    ) -> Dict[str, Any]:
        """
        Interview single Agent

        Args:
            simulation_id: Simulation ID
            agent_id: Agent ID
            prompt: Interview question
            platform: Target platform (optional)
                - "twitter": Interview Twitter platform only
                - "reddit": Interview Reddit platform only
                - None: Interview both platforms in dual-platform simulations and return combined results
            timeout: Timeout in seconds

        Returns:
            Interview results dictionary

        Raises:
            ValueError: Simulation does not exist or environment not running
            TimeoutError: Waiting for response timed out
        """
        sim_dir = os.path.join(cls.RUN_STATE_DIR, simulation_id)
        if not os.path.exists(sim_dir):
            raise ValueError(f"Simulation does not exist: {simulation_id}")

        ipc_client = SimulationIPCClient(sim_dir)

        if not ipc_client.check_env_alive():
            logger.info(f"Live simulation IPC environment not active; using direct agent interview: simulation_id={simulation_id}, agent_id={agent_id}")
            return cls._interview_agent_direct(
                simulation_id=simulation_id,
                agent_id=agent_id,
                prompt=prompt,
                platform=platform
            )

        logger.info(f"Sent Interview command: simulation_id={simulation_id}, agent_id={agent_id}, platform={platform}")

        response = ipc_client.send_interview(
            agent_id=agent_id,
            prompt=prompt,
            platform=platform,
            timeout=timeout
        )

        if response.status.value == "completed":
            return {
                "success": True,
                "agent_id": agent_id,
                "prompt": prompt,
                "result": response.result,
                "timestamp": response.timestamp
            }
        else:
            return {
                "success": False,
                "agent_id": agent_id,
                "prompt": prompt,
                "error": response.error,
                "timestamp": response.timestamp
            }
    
    @classmethod
    def interview_agents_batch(
        cls,
        simulation_id: str,
        interviews: List[Dict[str, Any]],
        platform: str = None,
        timeout: float = 120.0
    ) -> Dict[str, Any]:
        """
        Batch interview multiple Agents

        Args:
            simulation_id: Simulation ID
            interviews: Interview list, each item containing {"agent_id": int, "prompt": str, "platform": str(optional)}
            platform: Default platform (optional, overridden by platform on each interview item)
                - "twitter": Default to interviewing Twitter platform only
                - "reddit": Default to interviewing Reddit platform only
                - None: Interview both platforms for each agent in dual-platform simulations
            timeout: Timeout in seconds

        Returns:
            Batch interview results dictionary

        Raises:
            ValueError: Simulation does not exist or environment not running
            TimeoutError: Waiting for response timed out
        """
        sim_dir = os.path.join(cls.RUN_STATE_DIR, simulation_id)
        if not os.path.exists(sim_dir):
            raise ValueError(f"Simulation does not exist: {simulation_id}")

        ipc_client = SimulationIPCClient(sim_dir)

        if not ipc_client.check_env_alive():
            logger.info(f"Live simulation IPC environment not active; using direct batch interview: simulation_id={simulation_id}, count={len(interviews)}")
            return cls._interview_agents_batch_direct(
                simulation_id=simulation_id,
                interviews=interviews,
                platform=platform
            )

        logger.info(f"Sent batch Interview command: simulation_id={simulation_id}, count={len(interviews)}, platform={platform}")

        response = ipc_client.send_batch_interview(
            interviews=interviews,
            platform=platform,
            timeout=timeout
        )

        if response.status.value == "completed":
            return {
                "success": True,
                "interviews_count": len(interviews),
                "result": response.result,
                "timestamp": response.timestamp
            }
        else:
            return {
                "success": False,
                "interviews_count": len(interviews),
                "error": response.error,
                "timestamp": response.timestamp
            }
    
    @classmethod
    def interview_all_agents(
        cls,
        simulation_id: str,
        prompt: str,
        platform: str = None,
        timeout: float = 180.0
    ) -> Dict[str, Any]:
        """
        Interview all agents (global interview)

        Uses the same question to interview all agents in the simulation

        Args:
            simulation_id: Simulation ID
            prompt: Interview question (same for all Agents)
            platform: Target platform (optional)
                - "twitter": Interview Twitter platform only
                - "reddit": Interview Reddit platform only
                - None: Interview both platforms for each agent in dual-platform simulations
            timeout: Timeout in seconds

        Returns:
            Global interview results dictionary
        """
        sim_dir = os.path.join(cls.RUN_STATE_DIR, simulation_id)
        if not os.path.exists(sim_dir):
            raise ValueError(f"Simulation does not exist: {simulation_id}")

        # Get all Agent information from configuration file
        config_path = os.path.join(sim_dir, "simulation_config.json")
        if not os.path.exists(config_path):
            raise ValueError(f"Simulation configuration does not exist: {simulation_id}")

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        agent_configs = config.get("agent_configs", [])
        if not agent_configs:
            raise ValueError(f"No Agents found in simulation configuration: {simulation_id}")

        # Build batch interview list
        interviews = []
        for agent_config in agent_configs:
            agent_id = agent_config.get("agent_id")
            if agent_id is not None:
                interviews.append({
                    "agent_id": agent_id,
                    "prompt": prompt
                })

        logger.info(f"Sent global Interview command: simulation_id={simulation_id}, agent_count={len(interviews)}, platform={platform}")

        return cls.interview_agents_batch(
            simulation_id=simulation_id,
            interviews=interviews,
            platform=platform,
            timeout=timeout
        )
    
    @classmethod
    def close_simulation_env(
        cls,
        simulation_id: str,
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        Close simulation environment (gracefully exits waiting command loop)
        
        Args:
            simulation_id: Simulation ID
            timeout: Timeout in seconds
            
        Returns:
            Operation result dictionary
        """
        sim_dir = os.path.join(cls.RUN_STATE_DIR, simulation_id)
        if not os.path.exists(sim_dir):
            raise ValueError(f"Simulation does not exist: {simulation_id}")
        
        ipc_client = SimulationIPCClient(sim_dir)
        
        if not ipc_client.check_env_alive():
            return {
                "success": True,
                "message": "Environment is already closed"
            }
        
        logger.info(f"Sent close environment command: simulation_id={simulation_id}")
        
        try:
            response = ipc_client.send_close_env(timeout=timeout)
            
            return {
                "success": response.status.value == "completed",
                "message": "Environment close command sent",
                "result": response.result,
                "timestamp": response.timestamp
            }
        except TimeoutError:
            # Timeout may indicate environment is currently shutting down
            return {
                "success": True,
                "message": "Environment close command sent (response timed out, environment may be closing)"
            }
    
    @classmethod
    def _get_interview_history_from_db(
        cls,
        db_path: str,
        platform_name: str,
        agent_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get Interview history from single database"""
        import sqlite3
        
        if not os.path.exists(db_path):
            return []
        
        results = []
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            if agent_id is not None:
                cursor.execute("""
                    SELECT user_id, info, created_at
                    FROM trace
                    WHERE action = 'interview' AND user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (agent_id, limit))
            else:
                cursor.execute("""
                    SELECT user_id, info, created_at
                    FROM trace
                    WHERE action = 'interview'
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))
            
            for user_id, info_json, created_at in cursor.fetchall():
                try:
                    info = json.loads(info_json) if info_json else {}
                except json.JSONDecodeError:
                    info = {"raw": info_json}
                
                results.append({
                    "agent_id": user_id,
                    "response": info.get("response", info),
                    "prompt": info.get("prompt", ""),
                    "timestamp": created_at,
                    "platform": platform_name
                })
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to read Interview history ({platform_name}): {e}")
        
        return results

    @classmethod
    def get_interview_history(
        cls,
        simulation_id: str,
        platform: str = None,
        agent_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get Interview history records (read from database)
        
        Args:
            simulation_id: Simulation ID
            platform: Platform type (reddit/twitter/None)
                - "reddit": Retrieve Reddit platform history only
                - "twitter": Retrieve Twitter platform history only
                - None: Retrieve history from both platforms
            agent_id: Specific Agent ID (optional, filter history by this agent)
            limit: Per-platform return limit
            
        Returns:
            List of Interview history records
        """
        sim_dir = os.path.join(cls.RUN_STATE_DIR, simulation_id)
        
        results = []
        
        # Determine platforms to query
        if platform in ("reddit", "twitter"):
            platforms = [platform]
        else:
            # Query both platforms when platform is unspecified
            platforms = ["twitter", "reddit"]
        
        for p in platforms:
            db_path = os.path.join(sim_dir, f"{p}_simulation.db")
            platform_results = cls._get_interview_history_from_db(
                db_path=db_path,
                platform_name=p,
                agent_id=agent_id,
                limit=limit
            )
            results.extend(platform_results)
        
        # Sort in descending chronological order
        results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # If multiple platforms queried, enforce total limit
        if len(platforms) > 1 and len(results) > limit:
            results = results[:limit]
        
        return results

    # ============== Direct Agent Interview Methods (Offline Fallback) ==============

    @classmethod
    def _get_agent_profile(cls, sim_dir: str, agent_id: int, platform: str) -> Optional[Dict[str, Any]]:
        """Load profile for a given agent_id and platform"""
        # If twitter platform requested, inspect twitter_profiles.csv first
        if platform == "twitter":
            csv_path = os.path.join(sim_dir, "twitter_profiles.csv")
            if os.path.exists(csv_path):
                import csv
                try:
                    with open(csv_path, 'r', encoding='utf-8', newline='') as f:
                        reader = list(csv.DictReader(f))
                        for idx, row in enumerate(reader):
                            uid = row.get("user_id") or row.get("id")
                            if uid is not None and str(uid) == str(agent_id):
                                return row
                            if idx == agent_id:
                                return row
                except Exception as e:
                    logger.warning(f"Error reading twitter_profiles.csv: {e}")

        # Check reddit / json profiles
        json_path = os.path.join(sim_dir, "reddit_profiles.json")
        if not os.path.exists(json_path):
            json_path = os.path.join(sim_dir, "profiles.json")

        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    profiles = json.load(f)
                    if isinstance(profiles, list):
                        for idx, p in enumerate(profiles):
                            uid = p.get("user_id") if p.get("user_id") is not None else p.get("id")
                            if uid is not None and str(uid) == str(agent_id):
                                return p
                            if idx == agent_id:
                                return p
            except Exception as e:
                logger.warning(f"Error reading reddit_profiles.json: {e}")

        # If still not found and platform was reddit, try twitter CSV as fallback
        if platform != "twitter":
            csv_path = os.path.join(sim_dir, "twitter_profiles.csv")
            if os.path.exists(csv_path):
                import csv
                try:
                    with open(csv_path, 'r', encoding='utf-8', newline='') as f:
                        reader = list(csv.DictReader(f))
                        for idx, row in enumerate(reader):
                            uid = row.get("user_id") or row.get("id")
                            if uid is not None and str(uid) == str(agent_id):
                                return row
                            if idx == agent_id:
                                return row
                except Exception as e:
                    logger.warning(f"Error reading fallback twitter_profiles.csv: {e}")

        return None

    @classmethod
    def _get_agent_recent_actions(cls, sim_dir: str, agent_id: int, platform: str) -> List[str]:
        """Retrieve recent posts and comments for the agent from simulation database"""
        actions = []
        db_path = os.path.join(sim_dir, f"{platform}_simulation.db")
        if not os.path.exists(db_path):
            alt_platform = "reddit" if platform == "twitter" else "twitter"
            alt_path = os.path.join(sim_dir, f"{alt_platform}_simulation.db")
            if os.path.exists(alt_path):
                db_path = alt_path

        if os.path.exists(db_path):
            import sqlite3
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT content FROM post WHERE user_id = ? ORDER BY created_at DESC LIMIT 3", (agent_id,))
                    for row in cursor.fetchall():
                        if row[0]:
                            actions.append(f"Post: {row[0]}")
                except Exception:
                    pass

                try:
                    cursor.execute("SELECT content FROM comment WHERE user_id = ? ORDER BY created_at DESC LIMIT 3", (agent_id,))
                    for row in cursor.fetchall():
                        if row[0]:
                            actions.append(f"Comment: {row[0]}")
                except Exception:
                    pass
                conn.close()
            except Exception as e:
                logger.warning(f"Failed to query agent actions from database: {e}")

        return actions

    @classmethod
    def _generate_agent_response(
        cls,
        profile: Optional[Dict[str, Any]],
        sim_requirement: str,
        past_actions: List[str],
        prompt: str
    ) -> str:
        """Generate an authentic response via LLM in the persona of the agent"""
        from ..utils.llm_client import LLMClient

        clean_prompt = prompt or ""
        prefix = "Drawing upon your persona, all past memories, and actions, reply directly in plain text without invoking any tools: "
        if clean_prompt.startswith(prefix):
            clean_prompt = clean_prompt[len(prefix):].strip()

        if not profile:
            name = "Agent"
            username = "agent"
            bio = "Active participant in this social simulation."
            persona = "An active participant in this social simulation."
            profession = "Community Member"
            topics = ""
        else:
            name = profile.get("name") or profile.get("username") or "Agent"
            username = profile.get("username") or "agent"
            bio = profile.get("bio") or profile.get("description") or ""
            persona = profile.get("persona") or profile.get("user_char") or bio or "A social simulation participant"
            profession = profile.get("profession") or profile.get("role") or "Participant"
            interested_topics = profile.get("interested_topics") or ""
            topics = ", ".join(interested_topics) if isinstance(interested_topics, list) else str(interested_topics)

        actions_context = ""
        if past_actions:
            actions_context = "\nYour past activities and statements in this simulation:\n" + "\n".join(f"- {act}" for act in past_actions[:4])

        system_prompt = (
            f"You are roleplaying as {name} (@{username}) on social media.\n"
            f"Your Role/Profession: {profession}\n"
            f"Your Bio: {bio}\n"
            f"Your Core Persona & Perspective: {persona}\n"
            f"{'Your Interests: ' + topics if topics else ''}\n"
            f"{'Simulation Background Topic: ' + sim_requirement if sim_requirement else ''}\n"
            f"{actions_context}\n\n"
            f"CRITICAL INSTRUCTIONS:\n"
            f"1. Stay completely in-character as {name} reflecting your specific background, tone, knowledge, and worldview.\n"
            f"2. Respond naturally to the user's message as an individual agent. Keep your tone realistic and personal.\n"
            f"3. Do NOT mention you are an AI, LLM, or in a simulation.\n"
            f"4. Reply directly in plain text without markdown headers, bullet lists (unless asked), or tools.\n"
            f"5. Match the language of the prompt (e.g. English)."
        )

        try:
            llm = LLMClient()
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": clean_prompt}
            ]
            response = llm.chat(messages, temperature=0.7, max_tokens=1024)
            return response.strip()
        except Exception as e:
            logger.error(f"Failed to generate LLM agent response: {e}")
            return f"Hello, I am {name}. As {profession}, I'm following the developments in this scenario closely."

    @classmethod
    def _record_interview_to_db(
        cls,
        sim_dir: str,
        agent_id: int,
        platform: str,
        prompt: str,
        response_text: str
    ):
        """Save interview record to database trace table"""
        import sqlite3
        db_path = os.path.join(sim_dir, f"{platform}_simulation.db")
        if not os.path.exists(db_path):
            alt_platform = "reddit" if platform == "twitter" else "twitter"
            alt_path = os.path.join(sim_dir, f"{alt_platform}_simulation.db")
            if os.path.exists(alt_path):
                db_path = alt_path

        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO trace (user_id, created_at, action, info) VALUES (?, ?, ?, ?)",
                    (
                        agent_id,
                        datetime.now().isoformat(),
                        "interview",
                        json.dumps({"prompt": prompt, "response": response_text}, ensure_ascii=False)
                    )
                )
                conn.commit()
                conn.close()
            except Exception as e:
                logger.warning(f"Failed to record interview to trace table: {e}")

    @classmethod
    def _interview_agent_direct(
        cls,
        simulation_id: str,
        agent_id: int,
        prompt: str,
        platform: str = None
    ) -> Dict[str, Any]:
        """
        Directly interview an agent using its profile, persona, and past simulation actions.
        Used when the simulation process is not actively running (e.g., in Step 5 Deep Interaction).
        """
        sim_dir = os.path.join(cls.RUN_STATE_DIR, simulation_id)
        if not os.path.exists(sim_dir):
            raise ValueError(f"Simulation does not exist: {simulation_id}")

        platforms_to_interview = []
        if platform:
            platforms_to_interview = [platform]
        else:
            has_reddit = os.path.exists(os.path.join(sim_dir, "reddit_profiles.json")) or os.path.exists(os.path.join(sim_dir, "reddit_simulation.db"))
            has_twitter = os.path.exists(os.path.join(sim_dir, "twitter_profiles.csv")) or os.path.exists(os.path.join(sim_dir, "twitter_simulation.db"))
            if has_reddit and has_twitter:
                platforms_to_interview = ["twitter", "reddit"]
            elif has_reddit:
                platforms_to_interview = ["reddit"]
            elif has_twitter:
                platforms_to_interview = ["twitter"]
            else:
                platforms_to_interview = ["reddit"]

        sim_requirement = ""
        config_file = os.path.join(sim_dir, "simulation_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    sim_requirement = cfg.get("simulation_requirement", "")
            except Exception:
                pass

        platform_results = {}
        for p in platforms_to_interview:
            profile = cls._get_agent_profile(sim_dir, agent_id, p)
            if not profile:
                other_p = "reddit" if p == "twitter" else "twitter"
                profile = cls._get_agent_profile(sim_dir, agent_id, other_p)

            past_actions = cls._get_agent_recent_actions(sim_dir, agent_id, p)
            response_text = cls._generate_agent_response(
                profile=profile,
                sim_requirement=sim_requirement,
                past_actions=past_actions,
                prompt=prompt
            )

            cls._record_interview_to_db(sim_dir, agent_id, p, prompt, response_text)

            platform_results[p] = {
                "agent_id": agent_id,
                "response": response_text,
                "platform": p,
                "timestamp": datetime.now().isoformat()
            }

        if platform:
            res = platform_results.get(platform, list(platform_results.values())[0])
            return {
                "success": True,
                "agent_id": agent_id,
                "prompt": prompt,
                "result": res,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": True,
                "agent_id": agent_id,
                "prompt": prompt,
                "result": {
                    "agent_id": agent_id,
                    "prompt": prompt,
                    "platforms": platform_results
                },
                "timestamp": datetime.now().isoformat()
            }

    @classmethod
    def _interview_agents_batch_direct(
        cls,
        simulation_id: str,
        interviews: List[Dict[str, Any]],
        platform: str = None
    ) -> Dict[str, Any]:
        """
        Directly batch interview agents using their profiles and past actions in parallel.
        """
        from concurrent.futures import ThreadPoolExecutor

        sim_dir = os.path.join(cls.RUN_STATE_DIR, simulation_id)
        if not os.path.exists(sim_dir):
            raise ValueError(f"Simulation does not exist: {simulation_id}")

        sim_requirement = ""
        config_file = os.path.join(sim_dir, "simulation_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    sim_requirement = cfg.get("simulation_requirement", "")
            except Exception:
                pass

        has_reddit = os.path.exists(os.path.join(sim_dir, "reddit_profiles.json")) or os.path.exists(os.path.join(sim_dir, "reddit_simulation.db"))
        has_twitter = os.path.exists(os.path.join(sim_dir, "twitter_profiles.csv")) or os.path.exists(os.path.join(sim_dir, "twitter_simulation.db"))

        def process_one_interview(item: Dict[str, Any]):
            agent_id = item.get("agent_id")
            prompt = item.get("prompt", "")
            item_platform = item.get("platform") or platform

            if item_platform:
                platforms = [item_platform]
            else:
                if has_reddit and has_twitter:
                    platforms = ["twitter", "reddit"]
                elif has_reddit:
                    platforms = ["reddit"]
                elif has_twitter:
                    platforms = ["twitter"]
                else:
                    platforms = ["reddit"]

            item_results = []
            for p in platforms:
                profile = cls._get_agent_profile(sim_dir, agent_id, p)
                if not profile:
                    other_p = "reddit" if p == "twitter" else "twitter"
                    profile = cls._get_agent_profile(sim_dir, agent_id, other_p)

                past_actions = cls._get_agent_recent_actions(sim_dir, agent_id, p)
                response_text = cls._generate_agent_response(
                    profile=profile,
                    sim_requirement=sim_requirement,
                    past_actions=past_actions,
                    prompt=prompt
                )
                cls._record_interview_to_db(sim_dir, agent_id, p, prompt, response_text)

                key = f"{p}_{agent_id}"
                item_results.append((key, {
                    "agent_id": agent_id,
                    "response": response_text,
                    "platform": p,
                    "timestamp": datetime.now().isoformat()
                }))
            return item_results

        results = {}
        max_workers = min(max(len(interviews), 1), 6)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_one_interview, item) for item in interviews]
            for future in futures:
                try:
                    for key, res_dict in future.result():
                        results[key] = res_dict
                except Exception as e:
                    logger.error(f"Error in batch interview execution: {e}")

        return {
            "success": True,
            "interviews_count": len(interviews),
            "result": {
                "interviews_count": len(results),
                "results": results
            },
            "timestamp": datetime.now().isoformat()
        }
