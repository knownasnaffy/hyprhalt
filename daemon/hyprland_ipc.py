"""Hyprland IPC communication module."""

import json
import os
import socket
from pathlib import Path
from typing import Optional


def get_socket_path() -> str:
    """Get Hyprland socket path from environment."""
    his = os.getenv("HYPRLAND_INSTANCE_SIGNATURE")
    if not his:
        raise RuntimeError(
            "HYPRLAND_INSTANCE_SIGNATURE not set - not running under Hyprland?"
        )

    runtime_dir = os.getenv("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    return f"{runtime_dir}/hypr/{his}/.socket.sock"


def send_command(cmd: str) -> str:
    """Send command to Hyprland socket and return response."""
    sock_path = get_socket_path()

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(5.0)

    try:
        sock.connect(sock_path)
        sock.sendall(cmd.encode())

        response = b""
        while True:
            chunk = sock.recv(8192)
            if not chunk:
                break
            response += chunk

        return response.decode(errors="replace")
    finally:
        sock.close()


def get_clients() -> list[dict]:
    """Query Hyprland for all client windows."""
    response = send_command("j/clients")
    return json.loads(response)


def get_layers() -> list[dict]:
    """Query Hyprland for all layer shell surfaces."""
    response = send_command("j/layers")
    data = json.loads(response)

    # Flatten layer structure
    layers = []
    for monitor_data in data.values():
        if "levels" in monitor_data:
            for level_data in monitor_data["levels"].values():
                layers.extend(level_data)

    return layers


def close_window(address: str) -> bool:
    """Close window via Hyprland IPC."""
    response = send_command(f"/dispatch closewindow address:{address}")
    return response.strip() == "ok"


def exit_hyprland():
    """Exit Hyprland."""
    send_command("/dispatch exit")


def get_hyprland_pid() -> Optional[int]:
    """Get Hyprland process PID from lock file."""
    his = os.getenv("HYPRLAND_INSTANCE_SIGNATURE")
    if not his:
        return None

    runtime_dir = os.getenv("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    lock_file = Path(f"{runtime_dir}/hypr/{his}/hyprland.lock")

    if not lock_file.exists():
        return None

    try:
        with open(lock_file) as f:
            return int(f.readline().strip())
    except (ValueError, IOError):
        return None
