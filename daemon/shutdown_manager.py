"""Core shutdown orchestration."""

import json
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Optional

from . import hyprland_ipc
from .app_tracker import App
from .config import Config


class ShutdownManager:
    """Manages the shutdown process."""

    def __init__(
        self,
        windows: list[App],
        layers: list[App],
        config: Config,
        dry_run: bool = False,
        no_exit: bool = False,
        post_cmd: Optional[str] = None,
        vt_switch: Optional[int] = None,
        verbose: bool = False,
        custom_text: str = "Exiting",
    ):
        self.windows = windows
        self.layers = layers
        self.config = config
        self.start_time = time.time()
        self.ui_process: Optional[subprocess.Popen] = None
        self.dry_run = dry_run
        self.no_exit = no_exit
        self.post_cmd = post_cmd
        self.vt_switch = vt_switch
        self.verbose = verbose
        self.own_pid = os.getpid()
        self._windowless_pids_termed: set[int] = set()
        self.custom_text = custom_text

    def elapsed(self) -> float:
        """Get elapsed time since start."""
        return time.time() - self.start_time

    def show_ui(self):
        """Launch unified shell UI."""
        self._write_config_for_ui()
        ui_path = self._get_ui_path("shell.qml")
        if ui_path:
            try:
                runtime_dir = os.getenv("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
                ui_log = open(f"{runtime_dir}/hyprhalt-ui.log", "w")
                self.ui_process = subprocess.Popen(
                    ["quickshell", "-p", str(ui_path)],
                    stdout=ui_log,
                    stderr=ui_log,
                )
            except FileNotFoundError:
                print("Warning: quickshell not found, running without UI")
            except Exception as e:
                print(f"Warning: Failed to start UI: {e}")

    def close_ui(self):
        """Kill UI process."""
        if self.ui_process:
            try:
                self.ui_process.terminate()
                self.ui_process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.ui_process.kill()
            self.ui_process = None

    def graceful_close_windows(self):
        """Close all windows gracefully."""
        if self.dry_run:
            print(f"[DRY RUN] Would close {len(self.windows)} windows")
            return

        for app in self.windows:
            app.quit()

    def close_all_layers(self):
        """Close all layer shells."""
        if self.dry_run:
            print(f"[DRY RUN] Would close {len(self.layers)} layers")
            return

        for layer in self.layers:
            # Layers need SIGTERM since they can't use closewindow
            if layer.pid > 0:
                try:
                    os.kill(layer.pid, signal.SIGTERM)
                except OSError:
                    pass

    def poll_windows(self) -> bool:
        """Check window status and return True if any are alive."""
        # Update status
        for app in self.windows:
            if not app.is_alive():
                app.status = "dead"

        # Remove dead apps
        self.windows = [app for app in self.windows if app.is_alive()]

        return len(self.windows) > 0

    def check_windowless_pids(self):
        """Send SIGTERM to PIDs whose windows closed but process remains."""
        if self.dry_run:
            return

        # Get current client PIDs
        try:
            clients = hyprland_ipc.get_clients()
            window_pids = {c.get("pid") for c in clients if c.get("pid")}
        except Exception:
            return

        for app in self.windows:
            # Only check apps that originally had a window address
            if app.pid <= 0 or not app.address:
                continue

            if app.pid in self._windowless_pids_termed:
                continue

            # If app's window closed but PID is still alive, SIGTERM it
            if app.pid not in window_pids and app.is_alive():
                if self.verbose:
                    print(
                        f"Window closed but PID {app.pid} ({app.class_name}) alive, sending SIGTERM"
                    )
                try:
                    os.kill(app.pid, 15)  # SIGTERM
                    self._windowless_pids_termed.add(app.pid)
                except OSError:
                    pass

    def escalate_sigterm(self):
        """Re-send SIGTERM to remaining windows."""
        if self.dry_run:
            print(f"[DRY RUN] Would SIGTERM {len(self.windows)} windows")
            return

        print(f"Escalating: sending SIGTERM to {len(self.windows)} remaining windows")
        for app in self.windows:
            if app.pid > 0:
                try:
                    os.kill(app.pid, 15)  # SIGTERM
                except OSError:
                    pass

    def escalate_sigkill(self):
        """Force kill remaining windows."""
        if self.dry_run:
            print(f"[DRY RUN] Would SIGKILL {len(self.windows)} windows")
            return

        print(f"Escalating: sending SIGKILL to {len(self.windows)} remaining windows")
        for app in self.windows:
            app.kill()

    def finish_shutdown(self):
        """Complete shutdown sequence."""
        self.close_ui()
        self.close_all_layers()

        if not self.no_exit:
            if self.dry_run:
                print("[DRY RUN] Would exit Hyprland")
            else:
                hyprland_ipc.exit_hyprland()

        # VT switch for NVIDIA+SDDM
        if self.vt_switch:
            if self.dry_run:
                print(f"[DRY RUN] Would switch to VT {self.vt_switch}")
            else:
                try:
                    subprocess.run(
                        ["sudo", "-n", "chvt", str(self.vt_switch)],
                        check=False,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                except FileNotFoundError:
                    pass

        # Run post-exit command
        if self.post_cmd:
            if self.dry_run:
                print(f"[DRY RUN] Would execute post-command: {self.post_cmd}")
            else:
                try:
                    # Run asynchronously like hyprshutdown does
                    subprocess.Popen(
                        ["/bin/sh", "-c", self.post_cmd],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                except Exception as e:
                    print(f"Post-command failed: {e}")

    def _get_ui_path(self, filename: str) -> Optional[Path]:
        """Find UI file in installation directories."""
        search_paths = [
            Path(__file__).parent.parent / "ui" / filename,  # Development
            Path.home() / ".local/share/hyprhalt/ui" / filename,  # User install
            Path("/usr/share/hyprhalt/ui") / filename,  # System install
        ]

        for path in search_paths:
            if path.exists():
                return path

        return None

    def _write_config_for_ui(self):
        """Write config to JSON file for UI consumption."""
        config_data = {
            "colors": {
                "backdrop": self.config.colors.backdrop,
                "backdrop_opacity": self.config.colors.backdrop_opacity,
                "modal_bg": self.config.colors.modal_bg,
                "modal_border": self.config.colors.modal_border,
                "text_primary": self.config.colors.text_primary,
                "text_secondary": self.config.colors.text_secondary,
                "accent_danger": self.config.colors.accent_danger,
                "status_alive": self.config.colors.status_alive,
                "status_closed": self.config.colors.status_closed,
            },
            "ui": {
                "border_radius": self.config.ui.border_radius,
                "modal_border_radius": self.config.ui.modal_border_radius,
            },
            "text": {
                "exiting": self.custom_text,
            },
        }

        runtime_dir = os.getenv("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
        config_path = f"{runtime_dir}/hyprhalt-config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)
