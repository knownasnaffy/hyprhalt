import QtQuick
import Quickshell
import Quickshell.Hyprland
import Quickshell.Wayland

PanelWindow {
    aboveWindows: true
    focusable: false
    exclusionMode: ExclusionMode.Ignore
    WlrLayershell.namespace: "hyprland-quit-notice"
    color: "transparent"

    anchors {
        top: true
        bottom: true
        left: true
        right: true
    }

    Rectangle {
        anchors.fill: parent
        color: Qt.rgba(22 / 225, 22 / 225, 30 / 225, 0.7)

        Text {
            id: clock

            property int dots: 1
            property int maxDots: 3

            text: "Exiting" + ".".repeat(dots)
            color: "#a9b1d6"
            font.family: "Inter"
            font.pixelSize: 36
            font.weight: Font.Medium
            anchors.centerIn: parent

            Timer {
                interval: 1000
                running: true
                repeat: true
                onTriggered: {
                    clock.dots = clock.dots % clock.maxDots + 1;
                }
            }

        }

    }

}
