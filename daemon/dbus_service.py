"""D-Bus service for UI communication."""

import json
import os
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop


class HyprHaltService(dbus.service.Object):
    """D-Bus service for hyprhalt UI."""

    def __init__(self, manager, verbose: bool = False):
        self.manager = manager
        self.verbose = verbose
        self.bus = dbus.SessionBus()
        bus_name = dbus.service.BusName("org.hyprland.HyprHalt", self.bus)
        super().__init__(bus_name, "/org/hyprland/HyprHalt")
        self.cancelled = False
        self.force_killed = False
        self.apps_file = "/tmp/hyprhalt-apps.json"

    @dbus.service.method("org.hyprland.HyprHalt", in_signature="", out_signature="")
    def Cancel(self):
        """Cancel shutdown and exit."""
        print("!!! CANCEL REQUESTED VIA D-BUS !!!")
        self.cancelled = True
        print(f"!!! cancelled flag set to: {self.cancelled} !!!")

    @dbus.service.method("org.hyprland.HyprHalt", in_signature="", out_signature="")
    def ForceKill(self):
        """Force kill all apps immediately."""
        print("!!! FORCE KILL REQUESTED VIA D-BUS !!!")
        self.force_killed = True
        print(f"!!! force_killed flag set to: {self.force_killed} !!!")

    @dbus.service.method("org.hyprland.HyprHalt", in_signature="", out_signature="s")
    def GetAppsFile(self):
        """Get path to apps JSON file."""
        return self.apps_file

    def update_apps_file(self):
        """Write current app list to JSON file."""
        apps = []
        for app in self.manager.windows:
            apps.append(
                {
                    "appName": app.class_name,
                    "appStatus": app.status,
                    "pid": app.pid,
                }
            )

        try:
            with open(self.apps_file, "w") as f:
                json.dump(apps, f)
            if self.verbose:
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


def start_service(manager, verbose: bool = False):
    """Initialize D-Bus service and return the service object."""
    DBusGMainLoop(set_as_default=True)
    return HyprHaltService(manager, verbose)
