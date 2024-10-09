from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import numpy as np
from pyqtgraph import PlotDataItem


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

class RightClickPopup(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(RightClickPopup, self).__init__(parent)
        self.setStyleSheet("""
            RightClickPopup {
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
                border-radius: 6px;        /* Rounded corners */
                font-size: 16px;           /* Increased font size */
                font-weight: bold;         /* Bold text */
                font-family: 'Arial', 'Helvetica', sans-serif; /* Elegant font */
                padding: 5px;              /* Padding around text */
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

        # Add a "Link" button to the layout
        link_button = QtWidgets.QPushButton("Link")
        link_button.clicked.connect(self.close)  # Optionally close the popup when clicked
        layout.addWidget(link_button)


class Ui_MainWindow(object):

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
        # Button configurations (shifted down by 50 pixels)
        self.Signal1 = self.createButton("Signal", 15, 140, self.signalButtonClicked)   # Left Signal button
        self.Play1 = self.createButton("Play", 110, 290)      # Left Play button
        self.Stop1 = self.createButton("Stop", 240, 290)      # Left Stop button
        self.Move1 = self.createButton("Move", 370, 290)     # Left Move button
        self.ZoomIn1 = self.createButton("+", 500, 290, size=(31, 31))  # Left Zoom In button
        self.ZoomOut1 = self.createButton("-", 560, 290, size=(31, 31)) # Left Zoom Out button
        self.Snapshot1 = self.createButton("SS", 620, 290, size=(31, 31))     # Left SS button

        self.Signal2 = self.createButton("Signal", 15, 470, self.signalButtonClicked)  # Left Signal button for second plot
        self.Play2 = self.createButton("Play", 110, 600)      # Left Play button for second plot
        self.Stop2 = self.createButton("Stop", 240, 600)      # Left Stop button for second plot
        self.Move2 = self.createButton("Move", 370, 600)     # Left Move button for second plot
        self.ZoomIn2 = self.createButton("+", 500, 600, size=(31, 31))  # Left Zoom In button for second plot
        self.ZoomOut2 = self.createButton("-", 560, 600, size=(31, 31)) # Left Zoom Out button
        self.Snapshot2 = self.createButton("SS", 620, 600, size=(31, 31))     # Left SS button for second plot

        # Right side buttons (renamed mirrored buttons)
        self.Signal3 = self.createButton("Signal", 695, 140, self.signalButtonClicked)   # Right Signal button
        self.Play3 = self.createButton("Play", 790, 290)      # Right Play button
        self.Stop3 = self.createButton("Stop", 920, 290)      # Right Stop button
        self.Move3 = self.createButton("Move", 1050, 290)     # Right Move button
        self.ZoomIn3 = self.createButton("+", 1180, 290, size=(31, 31))  # Right Zoom In button
        self.ZoomOut3 = self.createButton("-", 1240, 290, size=(31, 31)) # Right Zoom Out button
        self.Snapshot3 = self.createButton("SS", 1300, 290, size=(31, 31))     # Right SS button

        self.Signal4 = self.createButton("Signal", 695, 470, self.signalButtonClicked)  # Right Signal button for second plot
        self.Play4 = self.createButton("Play", 790, 600)      # Right Play button for second plot
        self.Stop4 = self.createButton("Stop", 920, 600)      # Right Stop button for second plot
        self.Move4 = self.createButton("Move", 1050, 600)     # Right Move button for second plot
        self.ZoomIn4 = self.createButton("+", 1180, 600, size=(31, 31))  # Right Zoom In button for second plot
        self.ZoomOut4 = self.createButton("-", 1240, 600, size=(31, 31)) # Right Zoom Out button
        self.Snapshot4 = self.createButton("SS", 1300, 600, size=(31, 31))     # Right SS button for second plot

        self.line_vertical = QtWidgets.QFrame(self.centralwidget)
        self.line_vertical.setGeometry(QtCore.QRect(680, 0, 2, 1200))  # Vertical line
        self.line_vertical.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_vertical.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_vertical.setStyleSheet("background-color: gray;")

        # Horizontal line
        self.line_horizontal = QtWidgets.QFrame(self.centralwidget)
        self.line_horizontal.setGeometry(QtCore.QRect(0, 360, 1920, 2))  # Adjusted height for the horizontal line
        self.line_horizontal.setFrameShape(QtWidgets.QFrame.HLine)  # Set the shape to horizontal
        self.line_horizontal.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_horizontal.setStyleSheet("background-color: gray;")  # Same style as the vertical line


    def createButton(self, text, x, y, slot=None, size=(100, 30)):
        button = QtWidgets.QPushButton(self.centralwidget)
        button.setGeometry(QtCore.QRect(x, y, *size))
        button.setText(text)
        button.setStyleSheet(self.getButtonStyle())
        if slot:
            button.clicked.connect(slot)
        return button

    def getButtonStyle(self):
        return (
            "QPushButton {\n"
            "    background-color: #474747;      /* Dark gray background */\n"
            "    color: #ffffff;                 /* White text */\n"
            "    border: 1px solid #ffffff;      /* White border */\n"
            "    border-radius: 6px;             /* Rounded corners */\n"
            "    font-size: 18px;                /* Increased font size */\n"  # Increased size
            "    font-weight: bold;              /* Bold text */\n"            # Bold text
            "    font-family: 'Georgia', 'Garamond', 'Times New Roman', serif; /* Elegant font */\n"
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
        # Create two plots using PyQtGraph (shifted 50 pixels down)
        self.Plot1 = pg.PlotWidget(self.centralwidget)
        self.Plot1.setGeometry(QtCore.QRect(120, 70, 541, 201))  # Shifted from 20 to 70
        self.Plot1.setObjectName("Plot1")

        # Increase the y-coordinate for the second plot
        self.Plot2 = pg.PlotWidget(self.centralwidget)
        self.Plot2.setGeometry(QtCore.QRect(120, 390, 541, 201))  # Shifted from 340 to 390
        self.Plot2.setObjectName("Plot2")

        # Mirrored plots
        self.Plot3 = pg.PlotWidget(self.centralwidget)
        self.Plot3.setGeometry(QtCore.QRect(800, 70, 541, 201))  # Right Plot1
        self.Plot3.setObjectName("Plot3")

        self.Plot4 = pg.PlotWidget(self.centralwidget)
        self.Plot4.setGeometry(QtCore.QRect(800, 390, 541, 201))  # Right Plot2
        self.Plot4.setObjectName("Plot4")

        # Example data for plotting
        self.plotData()

    def plotData(self):
        # Generate some example data
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)
        y3 = np.exp(x)
        y4 = np.log10(x + 1e-10)  # Adjust to avoid log(0)

        # Plot the data
        signal1 = pg.PlotDataItem(x, y1, pen='r', name='Sin')  # Red line
        signal2 = pg.PlotDataItem(x, y2, pen='b', name='Cos')  # Blue line

        self.Plot1.addItem(signal1)
        self.Plot2.addItem(signal2)
        self.Plot3.plot(x, y3, pen='g', name='e^x')  # Green line
        self.Plot4.plot(x, y4, pen='y', name='log(x)')  # Yellow line

    def signalButtonClicked(self):
        # Show a message box when any Signal button is pressed
        msg = CustomMessageBox()
        msg.setTitle("Signal")  # Set the title with the desired formatting
        
        # Add buttons to the message box
        buttonSignal = msg.addButton("Choose Signal", QtWidgets.QMessageBox.ActionRole)
        buttonName = msg.addButton("Name", QtWidgets.QMessageBox.ActionRole)
        buttonColor = msg.addButton("Color", QtWidgets.QMessageBox.ActionRole)
        buttonReport = msg.addButton("Report", QtWidgets.QMessageBox.ActionRole)
        msg.exec_()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))