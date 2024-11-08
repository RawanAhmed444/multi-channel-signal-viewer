import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QPoint
import pyqtgraph as pg
from pyqtgraph import PlotDataItem, mkPen
from logic.signal_processing import convert_signal_values_to_numeric, cartesian_to_polar
from logic.real_time_data import update_real_time_data
import pandas as pd
import matplotlib.pyplot as plt
from logic.calculate_stats import calculate_statistics
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QColorDialog
from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QGraphicsView
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from scipy import interpolate
from scipy.interpolate import interp1d
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QGraphicsEllipseItem

class NewWindow(QtWidgets.QMessageBox):
    def __init__(self, parent=None):
        super(NewWindow, self).__init__(parent)
        self.setStyleSheet("""
            NewWindow {
                background-color: black;  /* Black background */
                border: 1px solid white;   /* White border */
                border-radius: 3px;      /* Rounded corners */
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

        # Change the standard button to "Close" instead of "OK"
        self.setStandardButtons(QtWidgets.QMessageBox.Close)

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
        closeButton.clicked.connect(self.hide)
        layout.addWidget(closeButton)

    def display_statistics(self, selected_signal_stats):
        selected_signal_stats_text = (
            f"Mean: {selected_signal_stats['mean']:.5f}\n"
            f"Standard Deviation {selected_signal_stats['std']:.5f}\n"
            f"Min: {selected_signal_stats['min']:.5f}\n"
            f"Max: {selected_signal_stats['max']:.5f}\n"
        )
        self.statsLabel.setText(selected_signal_stats_text)

class RightClickPopup(QtWidgets.QMenu):
    def __init__(self, parent=None, selected_signal_data=None, main_window = None, Plot = None):
        super(RightClickPopup, self).__init__(parent)
        self.selected_signal_data = selected_signal_data
        self.main_window = main_window
        self.Plot = Plot
        self.setStyleSheet("""
            QMenu {
            background-color: #1D1C1C;  /* Dark gray background */
            border: 1px solid #636161;  /* White border */
            border-radius: 4px;        /* Rounded corners */
            }
            QMenu::item {
            color: #ffffff;             /* White text */
            padding: 6px 29px;          /* Decreased padding around text */
            font-size: 23px;            /* Decreased font size */
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

        self.setWindowFlags(QtCore.Qt.Popup | QtCore.Qt.FramelessWindowHint)  # Close when clicking outside and remove title bar

        # Add actions to the menu
        self.addAction("Name", self.change_name)
        self.addSeparator()
        self.addAction("Color", self.change_color)
        self.addSeparator()
        self.hide_show_action = self.addAction("Show/Hide", self.hide_plot)
        self.addSeparator()
        self.addAction("Swap" , self.swap_signals)
        self.addSeparator()
        self.addAction("Statistics", self.show_statistics)

    def change_name(self):
        self.setStyleSheet("""
            QInputDialog {
                background-color: black;
                color: white;
            }
            QLineEdit {
                background-color: black;
                color: white;
                border: 1px solid white;
            }
            QLabel {
                color: white;
            }
        """)

        # Open the input dialog
        text, ok = QInputDialog.getText(self, "Change Plot Name", "Enter new name:")

        # If the user pressed OK and entered some text
        if ok and text:
            self.Plot.setTitle(text)  # Change the plot title

    def change_color(self):
        # Open a QColorDialog to let the user pick a color
        color = QColorDialog.getColor()

        if color.isValid():
            color_rgb = color.getRgb()[:3]  # Get (R, G, B) values

            # Iterate through all curves in the plot and set their pen color
            for curve in self.Plot.getPlotItem().listDataItems():
                curve.setPen(color_rgb)

    def hide_plot(self):
            if self.Plot.getPlotItem().listDataItems()[0].isVisible():
                for curve in self.main_window.Plot1.getPlotItem().listDataItems():
                    curve.setVisible(False)
            else:
                for curve in self.main_window.Plot1.getPlotItem().listDataItems():
                    curve.setVisible(True)


    def show_statistics(self):
            self.hide()
            selected_signal_stats = calculate_statistics(self.selected_signal_data)
            stats_popup = StatisticsPopup()
            stats_popup.display_statistics(selected_signal_stats)
            stats_popup.exec_()
            self.close() 

    def swap_signals(self):
        self.hide()
        if self.main_window:
            self.main_window.swap_signals_between_plots(self.Plot)
        self.close()
  
    def showEvent(self, event):
        cursor_pos = QtGui.QCursor.pos()
        self.move(cursor_pos)
        super(RightClickPopup, self).showEvent(event)
    
    

class Ui_MainWindow(object):
    def __init__(self, play_stop_signals, parent=None):
        # Initialize plot_index  and time window size
        self.plot_index = 0  
        self.time_size = 200
        
         # Initialize the non rectangle signal file and its axis
        non_rectangle_signal = "src\\data\\signals\\radar.csv"
        self.x4, self.y4= convert_signal_values_to_numeric(non_rectangle_signal, 1, 2)
        
        # Initialize list to append real-time data
        self.data = []
        
        super().__init__()
        self.play_stop_signals = play_stop_signals
        self.signal_data_plot1 = []  # List to store (x, y) pairs for Plot1
        self.signal_data_plot2 = []  # List to store (x, y) pairs for Plot2
        self.curves_plot1 = []  # Store curves for Plot1
        self.curves_plot2 = []  # Store curves for Plot2
        self.plot_index_plot1 = 0  # Reset the plot index for Plot1
        self.plot_index_plot2 = 0  # Reset the plot index for Plot1

        self.x1, self.y1 = [], []
        self.x2, self.y2 = [], []
        self.original_segment2_position = None
        self.original_segment2_data = []

        self.parent = parent
        self.segments = []  # Store selected segments for interpolation
        self.last_interpolation_curve = None
        self.selected_signal_data = None
        self.original_segment2_data = None  # Store original x-data for segment 2


        self.timer1 = QtCore.QTimer()
        self.timer1.setInterval(150) 

        self.timer2 = QtCore.QTimer()
        self.timer2.setInterval(150)  

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        MainWindow.setStyleSheet("background-color: black;")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        print(type(self.centralwidget.children))

        # Initialize buttons and other UI elements
        self.initButtons()

        # Initialize plots
        self.initPlots()
        
        # Set the central widget
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # def show_real_time_popup(self):
    #     msg_box = NewWindow(self.parent)
    #     msg_box.setTitle("Real-Time")
    #     msg_box.setText("Real-time data visualization is not yet implemented.")
    #     msg_box.setFixedSize(1200, 400)  # Set the size of the popup
    #     msg_box.exec_()

    # def show_non_rectangular_popup(self):
    #     msg_box = NewWindow(self.parent)
    #     msg_box.setTitle("Non-Rectangular")
    #     msg_box.setText("Non-rectangular data visualization is not yet implemented.")
    #     msg_box.setFixedSize(600, 400)  # Set the size of the popup
    #     msg_box.init_non_rectangular_plot(self)
    #     msg_box.exec_()
    
    def init_real_time_plot(self):
        # Initiate graph 3 for real-time signal
        self.Plot3 = pg.plot()
        self.Plot3.setObjectName("Plot3")
        # self.Plot1.scene().sigMouseClicked.connect(self.plotRightClicked)  
        # Set axis labels
        self.Plot3.setLabel('bottom', "Time (s)")
        self.Plot3.setLabel('left', "Real Time Signal")
        self.curve = self.Plot3.plot(pen = 'g')
        
        self.plot_real_time_data()
        
    def plot_real_time_data(self):
        self.Plot3.enableAutoRange()  
        self.Plot3.showGrid(x=True, y=True)

        # Create a timer to update the plot dynamically
        self.timer = QtCore.QTimer()
        # Adjust the interval as needed
        self.timer.setInterval(100)  
        self.timer.timeout.connect(self.update_real_time_plot)
        self.timer.start()
        
    def update_real_time_plot(self):
        # Get new data point
        timestamp, price = update_real_time_data()

        # Add new data point to list
        self.data.append((timestamp, price))

        # Update the curve with all data points
        self.curve.setData(x=[d[0] for d in self.data], y=[d[1] for d in self.data])

        # Limit the number of data points for performance
        if len(self.data) > 100:
            self.data = self.data[-100:]
        
    def init_non_rectangular_plot(self):
        self.Plot4 = pg.plot()
        self.Plot4.setAspectLocked()

        # Add polar grid lines
        self.Plot4.addLine(x=0, pen=0.2)
        self.Plot4.addLine(y=0, pen=0.2)
        for r in range(2, 20, 2):
            circle = QGraphicsEllipseItem(-r, -r, r * 2, r * 2)
            circle.setPen(pg.mkPen(0.2))
            self.Plot4.addItem(circle)
        self.Plot4.setLabel('bottom', "Theta")
        self.Plot4.setLabel('left', "Radial Distance")
        
        self.plot_non_rectangular_data()
        
    def plot_non_rectangular_data(self):
        self.Plot4.enableAutoRange()  
        self.Plot4.showGrid(x=True, y=True)

        # Create a timer to update the plot dynamically
        self.timer = QtCore.QTimer()
        # Adjust the interval as needed
        self.timer.setInterval(100)  
        self.timer.timeout.connect(self.update_non_rectangle_plot)
        self.timer.start()
    
    def update_non_rectangle_plot(self):
        # Update the plot with new data points for non-rectangle signal
        if self.plot_index < len(self.x4):
            self.plot_index += 1

            # Calculate the start and end indices for the dynamic time window
            start_index = max(self.plot_index - self.time_size, 0)  
            end_index = self.plot_index
            
            # Calculate theta (angle) and radial distance (r)
            theta = np.arctan2(self.y4[start_index:end_index], self.x4[start_index:end_index])
            r = np.sqrt(self.x4[start_index:end_index]**2 + self.y4[start_index:end_index]**2)

            # Update the plot with polar coordinates
            self.Plot4.plot(theta, r, pen='y', clear=False)
            
            # Adjust the pause time for animation speed
            plt.pause(0.01)
        
    def initButtons(self):


        self.RealTimeButton = self.createButton("Real-Time", 800, 10, size=(150, 50), font_size=20)
        self.NonRectangularButton = self.createButton("Non-Rectangular", 1000, 10, size=(200, 50), font_size=20)

        self.RealTimeButton.clicked.connect(self.init_real_time_plot)
        self.NonRectangularButton.clicked.connect(self.init_non_rectangular_plot)

        # Button configurations (shifted down by 50 pixels)
        self.Signal1 = self.createButton("Signal", 15, 70)   # Left Signal button with icon
        self.Link = self.createButton("Link Plot", 300, 440, size=(280, 50))  
        self.is_linked = False  # Initial state
        self.Play_stop1 = self.createToggleButton("src/data/Images/Pause.png", "src/data/Images/Play.png", 610, 440, )    # Left Toggle P/S button
        self.Speed1 = self.createSpeedButton(690, 440)       # Left Speed button
        self.ZoomIn1 = self.createButtonWithIcon("src/data/Images/Zoom in.png", 770, 440, )  # Left Zoom In button
        self.ZoomOut1 = self.createButtonWithIcon("src/data/Images/Zoom out.png", 850, 440, ) # Left Zoom Out button
        self.Snapshot1 = self.createButtonWithIcon("src/data/Images/Snapshot.png", 930, 440, )     # Left SS button


        self.Signal1.clicked.connect(self.load_first_signal)
        self.ZoomIn1.clicked.connect(self.zoom_in_1)
        self.ZoomOut1.clicked.connect(self.zoom_out_1)
        self.Link.clicked.connect(self.link_plots)
    
        
        self.Signal2 = self.createButton("Signal", 15, 530)   # Left Signal button with icon
        self.Play_stop2 = self.createToggleButton("src\data\Images\Pause.png", "src/data/Images/Play.png", 610, 900, )    # Left Toggle P/S button for second plot
        self.Speed2 = self.createSpeedButton(690, 900)       # Left Speed button for second plot
        self.ZoomIn2 = self.createButtonWithIcon("src/data/Images/Zoom in.png", 770, 900, )  # Left Zoom In button for second plot
        self.ZoomOut2 = self.createButtonWithIcon("src/data/Images/Zoom out.png", 850, 900, ) # Left Zoom Out button
        self.Snapshot2 = self.createButtonWithIcon("src/data/Images/Snapshot.png", 930, 900, )     # Left SS button for second plot
        
        self.Signal2.clicked.connect(self.load_second_signal)
        self.ZoomIn2.clicked.connect(self.zoom_in_2)
        self.ZoomOut2.clicked.connect(self.zoom_out_2)
       
        # Right side buttons (renamed mirrored buttons)
        self.ZoomIn3 = self.createButtonWithIcon("src/data/Images/Zoom in.png", 1680, 670)  # Right Zoom In button
        self.ZoomOut3 = self.createButtonWithIcon("src/data/Images/Zoom out.png", 1760, 670 ) # Right Zoom Out button
        self.Snapshot3 = self.createButtonWithIcon("src/data/Images/Snapshot.png", 1840, 670)     # Right SS button   
        
        self.ZoomIn3.clicked.connect(self.zoom_in_3)
        self.ZoomOut3.clicked.connect(self.zoom_out_3)    

        self.Report = self.createButton("Report",1250, 800, size=(250, 60), font_size=40)  # Report button

        self.radioBoxGroup = QtWidgets.QGroupBox(self.centralwidget)
        self.radioBoxGroup.setGeometry(QtCore.QRect(1600, 755, 160, 150))
        self.radioBoxGroup.setStyleSheet("""
            QGroupBox {
            background-color: #353535;  /* Dark gray background */
            color: #ffffff;             /* White text */
            border: 1px solid #959494;  /* White border */
            border-radius: 6px;         /* Rounded corners */
            font-size: 24px;            /* Font size */                       
            font-weight: bold;          /* Bold text */
            font-family: 'Arial', 'Helvetica', sans-serif; /* Elegant font */

            }
            QRadioButton {
            color: #ffffff;             /* White text */
            font-size: 28px;            /* Font size */
            font-weight: normal;        /* Normal text weight */
            font-family: 'Arial', 'Helvetica', sans-serif; /* Elegant font */
            background-color: transparent; /* Transparent background */
            text-align: Center;           /* Center text */

            }
        """)

        self.radioLinear = QtWidgets.QRadioButton("Linear", self.radioBoxGroup)
        self.radioLinear.setGeometry(QtCore.QRect(10, 30, 150, 30))

        self.radioQuadratic = QtWidgets.QRadioButton("Quadratic", self.radioBoxGroup)
        self.radioQuadratic.setGeometry(QtCore.QRect(10, 60, 150, 30))


        self.radioCubic = QtWidgets.QRadioButton("Cubic", self.radioBoxGroup)
        self.radioCubic.setGeometry(QtCore.QRect(10, 90, 150, 30))

        # Set default selection
        self.radioLinear.setChecked(True)

        # Create a slider below the 3rd graph
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.centralwidget)
        self.slider.setGeometry(QtCore.QRect(1120, 680, 500, 30))  # Position the slider below the 3rd graph
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
            background: #353535;  /* Dark gray background */
            height: 10px;         /* Groove height */
            border-radius: 5px;   /* Rounded corners */
            }
            QSlider::sub-page:horizontal {
            background: #616161;  /* Color behind the handle */
            border-radius: 5px;   /* Rounded corners */
            }
            QSlider::handle:horizontal { 
            background-color: #616161; 
            border: 2px solid #121212; 
            width: 20px; 
            height: 24px; 
            line-height: 20px; 
            margin-top: -7px; 
            margin-bottom: -7px; 
            border-radius: 12px; 
            }
        """)
        self.slider.setMinimum(0)
        self.slider.setMaximum(8)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.update_distance)

        self.radioLinear.toggled.connect(self.perform_interpolation)
        self.radioQuadratic.toggled.connect(self.perform_interpolation)
        self.radioCubic.toggled.connect(self.perform_interpolation)

    def load_first_signal(self):
        # Check if maximum signals have already been loaded
        if len(self.signal_data_plot1) >= 5:
            print("Maximum limit of 5 signals already loaded for Plot1.")
            return

        filename = askopenfilename(title="Select signal file for Plot1",
                                   filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if filename:
            try:
                # Load the data from the selected file
                x, y = convert_signal_values_to_numeric(filename, 0, 1)
                self.signal_data_plot1.append((x, y))  # Append the loaded signal
                print(f"Loaded signal {len(self.signal_data_plot1)} from {filename}")

                # Create a new curve for the loaded signal
                curve = self.createCurve(self.Plot1)
                self.curves_plot1.append(curve)  # Store the new curve

                # Connect the timer to update the plot for Plot1
                self.timer1.timeout.connect(lambda: self.update_plot(self.signal_data_plot1, self.curves_plot1, 1))

            except Exception as e:
                print(f"Error loading signal: {e}")

    def load_second_signal(self):
        # Check if maximum signals have already been loaded
        if len(self.signal_data_plot2) >= 5:
            print("Maximum limit of 5 signals already loaded for Plot2.")
            return

        filename = askopenfilename(title="Select signal file for Plot2",
                                   filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if filename:
            try:
                # Load the data from the selected file
                x, y = convert_signal_values_to_numeric(filename, 0, 1)
                self.signal_data_plot2.append((x, y))  # Append the loaded signal
                print(f"Loaded signal {len(self.signal_data_plot2)} from {filename}")

                # Create a new curve for the loaded signal
                curve = self.createCurve(self.Plot2)
                self.curves_plot2.append(curve)  # Store the new curve

                # Connect the timer to update the plot for Plot2
                self.timer2.timeout.connect(lambda: self.update_plot(self.signal_data_plot2, self.curves_plot2, 2))

            except Exception as e:
                print(f"Error loading signal: {e}")
    # Rawan Work Do not Touch
    def load_fourth_signal(self):
        # Open the file dialog for the second signal
        filename = askopenfilename(title="Select the second signal file",
                                   filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if filename:
            try:
                # Load the data from the second file
                self.x4, self.y4 = convert_signal_values_to_numeric(filename, 1, 2)
                print(f"Loaded second signal from {filename}")
            except Exception as e:
                print(f"Error loading second file: {e}")

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

    def link_plots(self):
        if self.is_linked:
            # Unlink the plots
            self.Plot2.setXLink(None)
            self.Plot2.setYLink(None)
            self.Link.setText("Link Plots")  # Change button text to "Link Plots"
            self.is_linked = False  # Update the state
        else:
            # Link the plots and set the same zoom
            self.Plot2.setXLink(self.Plot1)
            self.Plot2.setYLink(self.Plot1)
            # Synchronize zoom levels
            self.Plot2.getViewBox().setRange(xRange=self.Plot1.getViewBox().viewRange()[0],
                                             yRange=self.Plot1.getViewBox().viewRange()[1],
                                             padding=0)
            self.Link.setText("Unlink Plots")  # Change button text to "Unlink Plots"
            self.is_linked = True  # Update the state
    
    def createButton(self, text, x, y, slot=None, size=(150, 50), font_size=30):
        button = QtWidgets.QPushButton(self.centralwidget)
        button.setGeometry(QtCore.QRect(x, y, *size))
        button.setText(text)
        button.setStyleSheet(self.getButtonStyle(font_size))
        if slot:
            button.clicked.connect(slot)
        return button

    def createButtonWithIcon(self, icon_path, x, y, size=(50, 50)):
        button = QtWidgets.QPushButton(self.centralwidget)
        button.setGeometry(QtCore.QRect(x, y, *size))
        button.setIcon(QtGui.QIcon(icon_path))
        button.setIconSize(QtCore.QSize(size[0] - 10, size[1] - 10))  # Adjust icon size to fit within the button
        button.setStyleSheet(self.getButtonStyle())
        return button
    
    def createSpeedButton(self, x, y, size=(50, 50), default_speed=1):
       button = QtWidgets.QPushButton(f"{default_speed}x", self.centralwidget)
       button.setGeometry(QtCore.QRect(x, y, *size))
       button.setStyleSheet(self.getSpeedButtonStyle())
       button.speeds = [1.0, 1.5, 2.0, 8.0, 0.25, 0.5] 
       button.current_speed_index = button.speeds.index(default_speed)
       return button

    def createToggleButton(self, icon1_path, icon2_path, x, y, size=(50, 50)):
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
    
    def getButtonStyle(self, font_size=30):
        return (
            "QPushButton {\n"
            "    background-color: #353535;      /* Dark gray background */\n"
            "    color: #ffffff;                 /* White text */\n"
            "    border: 1px solid #959494;      /* White border */\n"
            "    border-radius: 6px;             /* Rounded corners */\n"
            f"    font-size: {font_size}px;       /* Font size */\n"  # Dynamic font size
            "    font-weight: bold;              /* Bold text */\n"            
            "    font-family: 'Georgia', 'Garamond', 'Times New Roman', serif; /* Elegant font */\n"
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
            "    font-size: 16px;                /* Increased font size */\n"  # Increased size
            "    font-weight: bold;              /* Bold text */\n"            # Bold text
            "    font-family: 'Georgia', 'Garamond', 'Times New Roman', serif; /* Elegant font */\n"
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

    def update_distance(self, value):
        if hasattr(self, 'segments') and len(self.segments) == 2:
            segment1 = self.segments[0]
            segment2 = self.segments[1]

            x1_min, x1_max, _ = segment1
            x2_min, x2_max, _ = segment2

            # Store original data for the second segment 
            if self.original_segment2_data is None:
                self.original_segment2_data = self.get_data_for_segment(segment2)
                
                if self.original_segment2_data is None:
                    print("Error: No data found for segment 2.")
                    return

            # Calculate the minimum allowed distance 
            min_distance = x1_max - x1_min + 1

            # Calculate shift amount
            shift_amount = (x2_min - x1_max - min_distance) * (1 - value / 100.0)

            # Update x positions for segment2 based on the slider
            new_x2_min = x2_min - shift_amount
            new_x2_max = x2_max - shift_amount
            self.segments[1] = (new_x2_min, new_x2_max, segment2[2])

            # Store the latest new_x2_min for interpolation reference
            self.current_x2_min = new_x2_min

            # Shift all x-values of the second segment if the original data is available
            try:
                if self.original_segment2_data is not None:
                    original_x_data, original_y_data = zip(*self.original_segment2_data)
                    shifted_x_data = np.array(original_x_data) - shift_amount
                    self.shifted_segment_data = list(zip(shifted_x_data, original_y_data))
            except TypeError as e:
                print("Error during data transformation:", e)
                return

            # Re-plot the segments and adjust the x-axis range
            self.plot_selected_regions_on_plot3()
            self.Plot3.setXRange(x1_min, new_x2_max)
            self.perform_interpolation()

    def get_data_for_segment(self, segment):
        x_min, x_max, source_plot = segment

        # Retrieve the appropriate data based on the source plot
        data = self.signal_data_plot1 if source_plot == self.Plot1 else self.signal_data_plot2

        # Convert data to NumPy arrays 
        x_data = np.array([x for x, y in data])
        y_data = np.array([y for x, y in data])

        # Create a mask to select data within the range [x_min, x_max]
        mask = (x_data >= x_min) & (x_data <= x_max)

        # Filter x and y data
        selected_x = x_data[mask]
        selected_y = y_data[mask]

        if len(selected_x) == 0 or len(selected_y) == 0:
            print("Warning: No data found in the range [{}, {}].".format(x_min, x_max))
            return None

        return list(zip(selected_x, selected_y))

    def plotRightClicked(self, event, plot):
        if event.button() == QtCore.Qt.RightButton:
           self.on_plot_click(event, plot)
        elif event.button() == QtCore.Qt.LeftButton:
            self.select_region(plot, event)

    def on_plot_click(self, event, plot_widget):
        full_y_data = []
        x_data = None
        items = plot_widget.listDataItems()
        print("Number of items in plot:", len(items))   
        if items:
            for signal in items: 
                x_data, y_data = signal.getData()
                if y_data is not None:
                    full_y_data.extend(y_data)
                else:
                    print("Warning: y_data is None for one of the signals.")

        full_y_data = np.array(full_y_data)
        
        self.selected_signal_data = full_y_data

        if event.button() == QtCore.Qt.RightButton:
            context_menu = RightClickPopup(
            parent=self.parent,
            selected_signal_data=self.selected_signal_data,
            main_window=self,
            Plot= plot_widget
        )
            context_menu.exec_(QPoint(int(event.screenPos().x()), int(event.screenPos().y()))) #show the menu at the mouse position 

    
    def select_region(self, plot, event):
        mouse_point = plot.getViewBox().mapSceneToView(event.scenePos())
        x_pos = mouse_point.x()

        if not hasattr(self, 'region_start'):
            # First left-click: Start region selection
            self.region_start = x_pos
            self.selection_rect = pg.LinearRegionItem([self.region_start, self.region_start], pen='b', brush=(100, 100, 255, 50))
            plot.addItem(self.selection_rect)
        else:
            # Second left-click: End region selection
            self.region_end = x_pos
            self.selection_rect.setRegion([self.region_start, self.region_end])

            if not hasattr(self, 'segments'):
                self.segments = [] 

            # Store the new segment
            self.segments.append((self.region_start, self.region_end, plot))  

            # Plot selected segments on Plot3
            self.plot_selected_regions_on_plot3()

            # Remove selection rectangle after plotting
            plot.removeItem(self.selection_rect)

            # Reset region selection for the next region
            del self.region_start, self.region_end

    def plot_selected_regions_on_plot3(self):
        # Clear the plot to start fresh
        self.Plot3.clear()

        if hasattr(self, 'segments'):
            # Plot the first segment
            self.plot_selected_region(self.segments[0])

            # Plot the second segment 
            if len(self.segments) == 2:
                if hasattr(self, 'shifted_segment_data'):
                    shifted_x, shifted_y = zip(*self.shifted_segment_data)
                    self.Plot3.plot(shifted_x, shifted_y, pen='b')
                else:
                    self.plot_selected_region(self.segments[1])

                self.perform_interpolation()

    def plot_selected_region(self, segment):
        if segment is None:
            return

        # Unpack the segment tuple
        x_min, x_max, source_plot = segment

        data = self.signal_data_plot1 if source_plot == self.Plot1 else self.signal_data_plot2

        x_data = np.array([x for x, y in data])
        y_data = np.array([y for x, y in data])

        # Create a mask to select data within the range [x_min, x_max]
        mask = (x_data >= x_min) & (x_data <= x_max)

        # Filter x and y data
        selected_x = x_data[mask]
        selected_y = y_data[mask]

        # Plot the selected region on Plot3
        self.Plot3.plot(selected_x, selected_y, pen='b')

    def perform_interpolation(self):

        if hasattr(self, 'last_interpolation_curve') and self.last_interpolation_curve is not None:
            self.Plot3.removeItem(self.last_interpolation_curve)

        if len(self.segments) == 2:
                segment1, segment2 = self.segments
                x1_min, x1_max, plot = segment1  
                # x2_min, x2_max, _ = segment2
                # Use the updated new_x2_min from the slider adjustments
                x2_min = getattr(self, 'current_x2_min', segment2[0])
                print(f"Performing interpolation between x1_max: {x1_max} and new_x2_min: {x2_min}")

                x_values = [x1_max, x2_min]

                # Flatten the data arrays for segment 1 and 2
                x_data1 = np.array([x for x, y in (self.signal_data_plot1 if plot == self.Plot1 else self.signal_data_plot2)]).flatten()
                y_data1 = np.array([y for x, y in (self.signal_data_plot1 if plot == self.Plot1 else self.signal_data_plot2)]).flatten()
                x_data2 = np.array([x for x, y in (self.signal_data_plot1 if plot == self.Plot1 else self.signal_data_plot2)]).flatten()
                y_data2 = np.array([y for x, y in (self.signal_data_plot1 if plot == self.Plot1 else self.signal_data_plot2)]).flatten()

                # Get y-values at the end points using updated segment values
                y1_end = self.get_y_value_for_x(x_data1, y_data1, x1_max)
                y2_start = self.get_y_value_for_x(x_data2, y_data2, x2_min)

                if self.radioLinear.isChecked():
                    x_interp = np.linspace(x1_max, x2_min, num=150)
                    y_interp = np.interp(x_interp, x_values, [y1_end, y2_start])
                elif self.radioQuadratic.isChecked():
                    coeffs = np.polyfit(x_values, [y1_end, y2_start], 2)
                    poly_func = np.poly1d(coeffs)
                    x_interp = np.linspace(x1_max, x2_min, num=150)
                    y_interp = poly_func(x_interp)
                elif self.radioCubic.isChecked():
                    coeffs = np.polyfit(x_values, [y1_end, y2_start], 3)
                    poly_func = np.poly1d(coeffs)
                    x_interp = np.linspace(x1_max, x2_min, num=150)
                    y_interp = poly_func(x_interp)

                self.last_interpolation_curve = self.Plot3.plot(x_interp, y_interp, pen='r')

    def get_y_value_for_x(self, x_data, y_data, x_value):
        if len(x_data) == 0:
            return None  
        return np.interp(x_value, x_data, y_data)

    def swap_signals_between_plots(self, clicked_plot):
        # Identify source and target plots based on the clicked plot
        if clicked_plot == self.Plot1:
            source_plot = self.Plot1
            target_plot = self.Plot2
            source_timer = self.timer1
            target_timer = self.timer2
            source_curves = self.curves_plot1
            target_curves = self.curves_plot2
            source_signal_data = self.signal_data_plot1
            target_signal_data = self.signal_data_plot2
            source_plot_index = self.plot_index_plot1
            target_plot_index = self.plot_index_plot2
        else:
            source_plot = self.Plot2
            target_plot = self.Plot1
            source_timer = self.timer2
            target_timer = self.timer1
            source_curves = self.curves_plot2
            target_curves = self.curves_plot1
            source_signal_data = self.signal_data_plot2
            target_signal_data = self.signal_data_plot1
            source_plot_index = self.plot_index_plot2
            target_plot_index = self.plot_index_plot1

        source_timer.stop()
        target_timer.stop()

        # Ensure both source and target plots have data to swap
        if len(source_curves) == 0 or len(target_curves) == 0:
            print("Either source or target plot has no data to swap.")
            return

        # Get the current data from both plots
        source_x_data, source_y_data = source_curves[0].getData()
        target_x_data, target_y_data = target_curves[0].getData()

        source_plot.clear()
        target_plot.clear()

        new_target_curve = target_plot.plot(source_x_data, source_y_data, pen='r')  
        new_source_curve = source_plot.plot(target_x_data, target_y_data, pen='b')  

        if clicked_plot == self.Plot1:
            self.curves_plot1 = [new_source_curve]  
            self.curves_plot2 = [new_target_curve]  
            self.signal_data_plot1, self.signal_data_plot2 = target_signal_data, source_signal_data  
            self.plot_index_plot1, self.plot_index_plot2 = target_plot_index, source_plot_index  
        else:
            self.curves_plot1 = [new_target_curve]  
            self.curves_plot2 = [new_source_curve]  
            self.signal_data_plot1, self.signal_data_plot2 = source_signal_data, target_signal_data  
            self.plot_index_plot1, self.plot_index_plot2 = source_plot_index, target_plot_index  

        source_timer.start()
        target_timer.start()

        print("Signals swapped between Plot1 and Plot2")

    def initPlots(self):
        self.Plot1 = pg.PlotWidget(self.centralwidget)
        self.Plot1.setGeometry(QtCore.QRect(180, 70, 800, 350)) 
        self.Plot1.setObjectName("Plot1")
        self.Plot1.scene().sigMouseClicked.connect(lambda event: self.plotRightClicked(event, self.Plot1))  
        signal1_time_length = len(self.x1)
        signal1_value_length = len(self.y1)
        #Set x and y limits 
        self.Plot1.setXRange(0, signal1_time_length)  
        self.Plot1.setYRange(0, signal1_value_length) 
        # Set axis labels
        self.Plot1.setLabel('bottom', "Time (s)")
        self.Plot1.setMenuEnabled(False)
        # Initiate graph 2 for abnormal signal
        self.Plot2 = pg.PlotWidget(self.centralwidget)
        self.Plot2.setGeometry(QtCore.QRect(180, 530, 800, 350))  
        self.Plot2.setObjectName("Plot2")
        self.Plot2.scene().sigMouseClicked.connect(lambda event: self.plotRightClicked(event, self.Plot2))  
        signal2_time_length = len(self.x2)
        signal2_value_length = len(self.y2)
        # Set x and y limits 
        self.Plot2.setXRange(0, signal2_time_length)  
        self.Plot2.setYRange(0, signal2_value_length) 
        # Set axis labels
        self.Plot2.setLabel('bottom', "Time (s)")
        self.Plot2.setMenuEnabled(False)

        # Mirrored plots
        self.Plot3 = pg.PlotWidget(self.centralwidget)
        self.Plot3.setGeometry(QtCore.QRect(1090, 300, 800, 350))  
        self.Plot3.setObjectName("Plot3")
        self.Plot3.setMenuEnabled(False)
        self.Plot3.scene().sigMouseClicked.connect(lambda event: self.plotRightClicked(event, self.Plot3))

        self.plotData()

    def createCurve(self, Plot):
        curve = Plot.plot(clear=False)
        return curve

    def plotData(self):
        self.Plot1.enableAutoRange()
        self.Plot1.showGrid(x=True, y=True)  
        self.timer1.start()
        
        self.Plot2.enableAutoRange()  
        self.Plot2.showGrid(x=True, y=True) 
        self.timer2.start()

        # Initialize plot indices separately for each plot
        self.plot_index1 = 0
        self.plot_index2 = 0

    # Function responsible for play/pause
    def toggle_play_stop(self, plot_id):
        if self.play_stop_signals.is_playing(plot_id):
            self.play_stop_signals.stop_signal(plot_id)
            self.control_plot(plot_id, start=False)
        else:
            self.play_stop_signals.start_signal(plot_id)
            self.control_plot(plot_id, start=True)

    # Control function for starting/stopping the timer for each plot
    def control_plot(self, plot_id, start):
        if start:
            if plot_id == 1:
                self.timer1.start()
                print(f"Plot {plot_id} started.")
            elif plot_id == 2:
                self.timer2.start()
                print(f"Plot {plot_id} started.")
        else:
            if plot_id == 1:
                self.timer1.stop()
                print(f"Plot {plot_id} stopped.")
            elif plot_id == 2:
                self.timer2.stop()
                print(f"Plot {plot_id} stopped.")

    # function responsible for speed
    def toggleSpeed(self, button, plot_id):
       button.speeds = [1.0, 1.5, 2.0, 8.0, 0.25, 0.5] 
       button.current_speed_index = (button.current_speed_index + 1) % len(button.speeds)
       new_speed = button.speeds[button.current_speed_index]
       button.setText(f"{new_speed}x")
       print(f"Speed set to: {new_speed}x")
       if plot_id == 1:
            self.timer1.setInterval(int(150 / new_speed))
       else:
            self.timer2.setInterval(int(150 / new_speed))

    def update_plot(self, signal_data, curves, plot_id):
        if plot_id == 1:
            plot_index = self.plot_index_plot1
            signal_data = self.signal_data_plot1
            curves = self.curves_plot1
        elif plot_id == 2:
            plot_index = self.plot_index_plot2
            signal_data = self.signal_data_plot2
            curves = self.curves_plot2

        if self.play_stop_signals.is_playing(plot_id):
            # Loop through each signal and update the corresponding curve
            for i, curve in enumerate(curves):
                if i < len(signal_data):
                    x, y = signal_data[i]

                    # Check that plot_index is within bounds
                    if plot_index < len(x) and plot_index > 0:
                        start_index = max(plot_index - 200, 0)
                        end_index = min(plot_index, len(x))  # Ensure end_index is within bounds

                        # Update the current curve with its specific signal data
                        curve.setData(x[start_index:end_index], y[start_index:end_index])

                    else:
                        # Prevent negative or zero values in case of an invalid index
                        curve.setData([], [])

            # Increment the plot_index to move to the next data point
            if plot_id == 1:
                self.plot_index_plot1 += 1
                
            elif plot_id == 2:
                self.plot_index_plot2 += 1
                
            # Set the x-axis limits based on the first signal in the current plot
            # if signal_data:
            #     x_min = min(signal_data[0][0])  # Minimum x of the first signal
            #     x_max = max(signal_data[0][0])  # Maximum x of the first signal
            #     curves[0].setXRange(x_min, x_max)

            plt.pause(0.01)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate


# def plot_selected_regions_on_plot3(self):
    #     # Clear the plot to start fresh
    #     self.Plot3.clear()

    #     if hasattr(self, 'segments'):
    #         # Plot the first segment
    #         self.plot_selected_region(self.segments[0])

    #         # Check if we have two segments to plot
    #         if len(self.segments) == 2:
    #             segment1 = self.segments[0]
    #             segment2 = self.segments[1]
    #             x1_min, x1_max, _ = segment1
    #             x2_min, x2_max, _ = segment2

    #             # Handle the shifted second segment based on slider value
    #             if hasattr(self, 'shifted_segment_data'):
    #                 shifted_x, shifted_y = zip(*self.shifted_segment_data)
    #                 self.Plot3.plot(shifted_x, shifted_y, pen='b')
    #             else:
    #                 # Plot the second segment normally if not shifted
    #                 self.plot_selected_region(segment2)

    #             # Calculate the overlap region for interpolation
    #             overlap_start = max(x1_min, x2_min)
    #             overlap_end = min(x1_max, x2_max)
    #             print(f"overlap_start: {overlap_start}")
    #             print(f"overlap_end: {overlap_end}")

    #             # Perform interpolation if required
    #             self.perform_interpolation(overlap_start, overlap_end)

    
    # def plot_selected_region(self, segment):
    #     if segment is None:
    #         return

    #     # Unpack the segment tuple for min, max, and source plot
    #     x_min, x_max, source_plot = segment

    #     # Retrieve the appropriate data for the selected plot
    #     if source_plot == self.Plot1:
    #         data = self.signal_data_plot1  # Get data for Plot1
    #     else:
    #         data = self.signal_data_plot2  # Get data for Plot2

    #     # Assuming data is a list of (x, y) tuples, convert to NumPy arrays for easier filtering
    #     x_data = np.array([x for x, y in data])
    #     y_data = np.array([y for x, y in data])

    #     # Create a mask to select data within the range [x_min, x_max]
    #     mask = (x_data >= x_min) & (x_data <= x_max)
        
    #     # Apply the mask to filter x and y data
    #     selected_x = x_data[mask]
    #     selected_y = y_data[mask]

    #     # Plot the selected region on Plot3
    #     self.Plot3.plot(selected_x, selected_y, pen='b')

# def update_distance(self, value):
    #     if hasattr(self, 'segments') and len(self.segments) == 2:
    #         # Get the segments and their original positions
    #         segment1 = self.segments[0]
    #         segment2 = self.segments[1]
    #         x1_min, x1_max, _ = segment1
    #         x2_min, x2_max, _ = segment2

    #         # Store original data for the second segment if not already done
    #         if not hasattr(self, 'original_segment2_data'):
    #             self.original_segment2_data = self.get_data_for_segment(segment2)  # Get original data for segment 2

    #         # Calculate the distance adjustment based on the slider value (0 to 100)
    #         # When value is 0, segments are at their original positions
    #         # When value is 100, segments overlap completely (x1_max == x2_min)
    #         shift_amount = (x1_max - x2_min) * (value / 100.0)  # Shifts towards overlap when value increases

    #         # Update the x2_min and x2_max based on the shift amount
    #         new_x2_min = x2_min + shift_amount
    #         new_x2_max = x2_max + shift_amount
    #         self.segments[1] = (new_x2_min, new_x2_max, segment2[2])  # Update the segment with new min/max

    #         # Store the shifted data for the second segment to use during plotting
    #         original_x_data, original_y_data = zip(*self.original_segment2_data)
    #         shifted_x_data = np.array(original_x_data) + shift_amount
    #         self.shifted_segment_data = list(zip(shifted_x_data, original_y_data))

    #         # Re-plot the segments and update the x-axis range to fit them both
    #         self.plot_selected_regions_on_plot3()

    #         # Adjust the x-axis range of Plot3 to fit both segments
    #         self.adjust_plot3_x_range(x1_min, new_x2_max)  # Ensure the range fits both segments


    
    # def adjust_plot3_x_range(self, x_min, x_max):
    #     """Adjusts the x-axis range of Plot3."""
    #     self.Plot3.setXRange(x_min, x_max)
# def perform_interpolation(self, overlap_start=None, overlap_end=None):
    #     # Remove the previous interpolation curve if it exists
    #     if self.last_interpolation_curve is not None:
    #         self.Plot3.removeItem(self.last_interpolation_curve)

    #     # Ensure we have two segments selected for interpolation
    #     if len(self.segments) == 2:
    #         segment1, segment2 = self.segments
    #         x1_min, x1_max, plot1 = segment1  
    #         x2_min, x2_max, _ = segment2  # This will now have the updated x2_min

    #         # Check if there's an overlap for averaging
    #         if overlap_start is not None and overlap_end is not None and overlap_start < overlap_end:
    #             x_values_overlap = np.linspace(overlap_start, overlap_end, num=100)
    #             y_values_segment1_overlap = self.get_interpolated_y_values(segment1, x_values_overlap)
    #             y_values_segment2_overlap = self.get_interpolated_y_values(segment2, x_values_overlap)

    #             # Calculate the average y-values in the overlapping region
    #             y_values_avg = (y_values_segment1_overlap + y_values_segment2_overlap) / 2

    #             # Plot the averaged y-values in the overlap on Plot3
    #             self.last_interpolation_curve = self.Plot3.plot(x_values_overlap, y_values_avg, pen='r')

    #         else:
    #             # Handle no overlap and interpolate between the segments
    #             x_values = [x1_max, x2_min]  # Will use updated x2_min

    #             # Extract x_data and y_data for plot1 and plot2
    #             x_data1 = np.array([x for x, y in (self.signal_data_plot1 if plot1 == self.Plot1 else self.signal_data_plot2)]).flatten()
    #             y_data1 = np.array([y for x, y in (self.signal_data_plot1 if plot1 == self.Plot1 else self.signal_data_plot2)]).flatten()
    #             x_data2 = np.array([x for x, y in (self.signal_data_plot1 if plot2 == self.Plot1 else self.signal_data_plot2)]).flatten()
    #             y_data2 = np.array([y for x, y in (self.signal_data_plot1 if plot2 == self.Plot1 else self.signal_data_plot2)]).flatten()

    #             # Get y-values at the end points using updated segment values
    #             y1_end = self.get_y_value_for_x(x_data1, y_data1, x_values[0])
    #             y2_start = self.get_y_value_for_x(x_data2, y_data2, x_values[1])
                        
    #             # Perform interpolation (linear, quadratic, or cubic)
    #             if self.radioLinear.isChecked():
    #                 x_interp = np.linspace(x1_max, x2_min, num=150)
    #                 y_interp = np.interp(x_interp, x_values, [y1_end, y2_start])
    #             elif self.radioQuadratic.isChecked():
    #                 coeffs = np.polyfit(x_values, [y1_end, y2_start], 2)
    #                 poly_func = np.poly1d(coeffs)
    #                 x_interp = np.linspace(x1_max, x2_min, num=150)
    #                 y_interp = poly_func(x_interp)
    #             elif self.radioCubic.isChecked():
    #                 coeffs = np.polyfit(x_values, [y1_end, y2_start], 3)
    #                 poly_func = np.poly1d(coeffs)
    #                 x_interp = np.linspace(x1_max, x2_min, num=150)
    #                 y_interp = poly_func(x_interp)

    #             # Plot the interpolated values on Plot3
    #             self.last_interpolation_curve = self.Plot3.plot(x_interp, y_interp, pen='r')
    # # Ensure the get_y_value_for_x function is also defined properly:
    # def get_y_value_for_x(self, x_data, y_data, x_value):
    #     if len(x_data) == 0:
    #         return None  
    #     return np.interp(x_value, x_data, y_data)
