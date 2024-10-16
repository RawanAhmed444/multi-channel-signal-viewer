# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Task.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from signal_processing import load_signal_from_file
import pandas as pd
import matplotlib.pyplot as plt

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
        MainWindow.resize(790, 600)
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
        # Button configurations
        self.Signal1 = self.createButton("Signal", 50, 90)
        self.Play1 = self.createButton("Play", 180, 240)
        self.Stop1 = self.createButton("Stop", 310, 240)
        self.ZoomIn1 = self.createButton("+", 540, 240, size=(31, 31))
        self.ZoomOut1 = self.createButton("-", 600, 240, size=(31, 31))
        self.SS1 = self.createButton("SS", 660, 240, size=(31, 31))

        self.Play1_2 = self.createButton("Play", 180, 510)
        self.Stop2 = self.createButton("Stop", 310, 510)
        self.ZoomIn2 = self.createButton("+", 540, 510, size=(31, 31))
        self.ZoomOut2 = self.createButton("-", 600, 510, size=(31, 31))
        self.SS2 = self.createButton("SS", 660, 510, size=(31, 31))

        self.Signal2 = self.createButton("Signal", 50, 380)

        # Horizontal line
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(0, 270, 941, 31))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

    def createButton(self, text, x, y, size=(101, 31)):
        button = QtWidgets.QPushButton(self.centralwidget)
        button.setGeometry(QtCore.QRect(x, y, *size))
        button.setStyleSheet(self.getButtonStyle())
        button.setText(text)
        return button

    def getButtonStyle(self):
        return (
            "QPushButton {\n"
            "    background-color: #474747;      /* Dark gray background */\n"
            "    color: #ffffff;                 /* White text */\n"
            "    border: 1px solid #ffffff;      /* White border */\n"
            "    border-radius: 6px;             /* Rounded corners */\n"
            "    font-size: 14px;                /* Font size */\n"
            "    transition: all 0.3s ease;      /* Smooth transition for hover effect */\n"
            "}\n"
            "\n"
            "QPushButton:hover {\n"
            "    background-color: #6C6C6C;      /* Lighter gray for hover */\n"
            "    color: #ffffff;                 /* Keep white text */\n"
            "    border-color: #ffffff;          /* Keep white border */\n"
            "}\n"
            "\n"
            "QPushButton:pressed {\n"
            "    background-color: #1C1C1C;      /* Even darker gray for pressed state */\n"
            "    color: #ffffff;                 /* White text when pressed */\n"
            "}\n"
        )
        
    def initPlots(self):
        # Create two plots using PyQtGraph
        self.Plot1 = pg.PlotWidget(self.centralwidget)
        self.Plot1.setGeometry(QtCore.QRect(180, 20, 541, 201))
        self.Plot1.setObjectName("Plot1")
        
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
        
        
        self.Plot2 = pg.PlotWidget(self.centralwidget)
        self.Plot2.setGeometry(QtCore.QRect(180, 300, 541, 201))
        self.Plot2.setObjectName("Plot2")
        
        # Set x and y limits (adjust as needed)
        self.Plot2.setXRange(0, signal2_time_length)  # Set x-axis limits from 0 to 10
        self.Plot2.setYRange(0, signal2_value_length)  # Set y-axis limits from 0 to 100

        # Set axis labels
        self.Plot2.setLabel('bottom', "Time (s)")
        self.Plot2.setLabel('left', "Abnormal Signal")

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


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

            
            
            