# Hyprhalt Flow

## Overview
A Python-based graceful shutdown utility for Hyprland with a Quickshell UI that only appears if processes take >3 seconds to close.

## Execution Flow

### Phase 1: Initialization (0s)
1. User runs `hyprhalt` command
2. Daemon forks/daemonizes to survive parent death
3. **Immediately show simple "Exiting..." overlay** (minimal UI)
4. Query Hyprland IPC for all apps:
   - Windows via `j/clients`
   - Layer shells via `j/layers` (stored separately, not closed yet)
   - Direct children of Hyprland process
5. Store app list with metadata (address, PID, class, namespace)
6. Identify hyprhalt's own PID to exclude from closure
7. Start 3-second timer

### Phase 2: Graceful Shutdown (0-3s)
1. **Simple "Exiting..." overlay remains visible**
2. For each **window** (not layers yet), attempt graceful close:
   - **Windows with address**: Use Hyprland IPC `closewindow address:{addr}`
   - **Windowless children**: Send SIGTERM to PID (exclude own PID)
3. Poll app status every 200ms:
   - Check PIDs with `kill(pid, 0)`
   - Query `j/clients` to verify windows closed
   - Remove dead apps from tracking list
4. If window closes but PID alive: send SIGTERM to process
5. **Layers are NOT closed yet** - keeps waybar, wallpapers, etc. functional

### Phase 3: UI Decision Point (3s)
**If all windows closed**:
- Close simple overlay
- Close all layers (waybar, wallpapers, etc.)
- Exit Hyprland immediately
- Run post-exit command if specified
- Terminate daemon

**If windows still alive**:
- **Replace simple overlay with detailed UI** showing:
  - List of remaining windows
  - Cancel and Force Kill buttons
- Continue to Phase 4
- **Layers still remain active** (environment stays functional)

### Phase 4: UI Display (3s+)
1. Detailed UI shows:
   - List of remaining windows (class name, status)
   - "Cancel" button (abort shutdown, restore apps)
   - "Force Kill" button (SIGKILL all immediately)
2. Daemon continues polling every 500ms:
   - Update window list (still ignoring layers)
   - Send status to Quickshell via D-Bus signals
   - Remove closed apps from UI
3. UI updates in real-time as apps close

### Phase 5: Escalation (8s+)
1. At 8 seconds total elapsed time:
   - Send SIGTERM again to all remaining windows
2. At 15 seconds total elapsed time:
   - Send SIGKILL to all remaining windows
   - Close all layers (waybar, wallpapers, hyprhalt UI)
   - Exit Hyprland
   - Run post-exit command

### Phase 6: Completion
**User clicks "Force Kill"**:
- SIGKILL all remaining windows immediately
- Close all layers
- Close UI
- Exit Hyprland
- Run post-exit command

**User clicks "Cancel"**:
- Stop all shutdown operations
- Close detailed UI
- Daemon exits (Hyprland and all layers stay running)

**All windows close naturally**:
- Close detailed UI automatically
- Close all layers
- Exit Hyprland
- Run post-exit command

## State Transitions

```
START → SHOW_SIMPLE_UI → GRACEFUL_CLOSE_WINDOWS → [3s check]
                                                      ↓
                                              [All windows closed?]
                                              ↙                    ↘
                                            YES                    NO
                                             ↓                      ↓
                                      CLOSE_SIMPLE_UI      SHOW_DETAILED_UI
                                             ↓                      ↓
                                      CLOSE_LAYERS       [Continue polling windows]
                                             ↓                      ↓
                                      EXIT_HYPRLAND        [8s: Re-SIGTERM]
                                                                   ↓
                                                         [15s: SIGKILL windows]
                                                                   ↓
                                                           CLOSE_DETAILED_UI
                                                                   ↓
                                                            CLOSE_LAYERS
                                                                   ↓
                                                            EXIT_HYPRLAND
```

## D-Bus Interface

**Service**: `org.hyprland.HyprHalt`
**Object Path**: `/org/hyprland/HyprHalt`

**Methods**:
- `Cancel()` - Abort shutdown
- `ForceKill()` - SIGKILL all apps immediately

**Signals**:
- `AppsUpdated(apps: array)` - Emitted when app list changes
- `ShutdownComplete()` - Emitted when all apps closed

**Properties**:
- `Apps` - Current list of apps (read-only)
- `ElapsedTime` - Seconds since start (read-only)

## Error Handling

- **Hyprland IPC failure**: Log error, fall back to SIGTERM for all
- **D-Bus connection failure**: Continue without UI, use timeouts only
- **Quickshell fails to start**: Continue with timeout-based SIGKILL
- **Permission denied (SIGTERM/SIGKILL)**: Log warning, skip that app
