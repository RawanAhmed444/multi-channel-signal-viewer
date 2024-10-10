from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import numpy as np
from pyqtgraph import PlotDataItem
from logic.signal_processing import load_signal_from_file
import pandas as pd
import matplotlib.pyplot as plt
from logic.calculate_stats import calculate_statistics


class CustomMessageBox(QtWidgets.QMessageBox):
    def __init__(self, parent=None):
        super(CustomMessageBox, self).__init__(parent)
        self.setStyleSheet("""
            CustomMessageBox {
                background-color: black;  /* Black background */
                border: 1px solid white;   /* White border */
                border-radius: 10px;      /* Rounded corners */
            }
            QLabel {
                color: white;              /* White text */
            }
            QPushButton {
                background-color: #474747; /* Dark gray background for buttons */
                color: white;              /* White text */
                border: 1px solid white;   /* White border */
                border-radius: 6px;       /* Rounded corners */
                font-size: 16px;          /* Increased font size */
                font-weight: bold;        /* Bold text */
                font-family: 'Arial', 'Helvetica', sans-serif; /* Elegant font */
                padding: 5px;             /* Padding around text */
            }
            QPushButton:hover {
                background-color: #6C6C6C; /* Lighter gray for hover */
            }
        """)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Remove title bar
        self.setContentsMargins(10, 10, 10, 10)  # Set margins to prevent clipping

    def setTitle(self, title):
        label = QtWidgets.QLabel(title)
        label.setStyleSheet("font-size: 24px; font-weight: bold; color: white; text-align: center;")
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout().addWidget(label, 0, 0, 1, 2)  # Add the label to the layout

class StatisticsPopup(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(StatisticsPopup, self).__init__(parent)
        self.setStyleSheet("""
            StatisticsPopup {
                background-color: black;  /* Black background */
                border: 1px solid white;   /* White border */
                border-radius: 10px;      /* Rounded corners */
            }
            QLabel {
                color: white;              /* White text */
            }
            QPushButton {
                background-color: #474747; /* Dark gray background for buttons */
                color: white;              /* White text */
                border: 1px solid white;   /* White border */
                border-radius: 6px;       /* Rounded corners */
                font-size: 16px;          /* Increased font size */
                font-weight: bold;        /* Bold text */
                font-family: 'Arial', 'Helvetica', sans-serif; /* Elegant font */
                padding: 5px;             /* Padding around text */
            }
            QPushButton:hover {
                background-color: #6C6C6C; /* Lighter gray for hover */
            }
        """)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Remove title bar
        self.setContentsMargins(10, 10, 10, 10)  # Set margins to prevent clipping

        # Set the layout
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        # Title label
        titleLabel = QtWidgets.QLabel("Statistics")
        titleLabel.setStyleSheet("font-size: 24px; font-weight: bold; color: white; text-align: center;")
        titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(titleLabel)

        # Statistics content label
        self.statsLabel = QtWidgets.QLabel("Click on a graph to see statistics here.")
        self.statsLabel.setStyleSheet("font-size: 16px; color: white; text-align: center;")
        self.statsLabel.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.statsLabel)

        # Close button
        closeButton = QtWidgets.QPushButton("Close")
        closeButton.clicked.connect(self.close)
        layout.addWidget(closeButton)

    def display_statistics(self, selected_signal_stats):
        selected_signal_stats_text = (
            f"Mean: {selected_signal_stats['mean']:.2f}\n"
            f"Standard Deviation {selected_signal_stats['std']:.2f}\n"
            f"Min: {selected_signal_stats['min']:.2f}\n"
            f"Max: {selected_signal_stats['max']:.2f}\n"
            f"Duration: {selected_signal_stats['duration']:.2f}\n"
        )
        self.statsLabel.setText(selected_signal_stats_text)

class RightClickPopup(QtWidgets.QMenu):
    def __init__(self, parent=None, selected_signal_data=None):
        super(RightClickPopup, self).__init__(parent)
        self.selected_signal_data = selected_signal_data
        self.setStyleSheet("""
            QMenu {
            background-color: #1D1C1C;  /* Dark gray background */
            border: 1px solid #636161;  /* White border */
            border-radius: 4px;        /* Rounded corners */
            }
            QMenu::item {
            color: #ffffff;             /* White text */
            padding: 5px 20px;          /* Padding around text */
            font-size: 16px;            /* Font size */
            font-weight: bold;          /* Bold text */
            font-family: 'Arial', 'Helvetica', sans-serif; /* Elegant font */
            }
            QMenu::item:selected {
            background-color: #403F3F;  /* Lighter gray for hover */
            }
            QMenu::separator {
            height: 1px;                /* Height of the separator */
            background: #636161;        /* Color of the separator */
            }
        """)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Remove title bar

        # Add actions to the menu
        self.addAction("Name", self.close)
        self.addSeparator()
        self.addAction("Color", self.close)
        self.addSeparator()
        self.addAction("Hide", self.close)
        self.addSeparator()
        self.addAction("Move", self.close)
        self.addSeparator()
        self.addAction("Statistics", self.show_statistics)
    
    def show_statistics(self):
        if self.selected_signal_data is not None:
            self.hide()
            selected_signal_stats = calculate_statistics(self.selected_signal_data)
            stats_popup = StatisticsPopup()
            stats_popup.display_statistics(selected_signal_stats)
            stats_popup.exec_()
        
    def showEvent(self, event):
        cursor_pos = QtGui.QCursor.pos()
        self.move(cursor_pos)
        super(RightClickPopup, self).showEvent(event)

class Ui_MainWindow(object):
    def convert_signal_values_to_numeric(self, filename):
        signal_data = load_signal_from_file(filename)
        df = pd.DataFrame(signal_data)

        # Convert the columns to numeric
        df[0] = pd.to_numeric(df[0], errors='coerce')
        df[1] = pd.to_numeric(df[1], errors='coerce')

        # Extract the converted data
        x = df[0].values
        y = df[1].values
        
        return x, y
    
    def __init__(self):
        super().__init__()
        self.plot_index = 0  # Initialize plot_index

        normal_signal = "src\data\signals\ECG_Normal.csv"
        self.x1, self.y1 = self.convert_signal_values_to_numeric(normal_signal)
        
        abnormal_signal = "src\data\signals\ECG_Abnormal.csv"
        self.x2, self.y2 = self.convert_signal_values_to_numeric(abnormal_signal)
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        MainWindow.setStyleSheet("background-color: black;")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Initialize buttons and other UI elements
        self.initButtons()

        # Initialize plots
        self.initPlots()

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 790, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def initButtons(self):

        self.Signal1 = self.createButton("Signal", 15, 70)   # Left Signal button with icon
        self.Link1 = self.createButton("Link To Graph 2", 140, 290, size=(200, 31))   # Left Link button
        self.Speed1 = self.createSpeedButton(430, 290)       # Left Speed button
        self.ZoomIn1 = self.createButtonWithIcon("C:/Users/HP/Task1/Photos/Zoom in.png", 490, 290, )  # Left Zoom In button
        self.ZoomOut1 = self.createButtonWithIcon("C:/Users/HP/Task1/Photos/Zoom out.png", 550, 290, ) # Left Zoom Out button
        self.Snapshot1 = self.createButtonWithIcon("C:/Users/HP/Task1/Photos/Snapshot.png", 610, 290, )     # Left SS button
        self.Play_stop1 = self.createToggleButton("C:/Users/HP/Task1/Photos/Pause.png", "C:/Users/HP/Task1/Photos/Play.png", 370, 290, )    # Left Toggle P/S button
        
        self.Signal2 = self.createButton("Signal", 15, 390)   # Left Signal button with icon
        self.Speed2 = self.createSpeedButton(430, 600)       # Left Speed button for second plot
        self.ZoomIn2 = self.createButtonWithIcon("C:/Users/HP/Task1/Photos/Zoom in.png", 490, 600, )  # Left Zoom In button for second plot
        self.ZoomOut2 = self.createButtonWithIcon("C:/Users/HP/Task1/Photos/Zoom out.png", 550, 600, ) # Left Zoom Out button
        self.Snapshot2 = self.createButtonWithIcon("C:/Users/HP/Task1/Photos/Snapshot.png", 610, 600, )     # Left SS button for second plot
        self.Play_stop2 = self.createToggleButton("C:/Users/HP/Task1/Photos/Pause.png", "C:/Users/HP/Task1/Photos/Play.png", 370, 600, )    # Left Toggle P/S button for second plot
        
        # Right side buttons (renamed mirrored buttons)
        self.Signal3 = self.createButton("Signal", 695, 70)   # Right Signal button
        self.Speed3 = self.createSpeedButton(1120, 290)       # Right Speed button
        self.ZoomIn3 = self.createButtonWithIcon("C:/Users/HP/Task1/Photos/Zoom in.png", 1180, 290, )  # Right Zoom In button
        self.ZoomOut3 = self.createButtonWithIcon("C:/Users/HP/Task1/Photos/Zoom out.png", 1240, 290, ) # Right Zoom Out button
        self.Snapshot3 = self.createButtonWithIcon("C:/Users/HP/Task1/Photos/Snapshot.png", 1300, 290, )     # Right SS button
        self.Play_Stop3 = self.createToggleButton("C:/Users/HP/Task1/Photos/Pause.png", "C:/Users/HP/Task1/Photos/Play.png", 1060, 290, )    # Right Toggle P/S button
        
        self.Signal4 = self.createButton("Signal", 695, 390)  # Right Signal button for second plot
        self.Speed4 = self.createSpeedButton(1120, 600)       # Right Speed button for second plot
        self.ZoomIn4 = self.createButtonWithIcon("C:/Users/HP/Task1/Photos/Zoom in.png", 1180, 600, )  # Right Zoom In button for second plot
        self.ZoomOut4 = self.createButtonWithIcon("C:/Users/HP/Task1/Photos/Zoom out.png", 1240, 600, ) # Right Zoom Out button
        self.Snapshot4 = self.createButtonWithIcon("C:/Users/HP/Task1/Photos/Snapshot.png", 1300, 600, )     # Right SS button for second plot
        self.Play_stop4 = self.createToggleButton("C:/Users/HP/Task1/Photos/Pause.png", "C:/Users/HP/Task1/Photos/Play.png", 1060, 600, )    # Right Toggle P/S button for second plot
    
        self.Report = self.createButton("Report", 605, 645, size=(150, 40), font_size=24)  # Report button
    
    def createButton(self, text, x, y, slot=None, size=(100, 30), font_size=18):
        button = QtWidgets.QPushButton(self.centralwidget)
        button.setGeometry(QtCore.QRect(x, y, *size))
        button.setText(text)
        button.setStyleSheet(self.getButtonStyle(font_size))
        if slot:
            button.clicked.connect(slot)
        return button

    def createButtonWithIcon(self, icon_path, x, y, size=(31, 31)):
        button = QtWidgets.QPushButton(self.centralwidget)
        button.setGeometry(QtCore.QRect(x, y, *size))
        button.setIcon(QtGui.QIcon(icon_path))
        button.setIconSize(QtCore.QSize(size[0] - 10, size[1] - 10))  # Adjust icon size to fit within the button
        button.setStyleSheet(self.getButtonStyle())
        return button
    
    def createSpeedButton(self, x, y, size=(31, 31), default_speed=1):
       button = QtWidgets.QPushButton(f"{default_speed}x", self.centralwidget)
       button.setGeometry(QtCore.QRect(x, y, *size))
       button.setStyleSheet(self.getSpeedButtonStyle())
       button.clicked.connect(lambda: self.toggleSpeed(button))
       button.speeds = [0.25, 0.5, 1, 2, 5, 10, 100]
       button.current_speed_index = button.speeds.index(default_speed)
       return button

    def toggleSpeed(self, button):
       button.current_speed_index = (button.current_speed_index + 1) % len(button.speeds)
       new_speed = button.speeds[button.current_speed_index]
       button.setText(f"{new_speed}x")
       print(f"Speed set to: {new_speed}x")

    def createToggleButton(self, icon1_path, icon2_path, x, y, size=(31, 31)):
        button = QtWidgets.QPushButton(self.centralwidget)
        button.setGeometry(QtCore.QRect(x, y, *size))
        button.setIcon(QtGui.QIcon(icon1_path))
        button.setIconSize(QtCore.QSize(size[0] - 10, size[1] - 10))  # Adjust icon size to fit within the button
        button.setStyleSheet(self.getButtonStyle())
        button.icons = [QtGui.QIcon(icon1_path), QtGui.QIcon(icon2_path)]
        button.current_icon_index = 0
        button.clicked.connect(lambda: self.toggleIcon(button))
        return button

    def toggleIcon(self, button):
        button.current_icon_index = (button.current_icon_index + 1) % len(button.icons)
        new_icon = button.icons[button.current_icon_index]
        button.setIcon(new_icon)
        print(f"Button icon set to: {new_icon.name()}")

    def toggleText(self, button):
        button.current_text_index = (button.current_text_index + 1) % len(button.texts)
        new_text = button.texts[button.current_text_index]
        button.setText(new_text)
        print(f"Button text set to: {new_text}")
    
    def getButtonStyle(self, font_size=18):
        return (
            "QPushButton {\n"
            "    background-color: #353535;      /* Dark gray background */\n"
            "    color: #ffffff;                 /* White text */\n"
            "    border: 1px solid #959494;      /* White border */\n"
            "    border-radius: 6px;             /* Rounded corners */\n"
            f"    font-size: {font_size}px;       /* Font size */\n"  # Dynamic font size
            "    font-weight: bold;              /* Bold text */\n"            
            "    font-family: 'Georgia', 'Garamond', 'Times New Roman', serif; /* Elegant font */\n"
            "    transition: all 0.3s ease;      /* Smooth transition for hover effect */\n"
            "}\n"
            "\n"
            "QPushButton:hover {\n"
            "    background-color: #4A4A4A;      /* Slightly darker gray for hover */\n"
            "    color: #ffffff;                 /* Keep white text */\n"
            "    border-color: #9A9999;          /* Keep white border */\n"
            "}\n"
            "\n"
            "QPushButton:pressed {\n"
            "    background-color: #1C1C1C;      /* Even darker gray for pressed state */\n"
            "    color: #ffffff;                 /* White text when pressed */\n"
            "}\n"
        )
    def getSpeedButtonStyle(self):
        return (
            "QPushButton {\n"
            "    background-color: #353535;      /* Dark gray background */\n"
            "    color: #ffffff;                 /* White text */\n"
            "    border: 1px solid #959494;      /* White border */\n"
            "    border-radius: 6px;             /* Rounded corners */\n"
            "    font-size: 10px;                /* Increased font size */\n"  # Increased size
            "    font-weight: bold;              /* Bold text */\n"            # Bold text
            "    font-family: 'Georgia', 'Garamond', 'Times New Roman', serif; /* Elegant font */\n"
            "    transition: all 0.3s ease;      /* Smooth transition for hover effect */\n"
            "}\n"
            "\n"
            "QPushButton:hover {\n"
            "    background-color: #4A4A4A;      /* Slightly darker gray for hover */\n"
            "    color: #ffffff;                 /* Keep white text */\n"
            "    border-color: #9A9999;          /* Keep white border */\n"
            "}\n"
            "\n"
            "QPushButton:pressed {\n"
            "    background-color: #1C1C1C;      /* Even darker gray for pressed state */\n"
            "    color: #ffffff;                 /* White text when pressed */\n"
            "}\n"
        )
    
    # def plotRightClicked(self, event):
    #   if event.button() == QtCore.Qt.RightButton:
    #     # Display the right-click popup
    #     right_click_popup = RightClickPopup()
    #     right_click_popup.exec_()

    def initPlots(self):
        # Create two plots using PyQtGraph (shifted 50 pixels down)
        self.Plot1 = pg.PlotWidget(self.centralwidget)
        self.Plot1.setGeometry(QtCore.QRect(120, 70, 541, 201))  # Shifted from 20 to 70
        self.Plot1.setObjectName("Plot1")
        # self.Plot1.scene().sigMouseClicked.connect(self.plotRightClicked)  # Connect mouse click to the plot

        signal1_time_length = len(self.x1)
        signal1_value_length = len(self.y1)
        
        signal2_time_length = len(self.x2)
        signal2_value_length = len(self.y2)
        
        #Set x and y limits (adjust as needed)
        self.Plot1.setXRange(0, signal1_time_length)  # Set x-axis limits from 0 to 10
        self.Plot1.setYRange(0, signal1_value_length)  # Set y-axis limits from 0 to 100

        # Set axis labels
        self.Plot1.setLabel('bottom', "Time (s)")
        self.Plot1.setLabel('left', "Normal Signal")

        # Increase the y-coordinate for the second plot
        self.Plot2 = pg.PlotWidget(self.centralwidget)
        self.Plot2.setGeometry(QtCore.QRect(120, 390, 541, 201))  # Shifted from 340 to 390
        self.Plot2.setObjectName("Plot2")
        # self.Plot2.scene().sigMouseClicked.connect(self.plotRightClicked)  # Connect mouse click to the plot

        # Set x and y limits (adjust as needed)
        self.Plot2.setXRange(0, signal2_time_length)  # Set x-axis limits from 0 to 10
        self.Plot2.setYRange(0, signal2_value_length)  # Set y-axis limits from 0 to 100

        # Set axis labels
        self.Plot2.setLabel('bottom', "Time (s)")
        self.Plot2.setLabel('left', "Abnormal Signal")

        # Mirrored plots
        self.Plot3 = pg.PlotWidget(self.centralwidget)
        self.Plot3.setGeometry(QtCore.QRect(800, 70, 541, 201))  # Right Plot1
        self.Plot3.setObjectName("Plot3")
        # self.Plot3.scene().sigMouseClicked.connect(self.plotRightClicked)  # Connect mouse click to the plot

        self.Plot4 = pg.PlotWidget(self.centralwidget)
        self.Plot4.setGeometry(QtCore.QRect(800, 390, 541, 201))  # Right Plot2
        self.Plot4.setObjectName("Plot4")
        # self.Plot4.scene().sigMouseClicked.connect(self.plotRightClicked)  # Connect mouse click to the plot

        # Example data for plotting
        self.plotData()

    def plotData(self):
        self.Plot1.enableAutoRange()  # Enable automatic scaling of axes
        self.Plot1.showGrid(x=True, y=True)  # Show grid lines
        
        self.Plot2.enableAutoRange()  # Enable automatic scaling of axes
        self.Plot2.showGrid(x=True, y=True)  # Show grid lines

        # Create a timer to update the plot dynamically
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)  # Adjust the interval as needed
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        if self.plot_index < len(self.x1):
            next_x = self.x1[self.plot_index]
            next_y = self.y1[self.plot_index]
            self.plot_index += 1

            self.Plot1.plot(self.x1[:self.plot_index], self.y1[:self.plot_index])  # Update the plot data
            plt.pause(0.01)  # Adjust the pause time for animation speed
            
        if self.plot_index < len(self.x2):
            next_x = self.x2[self.plot_index]
            next_y = self.y2[self.plot_index]
            self.plot_index += 1
              
            self.Plot2.plot(self.x2[:self.plot_index], self.y2[:self.plot_index])  # Update the plot data
            plt.pause(0.01)  # Adjust the pause time for animation speed

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))