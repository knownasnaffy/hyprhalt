# Hyprhalt Specifications

## Project Structure

```
hyprhalt/
├── flow.md                    # This flow document
├── specs.md                   # This file
├── daemon/
│   ├── __init__.py
│   ├── main.py               # Entry point, arg parsing, fork logic
│   ├── hyprland_ipc.py       # Hyprland socket communication
│   ├── app_tracker.py        # App state management and lifecycle
│   ├── shutdown_manager.py   # Core shutdown orchestration
│   └── dbus_service.py       # D-Bus service implementation
├── ui/
│   ├── simple.qml            # "Exiting..." overlay (0-3s)
│   └── detailed.qml          # Full UI with app list and buttons (3s+)
├── pyproject.toml            # Python package config
└── README.md                 # Usage instructions
```

## File Specifications

### `daemon/main.py`
**Purpose**: CLI entry point and process management

**Functions**:
- `parse_args()` - Handle CLI arguments (--dry-run, --no-exit, --post-cmd, --vt)
- `daemonize()` - Fork process to survive parent death
- `get_ui_path() -> str` - Find UI files in installation directories
- `main()` - Initialize components and start shutdown flow

**Dependencies**: `argparse`, `os`, `sys`, `signal`

---

### `daemon/hyprland_ipc.py`
**Purpose**: Communicate with Hyprland via Unix socket

**Functions**:
- `get_socket_path()` - Resolve Hyprland socket from $HYPRLAND_INSTANCE_SIGNATURE
- `send_command(cmd: str) -> str` - Send command, return response
- `get_clients() -> list[dict]` - Query `j/clients`
- `get_layers() -> list[dict]` - Query `j/layers`
- `close_window(address: str) -> bool` - Dispatch `closewindow`
- `exit_hyprland()` - Dispatch `exit`
- `get_hyprland_pid() -> int` - Get Hyprland process PID from lock file

**Dependencies**: `socket`, `os`, `json`

---

### `daemon/app_tracker.py`
**Purpose**: Track app state and determine close methods

**Classes**:
```python
class App:
    address: str | None      # Window address (None for layers/children)
    pid: int
    class_name: str
    namespace: str | None    # For layer shells
    is_xwayland: bool
    is_layer: bool           # True for layer shells
    status: str              # "closing", "alive", "dead"
    
    def should_close_via_ipc() -> bool
    def is_alive() -> bool
    def quit()  # Graceful close
    def kill()  # SIGKILL
```

**Functions**:
- `get_all_apps() -> tuple[list[App], list[App]]` - Returns (windows, layers) separately
- `get_hyprland_children(parent_pid: int) -> list[App]` - Parse /proc for children
- `filter_own_process(apps: list[App], own_pid: int) -> list[App]` - Remove hyprhalt daemon

**Dependencies**: `os`, `signal`, `pathlib`

---

### `daemon/shutdown_manager.py`
**Purpose**: Orchestrate shutdown phases and timing

**Classes**:
```python
class ShutdownManager:
    windows: list[App]       # Regular windows and children
    layers: list[App]        # Layer shells (closed last)
    start_time: float
    simple_ui_process: subprocess.Popen | None   # Simple overlay process
    detailed_ui_process: subprocess.Popen | None # Detailed UI process
    dry_run: bool
    no_exit: bool
    post_cmd: str | None
    vt_switch: int | None
    own_pid: int
    
    def start()
    def show_simple_ui()          # Launch simple "Exiting..." overlay
    def show_detailed_ui()        # Replace with detailed UI at 3s
    def close_ui()                # Kill UI process
    def graceful_close_windows()  # Only close windows, not layers
    def close_all_layers()        # Close layers when windows done
    def poll_windows() -> bool    # Returns True if any windows alive
    def check_windowless_pids()   # SIGTERM if window closed but PID alive
    def elapsed() -> float
    def should_show_detailed_ui() -> bool  # elapsed > 3s and windows alive
    def escalate_sigterm()        # At 8s
    def escalate_sigkill()        # At 15s
    def finish_shutdown()         # Close layers, exit Hyprland, run post-cmd, switch VT
```

**Dependencies**: `time`, `threading`, `subprocess`

---

### `daemon/dbus_service.py`
**Purpose**: Expose D-Bus interface for Quickshell UI

**Classes**:
```python
class HyprHaltService:
    # D-Bus interface: org.hyprland.HyprHalt
    
    @dbus.service.method("Cancel")
    def cancel()
    
    @dbus.service.method("ForceKill")
    def force_kill()
    
    @dbus.service.signal(signature='aa{sv}')
    def AppsUpdated(apps: list[dict])
    
    @dbus.service.signal()
    def ShutdownComplete()
    
    @dbus.service.property(signature='aa{sv}')
    def Apps() -> list[dict]
    
    @dbus.service.property(signature='d')
    def ElapsedTime() -> float
```

**Functions**:
- `start_service(manager: ShutdownManager)` - Initialize D-Bus service
- `emit_app_update(windows: list[App])` - Convert windows to D-Bus format and emit (layers not included)

**Dependencies**: `dbus`, `dbus.service`, `dbus.mainloop.glib`, `GLib`

---

### `ui/simple.qml`
**Purpose**: Minimal "Exiting..." overlay (0-3s)

**Components**:
```qml
// Launched via: quickshell -c /path/to/simple.qml
LayerShellWindow {
    namespace: "hyprhalt-simple"
    layer: Layer.Overlay
    anchors.centerIn: parent
    
    Rectangle {
        color: "#80000000"  // Semi-transparent black
        radius: 10
        
        Text {
            text: "Exiting..."
            color: "white"
            font.pixelSize: 32
            anchors.centerIn: parent
        }
    }
}
```

**Styling**: Centered, minimal, no interaction

---

### `ui/detailed.qml`
**Purpose**: Full shutdown UI with app list and controls (3s+)

**Components**:
```qml
// Launched via: quickshell -c /path/to/detailed.qml
LayerShellWindow {
    namespace: "hyprhalt-detailed"
    layer: Layer.Overlay
    anchors: fill
    
    Column {
        Text { text: "Shutting down..." }
        
        // Window list (layers not shown)
        Repeater {
            model: shutdownService.apps
            Row {
                Text { text: modelData.class }
                Text { text: modelData.status }
            }
        }
        
        Row {
            Button {
                text: "Cancel"
                onClicked: shutdownService.cancel()
            }
            Button {
                text: "Force Kill"
                onClicked: shutdownService.forceKill()
            }
        }
    }
}

DBusService {
    id: shutdownService
    service: "org.hyprland.HyprHalt"
    path: "/org/hyprland/HyprHalt"
    
    property var apps: []
    signal appsUpdated()
    signal shutdownComplete()
    
    function cancel() { /* D-Bus call */ }
    function forceKill() { /* D-Bus call */ }
}
```

**Styling**: Detailed, interactive, real-time updates

---

### `pyproject.toml`
**Purpose**: Python package configuration

```toml
[project]
name = "hyprhalt"
version = "0.1.0"
dependencies = [
    "dbus-python>=1.3.2",
    "PyGObject>=3.42.0",
]

[project.scripts]
hyprhalt = "daemon.main:main"
```

---

## Launching Quickshell UI

**Simple overlay (0-3s)**:
```bash
quickshell --path /path/to/hyprhalt/ui/simple.qml
```

**Detailed UI (3s+)**:
```bash
# Kill simple UI first
kill $SIMPLE_UI_PID

# Launch detailed UI
quickshell --path /path/to/hyprhalt/ui/detailed.qml
```

**Installation path**: UI files will be installed to:
- System: `/usr/share/hyprhalt/ui/`
- User: `~/.local/share/hyprhalt/ui/`

The daemon will detect the installation location and use absolute paths.

---

## Data Flow

1. **Daemon → Hyprland IPC**: Query windows/layers separately, send close commands
2. **Daemon → /proc**: Check PIDs, send signals (exclude own PID)
3. **Daemon → D-Bus**: Publish window list (not layers) and status
4. **Quickshell → D-Bus**: Subscribe to updates, send commands
5. **D-Bus → Daemon**: Receive Cancel/ForceKill commands

## Shutdown Sequence

1. **Phase 1**: Close windows only (waybar, wallpapers stay active)
2. **Phase 2**: If windows closed → close layers → exit
3. **Phase 3**: If windows remain → show UI (layers still active for usable environment)
4. **Phase 4**: When windows finally close → close layers → exit

## Configuration

**CLI Arguments**:
- `--dry-run` - Don't actually close apps or exit Hyprland
- `--no-exit` - Don't exit Hyprland after apps close
- `--post-cmd CMD` - Run command after Hyprland exits
- `--vt N` - Switch to VT N after exit (for NVIDIA+SDDM)
- `--verbose` - Enable debug logging

**Environment Variables**:
- `HYPRLAND_INSTANCE_SIGNATURE` - Required to find Hyprland socket
- `XDG_RUNTIME_DIR` - Used to locate socket directory

## Dependencies

**Python Runtime**: Python 3.11+

**System Libraries**:
- `dbus` - D-Bus communication
- `glib` - Event loop for D-Bus service

**Quickshell**: Must be installed and in PATH

## Installation

```bash
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

# NVIDIA+SDDM fix
hyprhalt --vt 1 --post-cmd "systemctl poweroff"
```
