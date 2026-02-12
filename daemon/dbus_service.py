"""D-Bus service for UI communication."""

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
    
    @dbus.service.method("org.hyprland.QuickShutdown", in_signature='', out_signature='aa{sv}')
    def GetApps(self):
        """Get current app list."""
        apps = []
        for app in self.manager.windows:
            apps.append({
                'name': app.class_name,
                'status': app.status,
                'pid': app.pid,
            })
        return apps


def start_service(manager):
    """Initialize D-Bus service and return the service object."""
    DBusGMainLoop(set_as_default=True)
    return QuickShutdownService(manager)
