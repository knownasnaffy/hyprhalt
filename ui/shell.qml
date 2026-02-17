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
    property var config: ({})
    property bool showModal: false

    aboveWindows: true
    focusable: true
    exclusionMode: ExclusionMode.Ignore
    WlrLayershell.namespace: "hyprhalt"
    color: "transparent"

    anchors {
        top: true
        bottom: true
        left: true
        right: true
    }

    // Read config from JSON file
    Process {
        id: readConfigProcess
        command: ["cat", "/tmp/hyprhalt-config.json"]
        running: true

        stdout: SplitParser {
            splitMarker: ""

            onRead: function(data) {
                try {
                    root.config = JSON.parse(data);
                } catch (e) {}
            }
        }
    }

    // Read apps from JSON file periodically
    Process {
        id: readAppsProcess

        command: ["cat", "/tmp/hyprhalt-apps.json"]
        running: true

        stdout: SplitParser {
            splitMarker: ""
            onRead: function(data) {
                try {
                    root.appsList = JSON.parse(data);
                } catch (e) {}
            }
        }
    }

    // Timer to refresh app list
    Timer {
        interval: 500
        running: root.showModal
        repeat: true
        onTriggered: {
            readAppsProcess.running = true;
        }
    }

    // Timer to show modal after 3 seconds
    Timer {
        interval: 3000
        running: true
        repeat: false
        onTriggered: {
            console.log("!!! 3 SECOND TIMER TRIGGERED, SHOWING MODAL !!!");
            root.showModal = true;
        }
    }

    // D-Bus connection for cancel
    Process {
        id: cancelProcess
        command: ["dbus-send", "--session", "--type=method_call", "--dest=org.hyprland.HyprHalt", "/org/hyprland/HyprHalt", "org.hyprland.HyprHalt.Cancel"]

        stdout: SplitParser {
            onRead: function(data) {
                console.log("Cancel D-Bus response:", data);
            }
        }

        onExited: function(exitCode) {
            console.log("Cancel D-Bus exited with code:", exitCode);
        }
    }

    Process {
        id: forceKillProcess
        command: ["dbus-send", "--session", "--type=method_call", "--dest=org.hyprland.HyprHalt", "/org/hyprland/HyprHalt", "org.hyprland.HyprHalt.ForceKill"]

        stdout: SplitParser {
            onRead: function(data) {
                console.log("ForceKill D-Bus response:", data);
            }
        }

        onExited: function(exitCode) {
            console.log("ForceKill D-Bus exited with code:", exitCode);
        }
    }

    // Backdrop
    Rectangle {
        anchors.fill: parent
        color: {
            var rgb = (root.config.colors?.backdrop || "12,14,20").split(",");
            var opacity = root.config.colors?.backdrop_opacity || 0.7;
            return Qt.rgba(rgb[0]/255, rgb[1]/255, rgb[2]/255, opacity);
        }

        // "Exiting..." text
        Text {
            id: exitingText

            property int dots: 1
            property int maxDots: 3

            text: (root.config.text?.exiting || "Exiting") + ".".repeat(dots)
            color: {
                var rgb = (root.config.colors?.text_secondary || "169,177,214").split(",");
                return Qt.rgba(rgb[0]/255, rgb[1]/255, rgb[2]/255, 1);
            }
            font.family: "Inter"
            font.pixelSize: 36
            font.weight: Font.Medium
            anchors.centerIn: parent
            opacity: root.showModal ? 0 : 1

            Behavior on opacity {
                NumberAnimation { duration: 300 }
            }

            Timer {
                interval: 1000
                running: !root.showModal
                repeat: true
                onTriggered: {
                    exitingText.dots = exitingText.dots % exitingText.maxDots + 1;
                }
            }
        }

        // Modal overlay
        Rectangle {
            id: modal
            anchors.centerIn: parent
            radius: root.config.ui?.border_radius !== undefined ? root.config.ui.border_radius : 16
            border.width: 0.5
            border.color: {
                var rgb = (root.config.colors?.modal_border || "41,46,66").split(",");
                return Qt.rgba(rgb[0]/255, rgb[1]/255, rgb[2]/255, 1);
            }
            border.pixelAligned: true
            width: 600
            height: parent.height * 0.4
            color: {
                var rgb = (root.config.colors?.modal_bg || "27,30,45").split(",");
                return Qt.rgba(rgb[0]/255, rgb[1]/255, rgb[2]/255, 1);
            }
            opacity: root.showModal ? 1 : 0
            scale: root.showModal ? 1 : 0.95

            Behavior on opacity {
                NumberAnimation { duration: 300; easing.type: Easing.OutCubic }
            }

            Behavior on scale {
                NumberAnimation { duration: 300; easing.type: Easing.OutCubic }
            }

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
                    color: {
                        var rgb = (root.config.colors?.text_primary || "192,202,245").split(",");
                        return Qt.rgba(rgb[0]/255, rgb[1]/255, rgb[2]/255, 1);
                    }
                    font.pixelSize: 20
                    font.family: "Cal Sans"
                }

                Rectangle {
                    width: parent.width - 48
                    height: parent.height - 90
                    radius: root.config.ui?.modal_border_radius !== undefined ? root.config.ui.modal_border_radius : 10
                    color: {
                        var rgb = (root.config.colors?.modal_bg || "27,30,45").split(",");
                        var r = Math.max(0, rgb[0] - 10);
                        var g = Math.max(0, rgb[1] - 10);
                        var b = Math.max(0, rgb[2] - 10);
                        return Qt.rgba(r/255, g/255, b/255, 1);
                    }
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
                                        color: {
                                            var rgb = (root.config.colors?.text_primary || "192,202,245").split(",");
                                            return Qt.rgba(rgb[0]/255, rgb[1]/255, rgb[2]/255, 1);
                                        }
                                        font.family: "Inter"
                                        font.pixelSize: 16
                                        Layout.fillWidth: true
                                    }

                                    Text {
                                        text: modelData.appStatus || "unknown"
                                        color: {
                                            var rgb = modelData.appStatus === "alive"
                                                ? (root.config.colors?.status_alive || "224,175,104").split(",")
                                                : (root.config.colors?.status_closed || "158,206,106").split(",");
                                            return Qt.rgba(rgb[0]/255, rgb[1]/255, rgb[2]/255, 1);
                                        }
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
                color: {
                    var rgb = (root.config.colors?.modal_bg || "27,30,45").split(",");
                    var r = Math.max(0, rgb[0] - 10);
                    var g = Math.max(0, rgb[1] - 10);
                    var b = Math.max(0, rgb[2] - 10);
                    return Qt.rgba(r/255, g/255, b/255, 1);
                }
                border.width: 0.5
                border.color: {
                    var rgb = (root.config.colors?.modal_border || "41,46,66").split(",");
                    return Qt.rgba(rgb[0]/255, rgb[1]/255, rgb[2]/255, 1);
                }
                border.pixelAligned: true
                bottomLeftRadius: root.config.ui?.border_radius !== undefined ? root.config.ui.border_radius : 16
                bottomRightRadius: root.config.ui?.border_radius !== undefined ? root.config.ui.border_radius : 16

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
                        radius: root.config.ui?.modal_border_radius !== undefined ? root.config.ui.modal_border_radius : 10
                        color: {
                            if (hovered) {
                                var rgb = (root.config.colors?.text_primary || "192,202,245").split(",");
                                return Qt.rgba(rgb[0]/255, rgb[1]/255, rgb[2]/255, 0.1);
                            }
                            return Qt.rgba(0.2, 0.2, 0.3, 0);
                        }

                        Text {
                            anchors.centerIn: parent
                            text: "Cancel"
                            color: {
                                var rgb = (root.config.colors?.text_primary || "192,202,245").split(",");
                                return Qt.rgba(rgb[0]/255, rgb[1]/255, rgb[2]/255, 1);
                            }
                            font.pixelSize: 14
                            font.family: "Inter"
                        }

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            onEntered: cancelBtn.hovered = true
                            onExited: cancelBtn.hovered = false
                            onClicked: {
                                console.log("!!! CANCEL BUTTON CLICKED - EXITING WITH CODE 2 !!!");
                                Qt.exit(2);
                            }
                            cursorShape: Qt.PointingHandCursor
                        }
                    }

                    Rectangle {
                        id: forceBtn

                        property bool hovered: false

                        width: 120
                        height: 36
                        radius: root.config.ui?.modal_border_radius !== undefined ? root.config.ui.modal_border_radius : 10
                        color: {
                            var rgb = (root.config.colors?.accent_danger || "247,118,142").split(",");
                            return Qt.rgba(rgb[0]/255, rgb[1]/255, rgb[2]/255, 1);
                        }
                        opacity: hovered ? 0.9 : 1

                        Text {
                            anchors.centerIn: parent
                            text: "Force Close"
                            color: {
                                var rgb = (root.config.colors?.modal_bg || "27,30,45").split(",");
                                return Qt.rgba(rgb[0]/255, rgb[1]/255, rgb[2]/255, 1);
                            }
                            font.pixelSize: 14
                            font.family: "Inter"
                            font.weight: Font.Medium
                        }

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            onEntered: forceBtn.hovered = true
                            onExited: forceBtn.hovered = false
                            onClicked: {
                                console.log("!!! FORCE KILL BUTTON CLICKED - EXITING WITH CODE 3 !!!");
                                Qt.exit(3);
                            }
                            cursorShape: Qt.PointingHandCursor
                        }
                    }
                }
            }
        }
    }
}
