#!/usr/bin/env python3
"""
Heartbeat Monitoring for Background Image Generation Process

Provides process health monitoring through timestamp files and lock files.
Prevents incomplete articles from reaching review/publish stages.

Usage:
    monitor = HeartbeatMonitor(article_path="/path/to/article.md")

    # In background task
    monitor.start_heartbeat()
    try:
        # Do work
        process_images()
    finally:
        monitor.stop_heartbeat()

    # In orchestrator
    if not monitor.is_alive(timeout_seconds=10):
        monitor.cleanup()
        # Retry or fail gracefully
"""

import os
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional


class HeartbeatMonitor:
    """Monitor process health through heartbeat files."""

    def __init__(self, article_path: str, heartbeat_interval: float = 2.0):
        """
        Initialize heartbeat monitor.

        Args:
            article_path: Absolute path to article.md
            heartbeat_interval: Seconds between heartbeat writes (default: 2s)
        """
        self.article_path = Path(article_path)
        self.heartbeat_file = Path(str(article_path) + ".heartbeat")
        self.lock_file = Path(str(article_path) + ".lock")
        self.heartbeat_interval = heartbeat_interval
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start_heartbeat(self) -> None:
        """
        Start background heartbeat thread.

        Creates:
        - {article_path}.lock: Signal that process is running
        - {article_path}.heartbeat: Timestamp updated every 2 seconds

        Call this at the start of background processing.
        """
        # Create lock file
        self.lock_file.touch()

        # Start heartbeat thread
        self._stop_event.clear()
        self._heartbeat_thread = threading.Thread(
            target=self._write_heartbeat,
            daemon=True,
            name=f"Heartbeat-{self.article_path.name}"
        )
        self._heartbeat_thread.start()

    def stop_heartbeat(self) -> None:
        """
        Stop heartbeat and clean up files.

        Call this when background processing completes (success or failure).
        """
        # Signal thread to stop
        self._stop_event.set()

        # Wait for thread to finish
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=5)

        # Remove lock file to signal completion
        if self.lock_file.exists():
            self.lock_file.unlink()

    def _write_heartbeat(self) -> None:
        """Background thread: write heartbeat timestamp every 2 seconds."""
        while not self._stop_event.is_set():
            try:
                # Write current timestamp
                timestamp = datetime.now().isoformat()
                self.heartbeat_file.write_text(timestamp)
            except Exception as e:
                # Fail silently to avoid crashing background process
                print(f"⚠️ Failed to write heartbeat: {e}", flush=True)

            # Wait before next write
            self._stop_event.wait(self.heartbeat_interval)

    def is_alive(self, timeout_seconds: float = 10.0) -> bool:
        """
        Check if monitored process is alive.

        Returns False if:
        - Heartbeat file doesn't exist (process never started)
        - Heartbeat file is stale (not updated for timeout_seconds)

        Args:
            timeout_seconds: Maximum age of heartbeat file (default: 10s)

        Returns:
            True if process appears healthy, False if stale or missing.
        """
        if not self.heartbeat_file.exists():
            return False

        try:
            # Read timestamp from heartbeat file
            timestamp_str = self.heartbeat_file.read_text().strip()
            last_heartbeat = datetime.fromisoformat(timestamp_str)

            # Check if heartbeat is recent
            age = (datetime.now() - last_heartbeat).total_seconds()
            return age < timeout_seconds
        except Exception:
            # If we can't read/parse, consider process unhealthy
            return False

    def cleanup(self) -> None:
        """Remove heartbeat and lock files."""
        for f in [self.heartbeat_file, self.lock_file]:
            if f.exists():
                try:
                    f.unlink()
                except Exception as e:
                    print(f"⚠️ Failed to clean {f}: {e}", flush=True)


class HeartbeatWatcher:
    """
    Monitor heartbeat in separate thread (for orchestrator use).

    Usage:
        watcher = HeartbeatWatcher(article_path, timeout=10)
        watcher.start()
        # ... do other work ...
        if watcher.is_stale():
            print("Process is stale, killing and retrying")
            # Kill process
            # Retry
        else:
            print("Process is healthy")
        watcher.stop()
    """

    def __init__(self, article_path: str, check_interval: float = 3.0, timeout: float = 10.0):
        """
        Initialize heartbeat watcher.

        Args:
            article_path: Path to article being monitored
            check_interval: How often to check heartbeat (default: 3s)
            timeout: Consider dead if no heartbeat for N seconds (default: 10s)
        """
        self.monitor = HeartbeatMonitor(article_path)
        self.check_interval = check_interval
        self.timeout = timeout
        self._watcher_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._is_stale = False

    def start(self) -> None:
        """Start watching heartbeat in background."""
        self._stop_event.clear()
        self._watcher_thread = threading.Thread(
            target=self._watch_loop,
            daemon=True,
            name=f"Watcher-{self.monitor.article_path.name}"
        )
        self._watcher_thread.start()

    def stop(self) -> None:
        """Stop watching."""
        self._stop_event.set()
        if self._watcher_thread:
            self._watcher_thread.join(timeout=5)

    def _watch_loop(self) -> None:
        """Background thread: check heartbeat periodically."""
        while not self._stop_event.is_set():
            if not self.monitor.is_alive(timeout_seconds=self.timeout):
                self._is_stale = True
                break
            self._stop_event.wait(self.check_interval)

    def is_stale(self) -> bool:
        """Check if monitored process appears stale."""
        return self._is_stale


if __name__ == "__main__":
    # Test heartbeat monitor
    import tempfile
    import subprocess

    print("Testing HeartbeatMonitor...")

    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        temp_file = f.name

    try:
        monitor = HeartbeatMonitor(temp_file)

        # Test 1: Start and stop
        print("✓ Test 1: Start/stop heartbeat")
        monitor.start_heartbeat()
        time.sleep(0.5)
        assert monitor.is_alive(), "Should be alive after starting"
        print(f"  Heartbeat file created: {monitor.heartbeat_file.exists()}")
        monitor.stop_heartbeat()
        assert not monitor.lock_file.exists(), "Lock file should be removed"
        print(f"  Lock file removed: {not monitor.lock_file.exists()}")

        # Test 2: Staleness detection
        print("✓ Test 2: Staleness detection")
        monitor.start_heartbeat()
        time.sleep(0.5)
        assert monitor.is_alive(timeout_seconds=1), "Should be alive with 1s timeout"
        time.sleep(1.5)
        assert not monitor.is_alive(timeout_seconds=1), "Should be stale after 1.5s with 1s timeout"
        monitor.stop_heartbeat()

        print("✅ All tests passed!")

    finally:
        # Cleanup
        os.unlink(temp_file)
        for f in [temp_file + ".heartbeat", temp_file + ".lock"]:
            if os.path.exists(f):
                os.unlink(f)
