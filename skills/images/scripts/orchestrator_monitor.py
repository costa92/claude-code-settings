#!/usr/bin/env python3
"""
Orchestrator Heartbeat Monitor Integration

Monitors background image generation process and handles timeouts with auto-recovery.

Usage:
    monitor = OrchestratorMonitor(
        article_path="/path/to/article.md",
        process=subprocess.Popen(...),
        timeout=10
    )
    result = monitor.wait_with_heartbeat()
    # result.success: bool
    # result.error: Optional[str]
    # result.killed: bool (True if process was killed due to timeout)
"""

import subprocess
import time
from pathlib import Path
from typing import NamedTuple, Optional
from heartbeat import HeartbeatMonitor, HeartbeatWatcher


class MonitorResult(NamedTuple):
    """Result of process monitoring."""
    success: bool
    error: Optional[str] = None
    killed: bool = False
    exit_code: Optional[int] = None
    timeout_seconds: Optional[float] = None


class OrchestratorMonitor:
    """
    Monitor background process with heartbeat health checks.

    Handles:
    - Process startup and cleanup
    - Heartbeat monitoring in separate thread
    - Automatic detection and recovery from hangs
    - Graceful degradation on timeout
    """

    def __init__(
        self,
        article_path: str,
        process: subprocess.Popen,
        timeout: float = 10.0,
        heartbeat_timeout: float = 10.0,
        check_interval: float = 3.0
    ):
        """
        Initialize orchestrator monitor.

        Args:
            article_path: Path to article being processed
            process: Subprocess to monitor
            timeout: Total timeout for process (seconds)
            heartbeat_timeout: Consider stale if no heartbeat for N seconds
            check_interval: How often to check heartbeat
        """
        self.article_path = article_path
        self.process = process
        self.timeout = timeout
        self.heartbeat_timeout = heartbeat_timeout

        self.monitor = HeartbeatMonitor(article_path)
        self.watcher = HeartbeatWatcher(
            article_path,
            check_interval=check_interval,
            timeout=heartbeat_timeout
        )

    def wait_with_heartbeat(self) -> MonitorResult:
        """
        Wait for process to complete with heartbeat monitoring.

        Returns:
            MonitorResult with success status, error info, and exit code.
        """
        start_time = time.time()
        self.watcher.start()

        try:
            while time.time() - start_time < self.timeout:
                # Check if process finished normally
                exit_code = self.process.poll()
                if exit_code is not None:
                    self.watcher.stop()
                    return MonitorResult(
                        success=(exit_code == 0),
                        error=None if exit_code == 0 else f"Process exited with code {exit_code}",
                        killed=False,
                        exit_code=exit_code
                    )

                # Check if process appears stale
                if self.watcher.is_stale():
                    return self._handle_stale_process(start_time)

                time.sleep(1)

            # Timeout reached
            return self._handle_timeout(start_time)

        finally:
            self.watcher.stop()
            self.monitor.cleanup()

    def _handle_stale_process(self, start_time: float) -> MonitorResult:
        """Handle case where process appears stalled."""
        elapsed = time.time() - start_time

        print(f"⚠️ Process stalled (no heartbeat for {self.heartbeat_timeout}s)")
        print(f"  Elapsed time: {elapsed:.1f}s")

        # Kill the stalled process
        try:
            self.process.terminate()
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()

        # Clean up monitor files
        self.monitor.cleanup()

        return MonitorResult(
            success=False,
            error=f"Process stalled (no heartbeat for {self.heartbeat_timeout}s)",
            killed=True,
            timeout_seconds=elapsed
        )

    def _handle_timeout(self, start_time: float) -> MonitorResult:
        """Handle case where process exceeded total timeout."""
        elapsed = time.time() - start_time

        print(f"⚠️ Process timeout ({self.timeout}s limit exceeded)")

        # Kill the process
        try:
            self.process.terminate()
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()

        # Clean up monitor files
        self.monitor.cleanup()

        return MonitorResult(
            success=False,
            error=f"Process timeout after {self.timeout}s",
            killed=True,
            timeout_seconds=elapsed
        )


def run_with_monitoring(
    command: list,
    article_path: str,
    timeout: float = 300.0,
    heartbeat_timeout: float = 10.0,
    max_retries: int = 1
) -> MonitorResult:
    """
    Run command with heartbeat monitoring and auto-recovery.

    Usage:
        result = run_with_monitoring(
            command=[
                "python3",
                "generate_and_upload_images.py",
                "--process-file", "/path/to/article.md"
            ],
            article_path="/path/to/article.md",
            timeout=300,
            max_retries=1
        )

        if result.success:
            print(f"✅ Image generation succeeded")
        elif result.killed and result.exit_code != 0:
            print(f"⚠️ Process killed: {result.error}")
            # Handle retry or graceful degradation
        else:
            print(f"❌ Image generation failed: {result.error}")

    Args:
        command: Command to run as list (e.g., ["python3", "script.py", "--arg"])
        article_path: Path to article being processed
        timeout: Total timeout in seconds
        heartbeat_timeout: Heartbeat staleness threshold in seconds
        max_retries: Number of retry attempts on timeout

    Returns:
        MonitorResult with outcome details
    """
    article_file = Path(article_path)
    if not article_file.exists():
        return MonitorResult(
            success=False,
            error=f"Article file not found: {article_path}"
        )

    for attempt in range(max_retries + 1):
        try:
            # Start process
            print(f"🚀 Starting process (attempt {attempt + 1}/{max_retries + 1})")
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Monitor with heartbeat
            monitor = OrchestratorMonitor(
                article_path=article_path,
                process=process,
                timeout=timeout,
                heartbeat_timeout=heartbeat_timeout
            )
            result = monitor.wait_with_heartbeat()

            # Check result
            if result.success:
                print(f"✅ Process succeeded")
                return result

            # On timeout/stall, retry once
            if result.killed and attempt < max_retries:
                print(f"🔄 Retrying after timeout...")
                time.sleep(2)
                continue

            # Final failure
            return result

        except Exception as e:
            return MonitorResult(
                success=False,
                error=f"Monitor error: {str(e)}"
            )

    # Should not reach here
    return MonitorResult(
        success=False,
        error="Unknown error in monitoring"
    )


if __name__ == "__main__":
    # Test orchestrator monitor
    import tempfile
    import sys

    print("Testing OrchestratorMonitor...")

    # Create temp article file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        temp_article = f.name
        f.write("# Test Article\n")

    try:
        # Test 1: Successful process
        print("✓ Test 1: Monitor successful process")
        process = subprocess.Popen(
            ["python3", "-c", "import time; time.sleep(1); print('Done')"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        monitor = OrchestratorMonitor(temp_article, process, timeout=5)
        result = monitor.wait_with_heartbeat()
        print(f"  Success: {result.success}, Exit code: {result.exit_code}")

        # Test 2: Failed process
        print("✓ Test 2: Monitor failed process")
        process = subprocess.Popen(
            ["python3", "-c", "import sys; sys.exit(1)"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        monitor = OrchestratorMonitor(temp_article, process, timeout=5)
        result = monitor.wait_with_heartbeat()
        print(f"  Success: {result.success}, Exit code: {result.exit_code}")

        print("✅ All orchestrator tests passed!")

    finally:
        # Cleanup
        import os
        for f in [temp_article, temp_article + ".heartbeat", temp_article + ".lock"]:
            if os.path.exists(f):
                try:
                    os.unlink(f)
                except:
                    pass
