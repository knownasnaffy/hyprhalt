# Hyprhalt

A graceful shutdown utility for Hyprland with Quickshell UI.

## Features

- Graceful window closure via Hyprland IPC
- Immediate visual feedback with "Exiting..." overlay
- Detailed UI after 3 seconds if apps remain open
- Preserves layers (waybar, wallpapers) until final shutdown
- Progressive escalation: graceful → SIGTERM → SIGKILL

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Basic usage
hyprhalt

# Dry run (testing)
hyprhalt --dry-run

# With post-shutdown command
hyprhalt --post-cmd "systemctl poweroff"
```

## Requirements

- Python 3.11+
- Hyprland
- Quickshell
- dbus-python
- PyGObject
