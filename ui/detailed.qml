import Quickshell
import Quickshell.Wayland
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

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
            WlrLayershell.namespace: "quickshutdown-detailed"
            
            Rectangle {
                anchors.centerIn: parent
                width: 500
                height: 400
                color: "#dd000000"
                radius: 15
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 15
                    
                    Text {
                        text: "Shutting down..."
                        color: "white"
                        font.pixelSize: 28
                        font.bold: true
                        Layout.alignment: Qt.AlignHCenter
                    }
                    
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: "#33ffffff"
                        radius: 8
                        
                        ScrollView {
                            anchors.fill: parent
                            anchors.margins: 10
                            
                            ListView {
                                id: appList
                                model: ListModel {
                                    // Will be populated via D-Bus
                                    ListElement { appName: "Example App"; appStatus: "closing" }
                                }
                                
                                delegate: Rectangle {
                                    width: ListView.view.width
                                    height: 40
                                    color: "transparent"
                                    
                                    RowLayout {
                                        anchors.fill: parent
                                        spacing: 10
                                        
                                        Text {
                                            text: appName
                                            color: "white"
                                            font.pixelSize: 16
                                            Layout.fillWidth: true
                                        }
                                        
                                        Text {
                                            text: appStatus
                                            color: appStatus === "alive" ? "#ffaa00" : "#00ff00"
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
                            font.pixelSize: 16
                            Layout.preferredWidth: 120
                            Layout.preferredHeight: 40
                            
                            onClicked: {
                                // TODO: D-Bus call to cancel
                                Qt.quit()
                            }
                        }
                        
                        Button {
                            text: "Force Kill"
                            font.pixelSize: 16
                            Layout.preferredWidth: 120
                            Layout.preferredHeight: 40
                            
                            onClicked: {
                                // TODO: D-Bus call to force kill
                                Qt.quit()
                            }
                        }
                    }
                }
            }
        }
    }
}
