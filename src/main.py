import sys 
import os 
import numpy as np
from PyQt5 import QtWidgets
from ui.main_window import Ui_MainWindow
from ui.main_window import RightClickPopup
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtCore
from PyQt5.QtCore import QPoint, QTimer
from logic.calculate_stats import calculate_statistics
from logic.take_snapshot import take_snapshot
from logic.generate_pdf import generate_pdf
from logic.move_signals import select_signal,  move_signal_between_plots
from logic.signal_processing import load_signal_from_file
import pandas as pd
import matplotlib.pyplot as plt
from logic.play_stop import PlayStopSignals 
from logic.move_signals import selected_signal

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.play_stop_signals = PlayStopSignals()
        self.ui = Ui_MainWindow(self.play_stop_signals,self)
        self.ui.setupUi(self)

        #list to store snapshots and statistics
        self.snapshots = []
        self.statistics_data = []

        # Initialize the timers for plot updates
        self.timers = {
            1: QtCore.QTimer(),
            2: QtCore.QTimer()
        }

        for plot_id, timer in self.timers.items():
            timer.setInterval(100)
            timer.timeout.connect(lambda plot_id=plot_id: self.ui.update_plot(plot_id))

        # Connect snapshot buttons to functions
        self.ui.Snapshot1.clicked.connect(lambda: self.take_snapshot(self.ui.Plot1, "Plot1"))
        self.ui.Snapshot2.clicked.connect(lambda: self.take_snapshot(self.ui.Plot2, "Plot2"))
        self.ui.Snapshot3.clicked.connect(lambda: self.take_snapshot(self.ui.Plot3, "Plot3"))
     

        # Connect buttons to the same toggle function
        self.ui.Play_stop1.clicked.connect(lambda: self.toggle_play_stop(1))
        self.ui.Play_stop2.clicked.connect(lambda: self.toggle_play_stop(2))

        self.update_timers()

        #connect report button to generate the pdf
        self.ui.Report.clicked.connect(self.generate_pdf)

        self.ui.Speed1.clicked.connect(lambda: self.ui.toggleSpeed(self.ui.Speed1, 1))
        self.ui.Speed2.clicked.connect(lambda: self.ui.toggleSpeed(self.ui.Speed2, 2))

        # Connect plots to select signal
        self.ui.Plot1.scene().sigMouseClicked.connect(lambda event: self.ui.on_plot_click(event, self.ui.Plot1))
        self.ui.Plot2.scene().sigMouseClicked.connect(lambda event: self.ui.on_plot_click(event, self.ui.Plot2))
        
        self.selected_signal_data = None
        self.selected_signal = None
        self.selected_signal_timer = None

    
    # linking this to take_snapshot file
    def take_snapshot(self, plot_widget, plot_name):
        # Get the data from the plot widget
        x_data, full_y_data = self.get_plot_data(plot_widget)

         # Check if full_y_data is empty
        if len(full_y_data) == 0:
            print("Warning: full_y_data is empty.")
        else:
            # Calculate statistics using only the full_y_data
            stats = calculate_statistics(full_y_data)  # Use full_y_data for statistics

            # Print calculated statistics for debugging
            print(f"Calculated statistics for {plot_name}: {stats}")

        # Take a snapshot and get the path
        snapshot_path = take_snapshot(plot_widget, plot_name=plot_name) 

        # Store snapshot path and statistics
        self.snapshots.append(snapshot_path)
        self.statistics_data.append(stats)

    # function responsible for play_pause 
    def toggle_play_stop(self, plot_id):
        if self.play_stop_signals.is_playing(plot_id):
            self.play_stop_signals.stop_signal(plot_id)
            self.control_plot(plot_id, start=False)  
        else:
            self.play_stop_signals.start_signal(plot_id)
            self.control_plot(plot_id, start=True) 
    
    # function responsible for play_pause and speed
    def control_plot(self, plot_id, start):
        if start:
            self.timers[plot_id].start()
            print(f"Plot {plot_id} started.")
        else:
            self.timers[plot_id].stop()
            print(f"Plot {plot_id} stopped.")

    # function responsible for play_pause and speed
    def update_timers(self):
        for plot_id in self.timers:
            if self.play_stop_signals.is_playing(plot_id):
                self.timers[plot_id].start()

    def get_plot_data(self, plot_widget):
        items = plot_widget.listDataItems()
        full_y_data = []
        x_data = None
        print("Number of items in plot:", len(items))   

        if items:
            for signal in items: 
                x_data, y_data = signal.getData()
                full_y_data.extend(y_data)
        return x_data, full_y_data
        
    # linking this to generate_pdf file
    def generate_pdf(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(None, "Save PDF", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        if file_name:
            generate_pdf(self.snapshots, self.statistics_data, file_name)
            for snapshot in self.snapshots:
                os.remove(snapshot)
            self.snapshots.clear()
            self.statistics_data.clear()
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())