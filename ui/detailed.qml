import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Hyprland
import Quickshell.Wayland
import Quickshell.Io

PanelWindow {
    id: root
    aboveWindows: true
    focusable: true
    exclusionMode: ExclusionMode.Ignore
    WlrLayershell.namespace: "hyprland-quit-detailed"
    color: "transparent"

    anchors {
        top: true
        bottom: true
        left: true
        right: true
    }

    property string appsFilePath: ""
    
    // Get apps file path from D-Bus
    Process {
        id: getAppsFileProcess
        command: ["dbus-send", "--session", "--print-reply",
                  "--dest=org.hyprland.QuickShutdown",
                  "/org/hyprland/QuickShutdown",
                  "org.hyprland.QuickShutdown.GetAppsFile"]
        running: true
        
        stdout: SplitParser {
            splitMarker: "\n"
            
            onRead: data => {
                var match = data.match(/string "([^"]+)"/);
                if (match && match[1]) {
                    root.appsFilePath = match[1];
                }
            }
        }
    }
    
    // Read apps from JSON file
    FileView {
        id: appsFile
        path: root.appsFilePath
        adapter: JsonAdapter {}
    }
    
    // Timer to refresh file view
    Timer {
        interval: 500
        running: root.appsFilePath !== ""
        repeat: true
        onTriggered: {
            appsFile.reload()
        }
    }

    // D-Bus connection for cancel
    Process {
        id: cancelProcess
        command: ["dbus-send", "--session", "--type=method_call",
                  "--dest=org.hyprland.QuickShutdown",
                  "/org/hyprland/QuickShutdown",
                  "org.hyprland.QuickShutdown.Cancel"]
    }

    Process {
        id: forceKillProcess
        command: ["dbus-send", "--session", "--type=method_call",
                  "--dest=org.hyprland.QuickShutdown",
                  "/org/hyprland/QuickShutdown",
                  "org.hyprland.QuickShutdown.ForceKill"]
    }

    Rectangle {
        anchors.fill: parent
        color: Qt.rgba(22 / 225, 22 / 225, 30 / 225, 0.8)

        Rectangle {
            anchors.centerIn: parent
            width: 500
            height: 400
            color: Qt.rgba(30 / 225, 30 / 225, 46 / 225, 0.95)
            radius: 15

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 15

                Text {
                    text: "Shutting down..."
                    color: "#a9b1d6"
                    font.family: "Inter"
                    font.pixelSize: 28
                    font.weight: Font.Medium
                    Layout.alignment: Qt.AlignHCenter
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: Qt.rgba(255, 255, 255, 0.05)
                    radius: 8

                    ScrollView {
                        anchors.fill: parent
                        anchors.margins: 10

                        ListView {
                            id: appList
                            model: appsFile.data
                            
                            delegate: Rectangle {
                                required property var modelData
                                width: ListView.view.width
                                height: 40
                                color: "transparent"

                                RowLayout {
                                    anchors.fill: parent
                                    spacing: 10

                                    Text {
                                        text: modelData.appName || "Unknown"
                                        color: "#c0caf5"
                                        font.family: "Inter"
                                        font.pixelSize: 16
                                        Layout.fillWidth: true
                                    }

                                    Text {
                                        text: modelData.appStatus || "unknown"
                                        color: modelData.appStatus === "alive" ? "#e0af68" : "#9ece6a"
                                        font.family: "Inter"
                                        font.pixelSize: 14
                                    }
                                }
                            }
                        }
                    }
                }

                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    spacing: 15

                    Button {
                        text: "Cancel"
                        font.family: "Inter"
                        font.pixelSize: 16
                        Layout.preferredWidth: 120
                        Layout.preferredHeight: 40

                        onClicked: {
                            cancelProcess.running = true
                        }
                    }

                    Button {
                        text: "Force Kill"
                        font.family: "Inter"
                        font.pixelSize: 16
                        Layout.preferredWidth: 120
                        Layout.preferredHeight: 40

                        onClicked: {
                            forceKillProcess.running = true
                        }
                    }
                }
            }
        }
    }
}
