import Quickshell
import Quickshell.Wayland

ShellRoot {
    Variants {
        model: Quickshell.Wayland.WaylandScreen.screens
        
        PanelWindow {
            property var modelData
            screen: modelData
            
            anchors {
                fill: true
            }
            
            color: "transparent"
            
            layer: WlrLayer.Overlay
            namespace: "quickshutdown-simple"
            exclusionMode: ExclusionMode.Normal
            
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
