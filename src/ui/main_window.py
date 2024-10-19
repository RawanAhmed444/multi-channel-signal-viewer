import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QPoint
import pyqtgraph as pg
from pyqtgraph import PlotDataItem
from logic.signal_processing import load_signal_from_file
import pandas as pd
import matplotlib.pyplot as plt
from logic.calculate_stats import calculate_statistics
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QGraphicsView
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from scipy import interpolate
from scipy.interpolate import interp1d

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
    def __init__(self, parent=None, selected_signal_data=None, main_window = None):
        super(RightClickPopup, self).__init__(parent)
        self.selected_signal_data = selected_signal_data
        self.main_window = main_window 
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
        self.addAction("Name", self.hide)
        self.addSeparator()
        self.addAction("Color", self.hide)
        self.addSeparator()
        self.addAction("Hide", self.hide)
        self.addSeparator()
        self.addAction("Swap" , self.swap_signals)
        self.addSeparator()
        self.addAction("Statistics", self.show_statistics)
       
    def show_statistics(self):
            self.hide()
            selected_signal_stats = calculate_statistics(self.selected_signal_data)
            stats_popup = StatisticsPopup()
            stats_popup.display_statistics(selected_signal_stats)
            stats_popup.exec_()
            self.close() 

    def swap_signals(self):
        """Swap the signals between Plot1 and Plot2"""
        self.hide()
        if self.main_window:
            self.main_window.swap_signals_between_plots()
        self.close()
  
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
    
    def __init__(self, play_stop_signals, parent=None):
        super().__init__()
        self.play_stop_signals = play_stop_signals
        self.plot_index = 0  
        self.parent = parent
        self.rois = []  
        self.region_count = 0
        self.x1, self.y1 = [0], [0]
        self.x2, self.y2 = [0], [0]
        self.segment1 = None  
        self.segment2 = None  
        self.last_interpolation_curve = None
        self.selected_signal_data = None

        self.timer1 = QtCore.QTimer()
        self.timer1.setInterval(150) 
        self.timer1.timeout.connect(lambda: self.update_plot(1))  

        self.timer2 = QtCore.QTimer()
        self.timer2.setInterval(150)  
        self.timer2.timeout.connect(lambda: self.update_plot(2))  

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
        self.slider.setMinimum(-2)
        self.slider.setMaximum(4)
        self.slider.setValue(2)

        # Connect the slider value change to the corresponding function
        self.slider.valueChanged.connect(self.update_distance)

        self.radioLinear.toggled.connect(self.perform_interpolation)
        self.radioQuadratic.toggled.connect(self.perform_interpolation)
        self.radioCubic.toggled.connect(self.perform_interpolation)

    
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

    def update_distance(self, value):

        distance = value 

        if hasattr(self, 'segments') and len(self.segments) == 2:
            segment1 = self.segments[0]
            segment2 = self.segments[1]

            x1_min, x1_max, plot = segment1  
            x2_min, x2_max, _ = segment2  

            # Update the second segment's minimum x value based on the distance
            new_x2_min = x1_max + distance  
            new_x2_max = new_x2_min + (x2_max - x2_min)
            new_x2_min = max(new_x2_min, x1_min - 1) 
            new_x2_max = new_x2_min + (x2_max - x2_min) 

            self.segments[1] = (new_x2_min, new_x2_max, plot)
            self.plot_selected_regions_on_plot3()

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
            main_window=self
        )
            context_menu.exec_(QPoint(int(event.screenPos().x()), int(event.screenPos().y()))) #show the menu at the mouse position 


    def select_region(self, plot, event):
        mouse_point = plot.getViewBox().mapSceneToView(event.scenePos())
        x_pos = mouse_point.x()

        if not hasattr(self, 'region_start'):
            # First left-click: Start region selection
            self.region_start = x_pos
            self.selection_rect = pg.LinearRegionItem([self.region_start, self.region_start], pen='b', brush=(100, 100, 255, 50))  # Light blue box
            plot.addItem(self.selection_rect)
        else:
            # Second left-click: End region selection
            self.region_end = x_pos
            self.selection_rect.setRegion([self.region_start, self.region_end])

            if not hasattr(self, 'segments'):
                self.segments = [] 

            # Store the new segment
            self.segments.append((self.region_start, self.region_end, plot))  # Store the source plot

            # Plot all selected segments on Plot3
            self.plot_selected_regions_on_plot3()

            # Remove the selection rectangle after plotting
            plot.removeItem(self.selection_rect)

            # Reset the region selection for the next region
            del self.region_start, self.region_end

    def plot_selected_regions_on_plot3(self):

        self.Plot3.clear()

        if hasattr(self, 'segments'):
            for segment in self.segments:
                self.plot_selected_region(segment) 

            self.perform_interpolation()

    def plot_selected_region(self, segment):
        if segment is None:
            return 

        x_min, x_max, source_plot = segment 
        x_data = self.x1 if source_plot == self.Plot1 else self.x2
        y_data = self.y1 if source_plot == self.Plot1 else self.y2

        # Get indices for the selected region, ensuring they are within bounds
        start_index = max(0, (np.abs(np.array(x_data) - x_min)).argmin())
        end_index = min(len(x_data) - 1, (np.abs(np.array(x_data) - x_max)).argmin() + 1)

        # Extract data points for the selected region
        selected_x = x_data[start_index:end_index]
        selected_y = y_data[start_index:end_index]

        # Plot the selected region on Plot3
        self.Plot3.plot(selected_x, selected_y, pen='b')  # Plot selected segment in blue

        #  # Check for overlap with the previously plotted segments
        # overlap = False
        # for existing_segment in self.segments:
        #     existing_x_min, existing_x_max, _ = existing_segment
        #     if not (x_max < existing_x_min or x_min > existing_x_max):  # Check for overlap
        #         print("overlap happened")
        #         overlap = True
        #         break

        # # Plot the selected region on Plot3 with different styles based on overlap
        # if overlap:
        #     # Use a different color (like a light blue) for overlapping segments
        #     self.Plot3.plot(selected_x, selected_y, pen='b', brush=(100, 100, 255, 150))  # Light blue box for overlap
        # else:
        #     # Normal color for non-overlapping segments
        #     self.Plot3.plot(selected_x, selected_y, pen='b')  # Plot selected segment in blue

    def perform_interpolation(self):
        if self.last_interpolation_curve is not None:
            self.Plot3.removeItem(self.last_interpolation_curve)
        if len(self.segments) == 2:
            segment1, segment2 = self.segments
            x1_min, x1_max, plot = segment1  
            x2_min, x2_max, _ = segment2  

            x_values = [x1_max, x2_min]  # Last point of the first segment and first point of the second segment

            # Get y values corresponding to x values
            y_values = [
                self.get_y_value_for_x(self.x1 if plot == self.Plot1 else self.x2,
                                        self.y1 if plot == self.Plot1 else self.y2, x1_max),  # Last point of first segment
                self.get_y_value_for_x(self.x1 if plot == self.Plot1 else self.x2,
                                        self.y1 if plot == self.Plot1 else self.y2, x2_min)   # First point of second segment
            ]

            # Determine the interpolation type
            if self.radioLinear.isChecked():
                x_interp = np.linspace(x1_max, x2_min, num=100) 
                y_interp = np.interp(x_interp, x_values, y_values)

            elif self.radioQuadratic.isChecked():
                if len(x_values) >= 3:
                    coeffs = np.polyfit(x_values[:3], y_values + [self.get_y_value_for_x(self.x1 if plot1 == self.Plot1 else self.x2,
                                                                                        self.y1 if plot1 == self.Plot1 else self.y2, x2_min)], 2)
                else:
                    coeffs = np.polyfit(x_values, y_values, 2)
                poly_func = np.poly1d(coeffs)
                x_interp = np.linspace(min(x_values), max(x_values), num=100)
                y_interp = poly_func(x_interp)

            elif self.radioCubic.isChecked():
                if len(x_values) == 4:
                    coeffs = np.polyfit(x_values, y_values, 3)
                else:
                    coeffs = np.polyfit(x_values, y_values, 2) 
                poly_func = np.poly1d(coeffs)
                x_interp = np.linspace(min(x_values), max(x_values), num=100)
                y_interp = poly_func(x_interp)
            
            self.last_interpolation_curve = self.Plot3.plot(x_interp, y_interp, pen='r') 

    def get_y_value_for_x(self, x_data, y_data, x_value):
        
        idx = (np.abs(np.array(x_data) - x_value)).argmin()
        return y_data[idx]

    def swap_signals_between_plots(self):
    
        # Store current indices before the swap
        current_index1 = self.plot_index1
        current_index2 = self.plot_index2

        # Swap x and y data of the plots
        self.x1, self.x2 = self.x2, self.x1
        self.y1, self.y2 = self.y2, self.y1

        self.Plot1.clear()
        self.Plot2.clear()

        # Set the x-axis limits to match the current positions after swap
        self.Plot1.setXRange(self.x1[0], self.x1[min(current_index1, len(self.x1) - 1)])
        self.Plot2.setXRange(self.x2[0], self.x2[min(current_index2, len(self.x2) - 1)])

        # Plot the swapped signals starting from their current indices
        if current_index1 < len(self.x1):
            self.Plot1.plot(self.x1[current_index1:], self.y1[current_index1:], pen='r', clear=False)
        if current_index2 < len(self.x2):
            self.Plot2.plot(self.x2[current_index2:], self.y2[current_index2:], pen='b', clear=False)

        print("Signals swapped between Plot1 and Plot2")
    
    def initPlots(self):
        self.Plot1 = pg.PlotWidget(self.centralwidget)
        self.Plot1.setGeometry(QtCore.QRect(180, 70, 800, 350)) 
        self.Plot1.setObjectName("Plot1")

        signal1_time_length = len(self.x1)
        signal1_value_length = len(self.y1)
        
        signal2_time_length = len(self.x2)
        signal2_value_length = len(self.y2)
        
        self.Plot1.setXRange(0, signal1_time_length)  # Set x-axis limits from 0 to 10
        self.Plot1.setYRange(0, signal1_value_length)  # Set y-axis limits from 0 to 100
        self.Plot1.setObjectName("Plot1")
        self.Plot1.scene().sigMouseClicked.connect(lambda event: self.plotRightClicked(event, self.Plot1))  # Connect mouse click to the plot

        # Set axis labels
        self.Plot1.setLabel('bottom', "Time (s)")
        self.Plot1.setLabel('left', "Normal Signal")

        self.Plot2 = pg.PlotWidget(self.centralwidget)
        self.Plot2.setGeometry(QtCore.QRect(180, 530, 800, 350))
        self.Plot2.setObjectName("Plot2")
        self.Plot2.scene().sigMouseClicked.connect(lambda event: self.plotRightClicked(event, self.Plot2))  # Connect mouse click to the plot

        self.Plot2.setXRange(0, signal2_time_length)  # Set x-axis limits from 0 to 10
        self.Plot2.setYRange(0, signal2_value_length)  # Set y-axis limits from 0 to 100

        # Set axis labels
        self.Plot2.setLabel('bottom', "Time (s)")
        self.Plot2.setLabel('left', "Abnormal Signal")

        # Mirrored plots
        self.Plot3 = pg.PlotWidget(self.centralwidget)
        self.Plot3.setGeometry(QtCore.QRect(1090, 300, 800, 350))  # Right Plot1
        self.Plot3.setObjectName("Plot3")
        self.Plot3.scene().sigMouseClicked.connect(lambda event: self.plotRightClicked(event, self.Plot3))  # Connect mouse click to the plot

        # Example data for plotting
        self.plotData()

    def plotData(self):
        self.Plot1.enableAutoRange()  # Enable automatic scaling of axes
        self.Plot1.showGrid(x=True, y=True)  # Show grid lines
        
        self.Plot2.enableAutoRange()  # Enable automatic scaling of axes
        self.Plot2.showGrid(x=True, y=True)  # Show grid lines

        self.timer1.start()
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
           

    def update_plot(self, plot_id):
        if plot_id == 1 and self.play_stop_signals.is_playing(plot_id):
                if self.plot_index1 < len(self.x1):
                    # next_x = self.x1[self.plot_index1]
                    # next_y = self.y1[self.plot_index1]

                    # Calculate the start and end indices for the dynamic time window
                    start_index = max(self.plot_index1 - 200, 0) 
                    end_index = self.plot_index1

                    # Update the plot with the dynamic time window
                    self.Plot1.plot(self.x1[start_index:end_index], self.y1[start_index:end_index], pen='r', clear=False)
                    self.plot_index1 += 1

                    # Set the x-axis limits to match the current time window
                    self.Plot1.setXRange(self.x1[start_index], self.x1[end_index])

                    plt.pause(0.01)
 
        if plot_id == 2 and self.play_stop_signals.is_playing(plot_id):     
                if self.plot_index2 < len(self.x2):
                    # next_x = self.x2[self.plot_index2]
                    # next_y = self.y2[self.plot_index2]
                    
                    # Calculate the start and end indices for the dynamic time window
                    start_index = max(self.plot_index2 - 200, 0)  
                    end_index = self.plot_index2

                    # Update the plot with the dynamic time window
                    self.Plot2.plot(self.x2[start_index:end_index], self.y2[start_index:end_index], pen='b', clear=False)
                    self.plot_index2 += 1

                    # Set the x-axis limits to match the current time window
                    self.Plot2.setXRange(self.x2[start_index], self.x2[end_index])

                    plt.pause(0.01) 


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
