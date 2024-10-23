from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import numpy as np
from logic.signal_processing import load_signal_from_file
import pandas as pd
import matplotlib.pyplot as plt

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
        # link_button = QtWidgets.QPushButton("Link")
        # link_button.clicked.connect(self.close)  # Optionally close the popup when clicked
        # layout.addWidget(link_button)


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

        # Button configurations (shifted down by 50 pixels)
        self.Signal1 = self.createButton("Signal", 15, 140, self.signalButtonClicked)   # Left Signal button
        self.Play1 = self.createButton("Play", 110, 290)      # Left Play button
        self.Stop1 = self.createButton("Stop", 240, 290)      # Left Stop button
        self.Move1 = self.createButton("Move", 370, 290)     # Left Move button
        self.ZoomIn1 = self.createButton("+", 500, 290, size=(31, 31))  # Left Zoom In button
        self.ZoomOut1 = self.createButton("-", 560, 290, size=(31, 31)) # Left Zoom Out button
        self.SS1 = self.createButton("SS", 620, 290, size=(31, 31))     # Left SS button
        self.link_button= self.createButton("Link", 1, 1)
        self.ZoomIn1.clicked.connect(self.zoom_in_1)
        self.ZoomOut1.clicked.connect(self.zoom_out_1)
        self.link_button.clicked.connect(self.link_plots)


        self.Signal2 = self.createButton("Signal", 15, 470, self.signalButtonClicked)  # Left Signal button for second plot
        self.Play2 = self.createButton("Play", 110, 600)      # Left Play button for second plot
        self.Stop2 = self.createButton("Stop", 240, 600)      # Left Stop button for second plot
        self.Move2 = self.createButton("Move", 370, 600)     # Left Move button for second plot
        self.ZoomIn2 = self.createButton("+", 500, 600, size=(31, 31))  # Left Zoom In button for second plot
        self.ZoomOut2 = self.createButton("-", 560, 600, size=(31, 31)) # Left Zoom Out button
        self.SS2 = self.createButton("SS", 620, 600, size=(31, 31))     # Left SS button for second plot
        self.ZoomIn2.clicked.connect(self.zoom_in_2)
        self.ZoomOut2.clicked.connect(self.zoom_out_2)

        # Right side buttons (renamed mirrored buttons)
        self.Signal3 = self.createButton("Signal", 695, 140, self.signalButtonClicked)   # Right Signal button
        self.Play3 = self.createButton("Play", 790, 290)      # Right Play button
        self.Stop3 = self.createButton("Stop", 920, 290)      # Right Stop button
        self.Move3 = self.createButton("Move", 1050, 290)     # Right Move button
        self.ZoomIn3 = self.createButton("+", 1180, 290, size=(31, 31))  # Right Zoom In button
        self.ZoomOut3 = self.createButton("-", 1240, 290, size=(31, 31)) # Right Zoom Out button
        self.SS3 = self.createButton("SS", 1300, 290, size=(31, 31))     # Right SS button
        self.ZoomIn3.clicked.connect(self.zoom_in_3)
        self.ZoomOut3.clicked.connect(self.zoom_out_3)

        self.Signal4 = self.createButton("Signal", 695, 470, self.signalButtonClicked)  # Right Signal button for second plot
        self.Play4 = self.createButton("Play", 790, 600)      # Right Play button for second plot
        self.Stop4 = self.createButton("Stop", 920, 600)      # Right Stop button for second plot
        self.Move4 = self.createButton("Move", 1050, 600)     # Right Move button for second plot
        self.ZoomIn4 = self.createButton("+", 1180, 600, size=(31, 31))  # Right Zoom In button for second plot
        self.ZoomOut4 = self.createButton("-", 1240, 600, size=(31, 31)) # Right Zoom Out button
        self.SS4 = self.createButton("SS", 1300, 600, size=(31, 31))     # Right SS button for second plot
        self.ZoomIn4.clicked.connect(self.zoom_in_4)
        self.ZoomOut4.clicked.connect(self.zoom_out_4)

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

    def link_plots(self):
        global is_linked
        is_linked = False
        if is_linked:
            # Unlink the plots
            self.Plot2.setXLink(None)
            self.Plot2.setYLink(None)
            self.link_button.setText("Link Plots")  # Change button text to "Link Plots"
            is_linked = False  # Update the state
        else:
            # Link the plots and set the same zoom
            self.Plot2.setXLink(self.Plot1)
            self.Plot2.setYLink(self.Plot1)  # Uncomment if you want to link y-axis as well

            # Synchronize zoom levels
            self.Plot2.getViewBox().setRange(xRange=self.Plot1.getViewBox().viewRange()[0],
                                        yRange=self.Plot1.getViewBox().viewRange()[1],
                                        padding=0)
            self.link_button.setText("Unlink Plots")  # Change button text to "Unlink Plots"
            is_linked = True  # Update the state

    def zoom_in_1(self):
        vb = self.Plot1.getViewBox()
        vb.scaleBy((0.8, 0.8))

    def zoom_out_1(self):
        vb = self.Plot1.getViewBox()
        vb.scaleBy((1.2, 1.2))
    def zoom_in_2(self):
        vb = self.Plot2.getViewBox()
        vb.scaleBy((0.8, 0.8))

    def zoom_out_2(self):
        vb = self.Plot2.getViewBox()
        vb.scaleBy((1.2, 1.2))

    def zoom_in_3(self):
        vb = self.Plot3.getViewBox()
        vb.scaleBy((0.8, 0.8))

    def zoom_out_3(self):
        vb = self.Plot3.getViewBox()
        vb.scaleBy((1.2, 1.2))

    def zoom_in_4(self):
        vb = self.Plot4.getViewBox()
        vb.scaleBy((0.8, 0.8))

    def zoom_out_4(self):
        vb = self.Plot4.getViewBox()
        vb.scaleBy((1.2, 1.2))

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
    def plotClicked(self, event):
    # Check if the left mouse button was clicked
      if event.button() == QtCore.Qt.LeftButton:
        # Display the statistics popup
        stats_popup = StatisticsPopup()
        stats_popup.statsLabel.setText("Mean =") 
        stats_popup.exec_()      
      elif event.button() == QtCore.Qt.RightButton:
        # Display the right-click popup
        right_click_popup = RightClickPopup()
        right_click_popup.exec_()
    
    def initPlots(self):
        # Create two plots using PyQtGraph
        self.Plot1 = pg.PlotWidget(self.centralwidget)
        self.Plot1.setGeometry(QtCore.QRect(120, 70, 541, 201))  # Shifted from 20 to 70
        self.Plot1.setObjectName("Plot1")
        self.Plot1.scene().sigMouseClicked.connect(self.plotClicked)  # Connect mouse click to the plot

        
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
        self.Plot2.setGeometry(QtCore.QRect(120, 390, 541, 201))  # Shifted from 340 to 390
        self.Plot2.setObjectName("Plot2")
        self.Plot2.scene().sigMouseClicked.connect(self.plotClicked)  # Connect mouse click to the plot
        
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
        self.Plot3.scene().sigMouseClicked.connect(self.plotClicked)  # Connect mouse click to the plot

        self.Plot4 = pg.PlotWidget(self.centralwidget)
        self.Plot4.setGeometry(QtCore.QRect(800, 390, 541, 201))  # Right Plot2
        self.Plot4.setObjectName("Plot4")
        self.Plot4.scene().sigMouseClicked.connect(self.plotClicked)  # Connect mouse click to the plot

        # Example data for plotting
        self.plotData()

    def plotData(self):
        # Generate some example data
        self.Plot1.enableAutoRange()  # Enable automatic scaling of axes
        self.Plot1.showGrid(x=True, y=True)  # Show grid lines
        
        self.Plot2.enableAutoRange()  # Enable automatic scaling of axes
        self.Plot2.showGrid(x=True, y=True)  # Show grid lines

        # Create a timer to update the plot dynamically
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)  # Adjust the interval as needed
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()
        # y3 = np.exp(x)
        # y4 = np.log10(x + 1e-10)  # Adjust to avoid log(0)

        # # Plot the data
        # self.Plot1.plot(x, y1, pen='r', name='Sin')  # Red line
        # self.Plot2.plot(x, y2, pen='b', name='Cos')  # Blue line
        # self.Plot3.plot(x, y3, pen='g', name='e^x')  # Green line
        # self.Plot4.plot(x, y4, pen='y', name='log(x)')  # Yellow line
        
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

if __name__ == "__main__":
    import sys 
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
