"""App tracking and lifecycle management."""

import os
import signal
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from . import hyprland_ipc


@dataclass
class App:
    """Represents an application to be closed."""

    address: Optional[str]
    pid: int
    class_name: str
    namespace: Optional[str]
    is_xwayland: bool
    is_layer: bool
    status: str = "alive"

    def should_close_via_ipc(self) -> bool:
        """Check if app should be closed via Hyprland IPC."""
        return self.address is not None and not self.is_layer

    def is_alive(self) -> bool:
        """Check if process is still alive."""
        if self.pid <= 0:
            return False

        try:
            os.kill(self.pid, 0)
            return True
        except OSError as e:
            if e.errno == 1:  # EPERM - process exists but no permission
                return True
            return False

    def quit(self):
        """Attempt graceful close."""
        if self.should_close_via_ipc():
            success = hyprland_ipc.close_window(self.address)
            if success:
                self.status = "closing"
        # For layers and children without addresses, don't send SIGTERM yet
        # They will be handled by check_windowless_pids() or escalation

    def kill(self):
        """Force kill with SIGKILL."""
        if self.pid > 0:
            try:
                os.kill(self.pid, signal.SIGKILL)
                self.status = "killed"
            except OSError:
                pass


def get_all_apps() -> tuple[list[App], list[App]]:
    """Get all apps, separated into windows and layers."""
    windows = []
    layers = []

    # Get client windows
    clients = hyprland_ipc.get_clients()
    for client in clients:
        app = App(
            address=client.get("address"),
            pid=client.get("pid", -1),
            class_name=client.get("class", "unknown"),
            namespace=None,
            is_xwayland=client.get("xwayland", False),
            is_layer=False,
        )
        windows.append(app)

    # Get layer shells
    layer_data = hyprland_ipc.get_layers()
    for layer in layer_data:
        app = App(
            address=layer.get("address"),
            pid=layer.get("pid", -1),
            class_name=layer.get("namespace", "unknown"),
            namespace=layer.get("namespace"),
            is_xwayland=False,
            is_layer=True,
        )
        layers.append(app)

    # Get Hyprland children
    hyprland_pid = hyprland_ipc.get_hyprland_pid()
    if hyprland_pid:
        children = get_hyprland_children(hyprland_pid)
        windows.extend(children)

    return windows, layers


def get_hyprland_children(parent_pid: int) -> list[App]:
    """Get all child processes of Hyprland."""
    children = []

    try:
        for pid_dir in Path("/proc").iterdir():
            if not pid_dir.name.isdigit():
                continue

            pid = int(pid_dir.name)
            stat_file = pid_dir / "stat"

            if not stat_file.exists():
                continue

            try:
                with open(stat_file) as f:
                    stat = f.read()
                    # Parse stat file: pid (comm) state ppid ...
                    parts = stat.split(")")
                    if len(parts) < 2:
                        continue

                    fields = parts[1].strip().split()
                    if len(fields) < 2:
                        continue

                    ppid = int(fields[1])
                    if ppid != parent_pid:
                        continue

                    # Get process name
                    comm_file = pid_dir / "comm"
                    if comm_file.exists():
                        with open(comm_file) as cf:
                            name = cf.read().strip()
                    else:
                        name = "unknown"

                    # Skip Xwayland
                    if name == "Xwayland":
                        continue

                    app = App(
                        address=None,
                        pid=pid,
                        class_name=name,
                        namespace=None,
                        is_xwayland=False,
                        is_layer=False,
                    )
                    children.append(app)

            except (IOError, ValueError):
                continue

    except IOError:
        pass

    return children


def filter_own_process(apps: list[App], own_pid: int) -> list[App]:
    """Remove quickshutdown daemon from app list."""
    return [app for app in apps if app.pid != own_pid]
