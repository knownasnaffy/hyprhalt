"""Configuration management for hyprhalt."""

import logging
import os
from pathlib import Path
from typing import NamedTuple

try:
    import tomllib
except ImportError:
    import tomli as tomllib

logger = logging.getLogger("hyprhalt")


class TimingConfig(NamedTuple):
    sigterm_delay: int = 8
    sigkill_delay: int = 15


class ColorConfig(NamedTuple):
    backdrop: str = "12,14,20"
    backdrop_opacity: float = 0.7
    modal_bg: str = "27,30,45"
    modal_border: str = "41,46,66"
    text_primary: str = "192,202,245"
    text_secondary: str = "169,177,214"
    accent_danger: str = "247,118,142"
    status_alive: str = "224,175,104"
    status_closed: str = "158,206,106"


class UIConfig(NamedTuple):
    border_radius: int = 16
    modal_border_radius: int = 10


class Config(NamedTuple):
    timing: TimingConfig = TimingConfig()
    colors: ColorConfig = ColorConfig()
    ui: UIConfig = UIConfig()


def hex_to_rgb(hex_color: str) -> str:
    """Convert hex color (#RRGGBB) to 'R,G,B' string."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: #{hex_color} (must be 6 characters)")
    try:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    except ValueError:
        raise ValueError(f"Invalid hex color: #{hex_color} (must contain valid hex digits)")
    return f"{r},{g},{b}"


def validate_config(config: Config) -> None:
    """Validate configuration values."""
    # Validate timing
    if config.timing.sigterm_delay < 0:
        raise ValueError(f"sigterm_delay must be non-negative, got {config.timing.sigterm_delay}")
    if config.timing.sigkill_delay < 0:
        raise ValueError(f"sigkill_delay must be non-negative, got {config.timing.sigkill_delay}")
    if config.timing.sigkill_delay < config.timing.sigterm_delay:
        raise ValueError(
            f"sigkill_delay ({config.timing.sigkill_delay}) must be >= sigterm_delay ({config.timing.sigterm_delay})"
        )
    
    # Validate colors
    if not (0 <= config.colors.backdrop_opacity <= 1):
        raise ValueError(f"backdrop_opacity must be between 0 and 1, got {config.colors.backdrop_opacity}")
    
    # Validate UI
    if config.ui.border_radius < 0:
        raise ValueError(f"border_radius must be non-negative, got {config.ui.border_radius}")
    if config.ui.modal_border_radius < 0:
        raise ValueError(f"modal_border_radius must be non-negative, got {config.ui.modal_border_radius}")


def load_config() -> Config:
    """Load configuration from XDG config directories."""
    # Build search paths in priority order
    search_paths = []
    
    # 1. XDG_CONFIG_HOME (or ~/.config fallback)
    xdg_config_home = os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    search_paths.append(Path(xdg_config_home) / "hyprhalt" / "config.toml")
    
    # 2. XDG_CONFIG_DIRS (colon-separated, defaults to /etc/xdg)
    xdg_config_dirs = os.getenv("XDG_CONFIG_DIRS", "/etc/xdg")
    for config_dir in xdg_config_dirs.split(":"):
        if config_dir:
            search_paths.append(Path(config_dir) / "hyprhalt" / "config.toml")
    
    # Find first existing config file
    config_file = None
    for path in search_paths:
        if path.exists():
            config_file = path
            break
    
    if not config_file:
        return Config()

    try:
        with open(config_file, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        logger.error(f"Failed to parse config file {config_file}: {e}")
        raise

    try:
        # Parse timing
        timing_data = data.get("timing", {})
        timing = TimingConfig(
            sigterm_delay=timing_data.get("sigterm_delay", 8),
            sigkill_delay=timing_data.get("sigkill_delay", 15),
        )

        # Parse colors (convert hex to RGB if needed)
        colors_data = data.get("colors", {})
        colors = ColorConfig(
            backdrop=(
                hex_to_rgb(colors_data["backdrop"])
                if "backdrop" in colors_data
                else "12,14,20"
            ),
            backdrop_opacity=colors_data.get("backdrop_opacity", 0.7),
            modal_bg=(
                hex_to_rgb(colors_data["modal_bg"])
                if "modal_bg" in colors_data
                else "27,30,45"
            ),
            modal_border=(
                hex_to_rgb(colors_data["modal_border"])
                if "modal_border" in colors_data
                else "41,46,66"
            ),
            text_primary=(
                hex_to_rgb(colors_data["text_primary"])
                if "text_primary" in colors_data
                else "192,202,245"
            ),
            text_secondary=(
                hex_to_rgb(colors_data["text_secondary"])
                if "text_secondary" in colors_data
                else "169,177,214"
            ),
            accent_danger=(
                hex_to_rgb(colors_data["accent_danger"])
                if "accent_danger" in colors_data
                else "247,118,142"
            ),
            status_alive=(
                hex_to_rgb(colors_data["status_alive"])
                if "status_alive" in colors_data
                else "224,175,104"
            ),
            status_closed=(
                hex_to_rgb(colors_data["status_closed"])
                if "status_closed" in colors_data
                else "158,206,106"
            ),
        )

        # Parse UI
        ui_data = data.get("ui", {})
        ui = UIConfig(
            border_radius=ui_data.get("border_radius", 16),
            modal_border_radius=ui_data.get("modal_border_radius", 10),
        )

        config = Config(timing=timing, colors=colors, ui=ui)
        validate_config(config)
        return config
    except (ValueError, KeyError) as e:
        logger.error(f"Invalid configuration in {config_file}: {e}")
        raise


def create_default_config():
    """Create default config file at $XDG_CONFIG_HOME/hyprhalt/config.toml."""
    xdg_config_home = os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    config_dir = Path(xdg_config_home) / "hyprhalt"
    config_file = config_dir / "config.toml"

    if config_file.exists():
        print(f"Config file already exists at {config_file}")
        response = input("Overwrite? [y/N]: ").strip().lower()
        if response != "y":
            print("Aborted")
            return

    config_dir.mkdir(parents=True, exist_ok=True)

    default_config = """# Hyprhalt Configuration

[timing]
sigterm_delay = 8
sigkill_delay = 15

[colors]
backdrop = "#0c0e14"
backdrop_opacity = 0.7
modal_bg = "#1b1e2d"
modal_border = "#292e42"
text_primary = "#c0caf5"
text_secondary = "#a9b1d6"
accent_danger = "#f7768e"
status_alive = "#e0af68"
status_closed = "#9ece6a"

[ui]
border_radius = 16
modal_border_radius = 10
"""

    with open(config_file, "w") as f:
        f.write(default_config)

    print(f"Created default config at {config_file}")
