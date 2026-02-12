"""D-Bus service for UI communication."""

import json
import os
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib


class QuickShutdownService(dbus.service.Object):
    """D-Bus service for quickshutdown UI."""
    
    def __init__(self, manager):
        self.manager = manager
        self.bus = dbus.SessionBus()
        bus_name = dbus.service.BusName("org.hyprland.QuickShutdown", self.bus)
        super().__init__(bus_name, "/org/hyprland/QuickShutdown")
        self.cancelled = False
        self.force_killed = False
        self.apps_file = "/tmp/quickshutdown-apps.json"
    
    @dbus.service.method("org.hyprland.QuickShutdown", in_signature='', out_signature='')
    def Cancel(self):
        """Cancel shutdown and exit."""
        print("Cancel requested via D-Bus")
        self.cancelled = True
    
    @dbus.service.method("org.hyprland.QuickShutdown", in_signature='', out_signature='')
    def ForceKill(self):
        """Force kill all apps immediately."""
        print("Force kill requested via D-Bus")
        self.force_killed = True
    
    @dbus.service.method("org.hyprland.QuickShutdown", in_signature='', out_signature='s')
    def GetAppsFile(self):
        """Get path to apps JSON file."""
        return self.apps_file
    
    def update_apps_file(self):
        """Write current app list to JSON file."""
        apps = []
        for app in self.manager.windows:
            apps.append({
                'appName': app.class_name,
                'appStatus': app.status,
                'pid': app.pid,
            })
        
        try:
            with open(self.apps_file, 'w') as f:
                json.dump(apps, f)
            print(f"Updated apps file with {len(apps)} apps")
        except Exception as e:
            print(f"Failed to write apps file: {e}")
    
    def cleanup(self):
        """Remove temp file."""
        try:
            if os.path.exists(self.apps_file):
                os.remove(self.apps_file)
        except Exception:
            pass


def start_service(manager):
    """Initialize D-Bus service and return the service object."""
    DBusGMainLoop(set_as_default=True)
    return QuickShutdownService(manager)
