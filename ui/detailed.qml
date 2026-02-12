import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Hyprland
import Quickshell.Io
import Quickshell.Wayland

PanelWindow {
    id: root

    property var appsList: []

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

    // Read apps from JSON file periodically
    Process {
        id: readAppsProcess

        command: ["cat", "/tmp/quickshutdown-apps.json"]
        running: true

        stdout: SplitParser {
            splitMarker: ""
            onRead: function(data) {
                try {
                    root.appsList = JSON.parse(data);
                } catch (e) {
                    console.log("Failed to parse apps JSON:", e);
                }
            }
        }

    }

    // Timer to refresh app list
    Timer {
        interval: 500
        running: true
        repeat: true
        onTriggered: {
            readAppsProcess.running = true;
        }
    }

    // D-Bus connection for cancel
    Process {
        id: cancelProcess

        command: ["dbus-send", "--session", "--type=method_call", "--dest=org.hyprland.QuickShutdown", "/org/hyprland/QuickShutdown", "org.hyprland.QuickShutdown.Cancel"]
    }

    Process {
        id: forceKillProcess

        command: ["dbus-send", "--session", "--type=method_call", "--dest=org.hyprland.QuickShutdown", "/org/hyprland/QuickShutdown", "org.hyprland.QuickShutdown.ForceKill"]
    }

    Rectangle {
        anchors.fill: parent
        color: Qt.rgba(12 / 255, 14 / 255, 20 / 255, 0.7)

        Rectangle {
            anchors.centerIn: parent
            radius: 16
            border.width: 0.5
            border.color: "#292e42"
            border.pixelAligned: true
            width: 600
            height: parent.height * 0.4
            color: "#1b1e2d"

            Column {
                anchors.top: parent.top
                anchors.bottom: footer.top
                anchors.right: parent.right
                anchors.left: parent.left
                padding: 24
                topPadding: 20
                spacing: 16

                Text {
                    text: "Closing apps"
                    color: "#c0caf5"
                    font.pixelSize: 20
                    font.family: "Cal Sans"
                }

                Rectangle {
                    width: parent.width - 48
                    height: parent.height - 90
                    radius: 10
                    color: "#24283b"
                    clip: true

                    ScrollView {
                        anchors.fill: parent
                        anchors.topMargin: 8
                        anchors.bottomMargin: 8
                        anchors.rightMargin: 8
                        anchors.leftMargin: 20

                        ListView {
                            id: appList

                            model: root.appsList

                            delegate: Rectangle {
                                required property var modelData

                                width: ListView.view.width
                                height: 40
                                color: "transparent"

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.rightMargin: 20
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

            }

            Rectangle {
                id: footer

                anchors.bottom: parent.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width
                height: 72
                color: "#24283b"
                border.width: 0.5
                border.color: "#292e42"
                border.pixelAligned: true
                bottomLeftRadius: 16
                bottomRightRadius: 16

                Row {
                    spacing: 16

                    anchors {
                        right: parent.right
                        verticalCenter: parent.verticalCenter
                        rightMargin: 24
                    }

                    Rectangle {
                        id: cancelBtn

                        property bool hovered: false

                        width: 90
                        height: 36
                        radius: 10
                        color: hovered ? Qt.rgba(192 / 255, 202 / 255, 245 / 255, 0.1) : Qt.rgba(0.2, 0.2, 0.3, 0)

                        Text {
                            anchors.centerIn: parent
                            text: "Cancel"
                            color: "#c0caf5"
                            font.pixelSize: 14
                            font.family: "Inter"
                        }

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            onEntered: cancelBtn.hovered = true
                            onExited: cancelBtn.hovered = false
                            onClicked: cancelProcess.running = true
                        }

                    }

                    Rectangle {
                        id: forceBtn

                        property bool hovered: false

                        width: 120
                        height: 36
                        radius: 10
                        color: "#f7768e"
                        opacity: hovered ? 0.9 : 1

                        Text {
                            anchors.centerIn: parent
                            text: "Force Close"
                            color: "#24283b"
                            font.pixelSize: 14
                            font.family: "Inter"
                            font.weight: Font.Medium
                        }

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            onEntered: forceBtn.hovered = true
                            onExited: forceBtn.hovered = false
                            onClicked: forceKillProcess.running = true
                        }

                    }

                }

            }

        }

    }

}
