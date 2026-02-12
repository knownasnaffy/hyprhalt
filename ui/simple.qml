import QtQuick
import Quickshell
import Quickshell.Hyprland
import Quickshell.Wayland
import Quickshell.Io

PanelWindow {
    id: root
    aboveWindows: true
    focusable: false
    exclusionMode: ExclusionMode.Ignore
    WlrLayershell.namespace: "hyprland-quit-simple"
    color: "transparent"

    anchors {
        top: true
        bottom: true
        left: true
        right: true
    }

    property var config: ({})

    Process {
        id: readConfigProcess
        command: ["cat", "/tmp/quickshutdown-config.json"]
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

    Rectangle {
        anchors.fill: parent
        color: {
            var rgb = (root.config.colors?.backdrop || "12,14,20").split(",");
            var opacity = root.config.colors?.backdrop_opacity || 0.7;
            return Qt.rgba(rgb[0]/255, rgb[1]/255, rgb[2]/255, opacity);
        }

        Text {
            id: clock

            property int dots: 1
            property int maxDots: 3

            text: "Exiting" + ".".repeat(dots)
            color: {
                var rgb = (root.config.colors?.text_secondary || "169,177,214").split(",");
                return Qt.rgba(rgb[0]/255, rgb[1]/255, rgb[2]/255, 1);
            }
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
