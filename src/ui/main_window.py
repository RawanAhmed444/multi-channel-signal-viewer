import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from pyqtgraph import PlotDataItem
from logic.signal_processing import load_signal_from_file
import pandas as pd
import matplotlib.pyplot as plt
from logic.calculate_stats import calculate_statistics
from logic.move_signals import move_selected_signal
from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QGraphicsView
from tkinter import Tk
from tkinter.filedialog import askopenfilename


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
    def __init__(self):
        super(StatisticsPopup, self).__init__()
        self.popup_menu = RightClickPopup(self)
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
    def __init__(self, parent=None, source_plot=None, selected_signal=None, selected_signal_data=None, target_plot=None, source_timer=None, target_timer=None, move_signal=None):
        super(RightClickPopup, self).__init__(parent)
        self.selected_signal_data = selected_signal_data
        self.source_plot = source_plot
        self.target_plot = target_plot
        self.source_timer = source_timer 
        self.target_timer = target_timer  
        self.move_signal = move_signal
        self.selected_signal = selected_signal
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

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Remove title bar

        # Add actions to the menu
        self.addAction("Name", self.close)
        self.addSeparator()
        self.addAction("Color", self.close)
        self.addSeparator()
        self.addAction("Hide", self.close)
        self.addSeparator()
        self.addAction("Move" , self.move_signal_action)
        self.addSeparator()
        self.addAction("Statistics", self.show_statistics)

    def move_signal_action(self):
        print("Move action triggered")
        self.hide()  # Hide the context menu
        if self.source_plot and self.target_plot and self.selected_signal:
            self.move_signal(self.source_plot, self.target_plot, self.source_timer, self.target_timer)

    def move_signal(self):
        if self.source_plot and self.target_plot and self.selected_signal:
            self.hide()
            move_selected_signal(self.source_plot, self.target_plot, self.source_timer, self.target_timer)

    def show_statistics(self):
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
    
    def __init__(self, play_stop_signals):
        super().__init__()
        self.play_stop_signals = play_stop_signals
        self.plot_index = 0  # Initialize plot_index
        self.parent = None

        # normal_signal = "src\\data\\signals\\ECG_Normal.csv"
        # self.x1, self.y1 = self.convert_signal_values_to_numeric(normal_signal)
        
        # abnormal_signal = "src\\data\\signals\\ECG_Abnormal.csv"
        # self.x2, self.y2 = self.convert_signal_values_to_numeric(abnormal_signal)
    
        self.x1, self.y1 = [0], [0]
        self.x2, self.y2 = [0], [0]

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
        
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1920, 21))
        self.menubar.setObjectName("menubar")
        self.menubar.setStyleSheet("""
            QMenuBar {
            background-color: #353535;  /* Dark gray background */
            border: 1px solid #636161;  /* White border */
            }
            QMenuBar::item {
            color: #ffffff;             /* White text */
            font-size: 16px;            /* Font size */
            font-weight: bold;          /* Bold text */
            font-family: 'Arial', 'Helvetica', sans-serif; /* Elegant font */
            }
            QMenuBar::item:selected {
            background-color: #403F3F;  /* Lighter gray for hover */
            }
            QMenuBar::separator {
            height: 1px;                /* Height of the separator */
            background: #636161;        /* Color of the separator */
            }
        """)

        # Add menus to the menu bar
        self.menuSignal = QtWidgets.QMenu(self.menubar)
        self.menuSignal.setObjectName("menuSignal")
        self.menuRealTime = QtWidgets.QMenu(self.menubar)
        self.menuRealTime.setObjectName("menuRealTime")
        self.menuNonRectangular = QtWidgets.QMenu(self.menubar)
        self.menuNonRectangular.setObjectName("menuNonRectangular")

        # Add menus to the menubar
        self.menubar.addAction(self.menuSignal.menuAction())
        self.menubar.addAction(self.menuRealTime.menuAction())
        self.menubar.addAction(self.menuNonRectangular.menuAction())

        # Set the menubar to the main window
        MainWindow.setMenuBar(self.menubar)

        # Set the central widget
        MainWindow.setCentralWidget(self.centralwidget)

        # Set text for menus and actions
        self.menuSignal.setTitle("Signal")
        self.menuRealTime.setTitle("Real-Time")
        self.menuNonRectangular.setTitle("Non-Rectangular")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def slider_value_changed(self, value):
        print(f"Slider value: {value}")
        

    def initButtons(self):
        # Button configurations (shifted down by 50 pixels)
        self.Signal1 = self.createButton("Signal", 15, 70)   # Left Signal button with icon
        self.Link = self.createButton("Link Plot", 300, 440, size=(280, 50))  
        self.is_linked = False  # Initial state
        self.Play_stop1 = self.createToggleButton("src/data/Images/Pause.png", "src/data/Images/Play.png", 610, 440, )    # Left Toggle P/S button
        self.Speed1 = self.createSpeedButton(690, 440)       # Left Speed button
        self.ZoomIn1 = self.createButtonWithIcon("src/data/Images/Zoom in.png", 770, 440, )  # Left Zoom In button
        self.ZoomOut1 = self.createButtonWithIcon("src/data/Images/Zoom out.png", 850, 440, ) # Left Zoom Out button
        self.Snapshot1 = self.createButtonWithIcon("src/data/Images/Snapshot.png", 930, 440, )     # Left SS button

      # self.GlueButton = self.createButton("Glue", 1,1)
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
        
        # self.GlueButton = self.createButton("Glue", 1,1)
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
            width: 24px; 
            height: 24px; 
            line-height: 20px; 
            margin-top: -7px; 
            margin-bottom: -7px; 
            border-radius: 12px; 
            }
        """)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self.slider_value_changed)

    
    def load_first_signal(self):
        # Open the file dialog for the first signal
        filename = askopenfilename(title="Select the first signal file",
                                   filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if filename:
            try:
                # Load the data from the first file
                self.x1, self.y1 = self.convert_signal_values_to_numeric(filename)
                print(f"Loaded first signal from {filename}")
            except Exception as e:
                print(f"Error loading first file: {e}")
    def load_second_signal(self):
        # Open the file dialog for the second signal
        filename = askopenfilename(title="Select the second signal file",
                                   filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if filename:
            try:
                # Load the data from the second file
                self.x2, self.y2 = self.convert_signal_values_to_numeric(filename)
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
       button.clicked.connect(lambda: self.toggleSpeed(button))
       button.speeds = [0.25, 0.5, 1, 2, 5, 10, 100]
       button.current_speed_index = button.speeds.index(default_speed)
       return button

    def toggleSpeed(self, button):
       button.current_speed_index = (button.current_speed_index + 1) % len(button.speeds)
       new_speed = button.speeds[button.current_speed_index]
       button.setText(f"{new_speed}x")
       print(f"Speed set to: {new_speed}x")

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
            "    font-size: 16px;                /* Increased font size */\n"  # Increased size
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
    
    def plotRightClicked(self, event):
      if event.button() == QtCore.Qt.RightButton:
        # Display the right-click popup
        right_click_popup = RightClickPopup()
        right_click_popup.exec_()

    
    def initPlots(self):
        # Create two plots using PyQtGraph (shifted 50 pixels down)
        self.Plot1 = pg.PlotWidget(self.centralwidget)
        self.Plot1.setGeometry(QtCore.QRect(180, 70, 800, 350))  # Shifted from 20 to 70
        self.Plot1.setObjectName("Plot1")

        signal1_time_length = len(self.x1)
        signal1_value_length = len(self.y1)
        
        signal2_time_length = len(self.x2)
        signal2_value_length = len(self.y2)
        
        #Set x and y limits (adjust as needed)
        self.Plot1.setXRange(0, signal1_time_length)  # Set x-axis limits from 0 to 10
        self.Plot1.setYRange(0, signal1_value_length)  # Set y-axis limits from 0 to 100
        self.Plot1.setObjectName("Plot1")
        self.Plot1.scene().sigMouseClicked.connect(self.plotRightClicked)  # Connect mouse click to the plot


        # Set axis labels
        self.Plot1.setLabel('bottom', "Time (s)")
        self.Plot1.setLabel('left', "Normal Signal")

        # Increase the y-coordinate for the second plot
        self.Plot2 = pg.PlotWidget(self.centralwidget)
        self.Plot2.setGeometry(QtCore.QRect(180, 530, 800, 350))  # Shifted from 340 to 390
        self.Plot2.setObjectName("Plot2")
        self.Plot2.scene().sigMouseClicked.connect(self.plotRightClicked)  # Connect mouse click to the plot


        # Set x and y limits (adjust as needed)
        self.Plot2.setXRange(0, signal2_time_length)  # Set x-axis limits from 0 to 10
        self.Plot2.setYRange(0, signal2_value_length)  # Set y-axis limits from 0 to 100

        # Set axis labels
        self.Plot2.setLabel('bottom', "Time (s)")
        self.Plot2.setLabel('left', "Abnormal Signal")

        # Mirrored plots
        self.Plot3 = pg.PlotWidget(self.centralwidget)
        self.Plot3.setGeometry(QtCore.QRect(1090, 300, 800, 350))  # Right Plot1
        self.Plot3.setObjectName("Plot3")
        self.Plot3.setObjectName("Plot1")
        self.Plot3.scene().sigMouseClicked.connect(self.plotRightClicked)  # Connect mouse click to the plot

        # Example data for plotting
        self.plotData()

    def plotData(self):
        self.Plot1.enableAutoRange()  # Enable automatic scaling of axes
        self.Plot1.showGrid(x=True, y=True)  # Show grid lines
        
        self.Plot2.enableAutoRange()  # Enable automatic scaling of axes
        self.Plot2.showGrid(x=True, y=True)  # Show grid lines

        self.timer1 = QtCore.QTimer()
        self.timer1.setInterval(150)  # Adjust the interval as needed
        self.timer1.timeout.connect(lambda: self.update_plot(1))  # Connect to update_plot for Plot1
        self.timer1.start()

        self.timer2 = QtCore.QTimer()
        self.timer2.setInterval(150)  # Adjust the interval as needed
        self.timer2.timeout.connect(lambda: self.update_plot(2))  # Connect to update_plot for Plot2
        self.timer2.start()

         # Initialize plot indices separately for each plot
        self.plot_index1 = 0
        self.plot_index2 = 0

    #function responsible for speed
    def toggleSpeed(self, button, plot_id):
       button.speeds = [1.0, 1.5, 2.0,4.0,8.0, 0.25, 0.5] 
       button.current_speed_index = (button.current_speed_index + 1) % len(button.speeds)
       new_speed = button.speeds[button.current_speed_index]
       button.setText(f"{new_speed}x")
       print(f"Speed set to: {new_speed}x")
       self.parent.timers[plot_id].setInterval(int(150 / new_speed))

    def update_plot(self, plot_id):
        # Update the plot with new data points
        if self.play_stop_signals.is_playing(plot_id):  # For Plot1
            if plot_id == 1:
                if self.plot_index1 < len(self.x1):
                    next_x = self.x1[self.plot_index1]
                    next_y = self.y1[self.plot_index1]
                    self.plot_index1 += 1

                    # Calculate the start and end indices for the dynamic time window
                    start_index = max(self.plot_index1 - 200, 0)  # Adjust the window size as needed
                    end_index = self.plot_index1

                    # Update the plot with the dynamic time window
                    self.Plot1.plot(self.x1[start_index:end_index], self.y1[start_index:end_index], pen='r', clear=False)

                    # Set the x-axis limits to match the current time window
                    self.Plot1.setXRange(self.x1[start_index], self.x1[end_index])

                    plt.pause(0.01)  # Adjust the pause time for animation speed
 
        if plot_id == 2 and self.play_stop_signals.is_playing(plot_id):     
            if self.plot_index2 < len(self.x2):
                next_x = self.x2[self.plot_index2]
                next_y = self.y2[self.plot_index2]
                self.plot_index2 += 1
                
                # Calculate the start and end indices for the dynamic time window
                start_index = max(self.plot_index2 - 200, 0)  # Adjust the window size as needed
                end_index = self.plot_index2

                # Update the plot with the dynamic time window
                self.Plot2.plot(self.x2[start_index:end_index], self.y2[start_index:end_index], pen='b', clear=False)

                # Set the x-axis limits to match the current time window
                self.Plot2.setXRange(self.x2[start_index], self.x2[end_index])

                plt.pause(0.01)  # Adjust the pause time for animation speed

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
