# Hyprhalt

A graceful shutdown utility for Hyprland with Quickshell UI.

## Features

- Graceful window closure via Hyprland IPC
- Immediate visual feedback with "Exiting..." overlay
- Detailed UI after 3 seconds if apps remain open
- Preserves layers (waybar, wallpapers) until final shutdown
- Progressive escalation: graceful → SIGTERM → SIGKILL

## Installation

### Arch

```bash
sudo paru -Sy hyprhalt
```
or
```bash
sudo yay -Sy hyprhalt
```

### Pipx

```bash
sudo pacman -Sy quickshell

pipx install git+https://github.com/knownasnaffy/hyprhalt.git
```

### Manual

```bash
sudo pacman -Sy quickshell

git clone https://github.com/knownasnaffy/hyprhalt
cd hyprhalt
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

## Attribution

Inspired by hyprshutdown.
This project is a clean-room reimplementation in Python using Quickshell.
