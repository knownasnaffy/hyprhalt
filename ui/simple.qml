import Quickshell
import Quickshell.Wayland
import QtQuick

ShellRoot {
    Variants {
        model: Quickshell.Wayland.WaylandScreen.screens
        
        PanelWindow {
            property var modelData
            screen: modelData
            
            anchors {
                left: true
                top: true
                right: true
                bottom: true
            }
            
            color: "transparent"
            WlrLayershell.layer: WlrLayer.Overlay
            WlrLayershell.namespace: "quickshutdown-simple"
            
            Rectangle {
                anchors.centerIn: parent
                width: 300
                height: 100
                color: "#cc000000"
                radius: 10
                
                Text {
                    anchors.centerIn: parent
                    text: "Exiting..."
                    color: "white"
                    font.pixelSize: 32
                    font.bold: true
                }
            }
        }
    }
}
