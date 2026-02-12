"""Main entry point for quickshutdown."""

import argparse
import os
import signal
import sys
import time
from gi.repository import GLib

from .app_tracker import get_all_apps, filter_own_process
from .shutdown_manager import ShutdownManager
from .dbus_service import start_service


def daemonize():
    """Fork process to survive parent death."""
    # First fork
    pid = os.fork()
    if pid > 0:
        sys.exit(0)

    # Become session leader
    os.setsid()

    # Ignore SIGHUP
    signal.signal(signal.SIGHUP, signal.SIG_IGN)

    # Second fork
    pid = os.fork()
    if pid > 0:
        sys.exit(0)

    # Set umask
    os.umask(0)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Graceful shutdown utility for Hyprland"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't actually close apps or exit Hyprland",
    )
    parser.add_argument(
        "--no-exit",
        action="store_true",
        help="Don't exit Hyprland after apps close",
    )
    parser.add_argument(
        "--post-cmd",
        type=str,
        help="Command to run after Hyprland exits",
    )
    parser.add_argument(
        "--vt",
        type=int,
        help="Switch to VT N after Hyprland exits (for NVIDIA+SDDM)",
    )
    parser.add_argument(
        "--no-fork",
        action="store_true",
        help="Don't daemonize (run in foreground)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Check we're running under Hyprland
    if not os.getenv("HYPRLAND_INSTANCE_SIGNATURE"):
        print("Error: Not running under Hyprland", file=sys.stderr)
        sys.exit(1)

    # Daemonize unless --no-fork
    if not args.no_fork:
        daemonize()
    else:
        signal.signal(signal.SIGHUP, signal.SIG_IGN)

    # Get all apps
    try:
        windows, layers = get_all_apps()
    except Exception as e:
        print(f"Error getting apps: {e}", file=sys.stderr)
        sys.exit(1)

    # Filter out our own process
    windows = filter_own_process(windows, os.getpid())

    if args.verbose:
        print(f"Found {len(windows)} windows and {len(layers)} layers")

    # Create shutdown manager
    manager = ShutdownManager(
        windows=windows,
        layers=layers,
        dry_run=args.dry_run,
        no_exit=args.no_exit,
        post_cmd=args.post_cmd,
        vt_switch=args.vt,
    )

    # Show simple UI immediately
    manager.show_simple_ui()

    # Start graceful close
    manager.graceful_close_windows()

    # Poll for 3 seconds
    while manager.elapsed() < 3.0:
        time.sleep(0.2)
        manager.check_windowless_pids()

        if not manager.poll_windows():
            # All windows closed before 3s
            if args.verbose:
                print("All windows closed within 3 seconds")
            manager.finish_shutdown()
            sys.exit(0)

    # Check if we need detailed UI
    if not manager.poll_windows():
        # All closed right at 3s mark
        if args.verbose:
            print("All windows closed at 3 second mark")
        manager.finish_shutdown()
        sys.exit(0)

    # Show detailed UI
    # Show detailed UI
    if args.verbose:
        print(f"{len(manager.windows)} windows remain, showing detailed UI")
    
    # Start D-Bus service
    try:
        dbus_service = start_service(manager)
        if args.verbose:
            print("D-Bus service started")
        # Write initial apps file before showing UI
        dbus_service.update_apps_file()
    except Exception as e:
        print(f"Warning: Failed to start D-Bus service: {e}")
        dbus_service = None
    
    manager.show_detailed_ui()

    # Continue polling with escalation
    last_sigterm = 0
    last_sigkill = 0
    
    # Create GLib main loop for D-Bus
    main_loop = GLib.MainLoop()
    
    def check_status():
        """Periodic check called by GLib timeout."""
        nonlocal last_sigterm, last_sigkill
        
        manager.check_windowless_pids()
        
        # Update apps file for UI
        if dbus_service:
            dbus_service.update_apps_file()

        # Check for cancel
        if dbus_service and dbus_service.cancelled:
            if args.verbose:
                print("Shutdown cancelled by user")
            manager.close_ui()
            if dbus_service:
                dbus_service.cleanup()
            main_loop.quit()
            return False

        # Check for force kill
        if dbus_service and dbus_service.force_killed:
            if args.verbose:
                print("Force kill requested by user")
            manager.escalate_sigkill()
            time.sleep(1)
            manager.finish_shutdown()
            if dbus_service:
                dbus_service.cleanup()
            main_loop.quit()
            return False

        if not manager.poll_windows():
            # All windows closed
            if args.verbose:
                print("All windows closed")
            manager.finish_shutdown()
            if dbus_service:
                dbus_service.cleanup()
            main_loop.quit()
            return False

        elapsed = manager.elapsed()

        # Escalate at 8 seconds
        if elapsed >= 8.0 and last_sigterm == 0:
            if args.verbose:
                print("8 seconds elapsed, escalating to SIGTERM")
            manager.escalate_sigterm()
            last_sigterm = elapsed

        # Escalate at 15 seconds
        if elapsed >= 15.0 and last_sigkill == 0:
            if args.verbose:
                print("15 seconds elapsed, escalating to SIGKILL")
            manager.escalate_sigkill()
            last_sigkill = elapsed

            # Force finish after SIGKILL
            time.sleep(1)
            manager.finish_shutdown()
            if dbus_service:
                dbus_service.cleanup()
            main_loop.quit()
            return False
        
        return True  # Continue calling
    
    # Schedule periodic checks every 500ms
    GLib.timeout_add(500, check_status)
    
    # Run main loop
    try:
        main_loop.run()
    except KeyboardInterrupt:
        if args.verbose:
            print("Interrupted by user")
        manager.close_ui()
    
    sys.exit(0)


if __name__ == "__main__":
    main()
