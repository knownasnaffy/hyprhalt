---
date: February 2026
section: 1
title: HYPRHALT
---

# NAME

hyprhalt - graceful shutdown utility for Hyprland with Quickshell UI

# SYNOPSIS

**hyprhalt** \[**-h**\] \[**\--dry-run**\] \[**\--no-exit**\]
\[**\--post-cmd** **command**\] \[**\--vt** **N**\] \[**\--no-fork**\]
\[**\--verbose**\] \[**\--text** **text**\]

# DESCRIPTION

**hyprhalt** is a graceful shutdown utility for Hyprland that
progressively closes applications while presenting a Quickshell-based
user interface.

It requests window closure via Hyprland IPC and escalates termination in
stages if applications remain open: graceful close, then SIGTERM, and
finally SIGKILL.

By default, hyprhalt exits Hyprland after all applications have been
closed. This behavior can be modified with command-line options.

# OPTIONS

**-h**, **\--help**

:   Show help information and exit.

<!-- -->

**\--dry-run**

:   Perform a simulation without actually closing applications or
    exiting Hyprland.

<!-- -->

**\--no-exit**

:   Do not exit Hyprland after all applications have been closed.

<!-- -->

**\--post-cmd*** command*

:   Execute *command* after Hyprland exits.

<!-- -->

**\--vt*** N*

:   Switch to virtual terminal *N* after Hyprland exits. This may be
    required with certain display manager configurations (e.g., SDDM,
    which commonly runs on VT 2).

<!-- -->

**\--no-fork**

:   Do not daemonize. Run in the foreground instead of forking into the
    background.

<!-- -->

**\--verbose**

:   Enable verbose logging output.

<!-- -->

**\--text*** text*

:   Override the default UI text (\"Exiting\") with custom *text.*

# BEHAVIOR

hyprhalt performs shutdown in progressive stages:

> 1\. Request window closure via Hyprland IPC.\
> 2. Wait for applications to exit gracefully.\
> 3. Send SIGTERM to remaining processes.\
> 4. Send SIGKILL if processes still remain.

An overlay is shown immediately. If applications remain open after a
short delay, a detailed interface is displayed.

# CONFIGURATION

hyprhalt reads configuration from:

*\$XDG_CONFIG_HOME/hyprhalt/config.toml*

:   User configuration file (typically
    *\$HOME/.config/hyprhalt/config.toml ).*

<!-- -->

*/etc/xdg/hyprhalt/config.toml*

:   System-wide configuration file.

    User configuration overrides system configuration. If no
    configuration file is present, built-in defaults are used.

    Configuration is written in TOML format and supports the following
    sections:

## \[timing\]

**sigterm_delay**

:   Number of seconds to wait after the initial graceful close request
    before escalating to SIGTERM.

<!-- -->

**sigkill_delay**

:   Number of seconds to wait after SIGTERM before escalating to
    SIGKILL.

## \[colors\]

All color values accept hexadecimal strings (e.g. \"#RRGGBB\") or
comma-separated RGB values.

**backdrop**

:   Backdrop color.

<!-- -->

**backdrop_opacity**

:   Backdrop opacity as a floating-point value between 0 and 1.

<!-- -->

**modal_bg**

:   Modal background color.

<!-- -->

**modal_border**

:   Modal border color.

<!-- -->

**text_primary**

:   Primary text color.

<!-- -->

**text_secondary**

:   Secondary text color.

<!-- -->

**accent_danger**

:   Color used for destructive or force actions.

<!-- -->

**status_alive**

:   Indicator color for running applications.

<!-- -->

**status_closed**

:   Indicator color for closed applications.

## \[ui\]

**border_radius**

:   Border radius of the main window.

<!-- -->

**modal_border_radius**

:   Border radius of modal dialogs.

# FILES

*/usr/bin/hyprhalt*

:   Executable wrapper script. Ensures the Python interpreter loads
    modules from */usr/share/hyprhalt* and invokes the main entry point.

<!-- -->

*/usr/share/hyprhalt*

:   Application source directory containing daemon logic and UI files.

    Directory layout:

        /usr/share/hyprhalt
        ├── daemon
        │   ├── app_tracker.py
        │   ├── config.py
        │   ├── dbus_service.py
        │   ├── hyprland_ipc.py
        │   ├── __init__.py
        │   ├── main.py
        │   └── shutdown_manager.py
        └── ui
            └── shell.qml

    The *daemon* subdirectory contains shutdown logic, IPC handling,
    configuration parsing, and D-Bus integration. The *ui* subdirectory
    contains the Quickshell interface definition.

# REQUIREMENTS

Python 3.11+\
Hyprland\
Quickshell\
dbus-python\
PyGObject

# EXAMPLES

Basic usage:

:   **hyprhalt**

<!-- -->

Dry run:

:   **hyprhalt \--dry-run**

<!-- -->

Shutdown after Hyprland exits:

:   **hyprhalt \--post-cmd systemctl poweroff**

<!-- -->

Switch to VT 2 after exit (commonly required when using SDDM):

:   **hyprhalt \--vt 2**

<!-- -->

Run in foreground with verbose logging:

:   **hyprhalt \--no-fork \--verbose**

# AUTHOR

Barinderpreet Singh \<contact@barinderpreet.com\>

# LICENSE

This software is released into the public domain under the terms of The
Unlicense.

# SEE ALSO

**hyprland**(1)**,** **systemctl**(1)
