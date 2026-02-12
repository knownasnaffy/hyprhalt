# Development Status

## Completed ✓

### Core Daemon
- [x] Hyprland IPC communication (`hyprland_ipc.py`)
  - Socket communication
  - Get clients/layers
  - Close windows
  - Exit Hyprland
  
- [x] App tracking (`app_tracker.py`)
  - App dataclass with lifecycle methods
  - Parse windows, layers, and Hyprland children
  - Filter own process
  
- [x] Shutdown manager (`shutdown_manager.py`)
  - UI control (simple → detailed transition)
  - Graceful close → SIGTERM → SIGKILL escalation
  - Window/layer separation
  - Post-command and VT switch support
  
- [x] Main entry point (`main.py`)
  - Argument parsing
  - Daemonization
  - 3-second polling loop
  - Escalation timing (8s, 15s)

### UI
- [x] Simple overlay (`ui/simple.qml`)
  - Minimal "Exiting..." display
  - Shows immediately on start
  
- [x] Detailed UI (`ui/detailed.qml`)
  - App list display
  - Cancel and Force Kill buttons
  - Basic layout (D-Bus integration pending)

### Project Setup
- [x] Git repository initialized
- [x] Project structure
- [x] pyproject.toml
- [x] README.md
- [x] .gitignore

## Pending ⏳

### D-Bus Integration
- [ ] `dbus_service.py` - D-Bus service for UI communication
- [ ] Update `detailed.qml` to connect to D-Bus
- [ ] Real-time app list updates
- [ ] Cancel/Force Kill button functionality

### Testing
- [ ] Test with real Hyprland session
- [ ] Test dry-run mode
- [ ] Test UI transitions
- [ ] Test escalation timing

### Polish
- [ ] Better error handling
- [ ] Logging system
- [ ] UI styling improvements
- [ ] Installation script

## Testing the Current Build

```bash
# Install in development mode
cd quickshutdown
pip install -e .

# Test dry run (safe, won't close anything)
quickshutdown --dry-run --verbose --no-fork

# Test with UI (will show overlays but not close apps)
quickshutdown --dry-run --no-fork
```

## Next Steps

1. Implement D-Bus service for UI communication
2. Test basic functionality in Hyprland
3. Add proper logging
4. Polish UI styling
5. Create installation instructions
