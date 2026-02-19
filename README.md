# Hyprhalt

A graceful shutdown utility for Hyprland with Quickshell UI. You can customize it to your heart's content.

## Demo

https://github.com/user-attachments/assets/e29ec0a5-8fac-4742-98ae-a93f40ee3996

I use it in my [personal dotfiles](https://github.com/knownasnaffy/dotfiles). Post-cmd [works with rofi](https://github.com/knownasnaffy/dotfiles/blob/cd0c2deb73654d01c2dbcf92c84b8d48bd6f0444/.config/rofi/powermenu/type-1/powermenu.sh#L61-L65) out of the box, unlike hyprshutdown, I don't know why. But it doesn't work from a quickshell process, I still don't know why, so I had to use `hyprctl dispatch exec hyprhalt --post-cmd 'systemctl poweroff'` in that.

## Features

- Graceful window closure via Hyprland IPC
- Immediate visual feedback with "Exiting..." overlay
- Detailed UI after 3 seconds if apps remain open
- Preserves layers (waybar, wallpapers) until final shutdown
- Progressive escalation: graceful → SIGTERM → SIGKILL

## Requirements

- Python 3.11+
- Hyprland
- Quickshell
- dbus-python
- PyGObject

## Installation

### Arch (AUR)

```bash
paru -Sy hyprhalt
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

### Enable blur in Hyprland

In your hyprland config, add the following window rule:

```hyprlang
layerrule {
	name = hyprhalt
	match:namespace = hyprhalt

	blur = on
	ignore_alpha = 0
}
```

## Usage

```bash
# Basic usage
hyprhalt

# Dry run (testing)
hyprhalt --dry-run

# With post-shutdown command
hyprhalt --post-cmd "systemctl poweroff"

# Explore
hyprhalt --help
```

## Customization

Hyprhalt can be customized via a configuration file located at:
- `$XDG_CONFIG_HOME/hyprhalt/config.toml` (usually `~/.config/hyprhalt/config.toml`)
- Or system-wide at `$XDG_CONFIG_DIRS/hyprhalt/config.toml` (usually `/etc/xdg/hyprhalt/config.toml`)

### Example Configuration

```toml
[timing]
sigterm_delay = 8    # Seconds before escalating to SIGTERM
sigkill_delay = 15   # Seconds before escalating to SIGKILL

[colors]
backdrop = "#0C0E14"           # Backdrop color (hex or "R,G,B")
backdrop_opacity = 0.7         # Backdrop transparency
modal_bg = "#1B1E2D"           # Modal background
modal_border = "#292E42"       # Modal border
text_primary = "#C0CAF5"       # Primary text
text_secondary = "#A9B1D6"     # Secondary text
accent_danger = "#F7768E"      # Danger/kill button
status_alive = "#E0AF68"       # Running app indicator
status_closed = "#9ECE6A"      # Closed app indicator

[ui]
border_radius = 16             # Main window border radius
modal_border_radius = 10       # Modal border radius
```

User configs override system configs. If no config exists, defaults are used.

## Attribution

Inspired by hyprshutdown.
This project is a clean-room reimplementation in Python using Quickshell.

## Todo

Todo, todo, todo todo todo todo todoooooooo, tododoo

- I'm thinking of showing a countdown inside the force close button along with a decreasing border length as an indicator.
- Better animations
