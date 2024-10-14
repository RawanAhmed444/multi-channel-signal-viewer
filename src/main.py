import sys 
import os 
from PyQt5 import QtWidgets
from ui.main_window import Ui_MainWindow
from ui.main_window import RightClickPopup
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtCore
from PyQt5.QtCore import QPoint, QTimer
from logic.calculate_stats import calculate_statistics
from logic.take_snapshot import take_snapshot
from logic.generate_pdf import generate_pdf
from logic.move_signals import select_signal, move_selected_signal
from logic.signal_processing import load_signal_from_file
import pandas as pd
import matplotlib.pyplot as plt
from logic.play_stop import PlayStopSignals 
from logic.move_signals import selected_signal
from functools import partial

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.play_stop_signals = PlayStopSignals()
        self.ui = Ui_MainWindow(self.play_stop_signals)
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
            timer.setInterval(150)
            timer.timeout.connect(partial(self.ui.update_plot, plot_id))

        # Connect snapshot buttons to functions
        self.ui.Snapshot1.clicked.connect(lambda: self.take_snapshot(self.ui.Plot1, "Plot1"))
        self.ui.Snapshot2.clicked.connect(lambda: self.take_snapshot(self.ui.Plot2, "Plot2"))
        self.ui.Snapshot3.clicked.connect(lambda: self.take_snapshot(self.ui.Plot3, "Plot3"))
        self.ui.Snapshot4.clicked.connect(lambda: self.take_snapshot(self.ui.Plot4, "Plot4"))

        # Connect buttons to the same toggle function
        self.ui.Play_stop1.clicked.connect(lambda: self.toggle_play_stop(1))
        self.ui.Play_stop2.clicked.connect(lambda: self.toggle_play_stop(2))

        
        # self.update_timers()

        #connect report button to generate the pdf
        self.ui.Report.clicked.connect(self.generate_pdf)

        self.ui.Speed1.clicked.connect(lambda: self.ui.toggleSpeed(self.ui.Speed1, 1))
        self.ui.Speed2.clicked.connect(lambda: self.ui.toggleSpeed(self.ui.Speed2, 2))

        # Connect plots to select signal
        self.ui.Plot1.scene().sigMouseClicked.connect(lambda event: self.on_plot_click(event, self.ui.Plot1))
        self.ui.Plot2.scene().sigMouseClicked.connect(lambda event: self.on_plot_click(event, self.ui.Plot2))

        self.selected_signal = None
        self.selected_signal_timer = None

    # def update_plot(self,plot_id):
    #     self.ui.update_plot(plot_id)

    def on_plot_click(self, event, plot_widget):
        items = plot_widget.listDataItems()
        if items:
            # select a signal from the many signals being displayed on the plot
            for signal in items:
                select_signal(plot_widget, signal)

            x_data, y_data = self.get_plot_data(plot_widget)
            source_plot = self.ui.Plot1 if selected_signal in self.ui.Plot1.listDataItems() else self.ui.Plot2

        if event.button() == QtCore.Qt.RightButton:

            target_plot = self.ui.Plot2 if source_plot == self.ui.Plot1 else self.ui.Plot1

            #pass selected signal data to the context menu
            context_menu = RightClickPopup(
            parent=self,
            selected_signal_data=y_data,
            source_plot=source_plot,
            target_plot=target_plot,
            source_timer=self.timers[1] if source_plot == self.ui.Plot1 else self.timers[2],
            target_timer=self.timers[2] if target_plot == self.ui.Plot2 else self.timers[1],
            move_signal=self.move_signals
        )
            context_menu.exec_(QPoint(int(event.screenPos().x()), int(event.screenPos().y()))) #show the menu at the mouse position 

    # linking this to take_snapshot file
    def take_snapshot(self, plot_widget, plot_name):
        data = self.get_plot_data(plot_widget)  
        stats = calculate_statistics(data)     
        snapshot_path = take_snapshot(plot_widget, plot_name=plot_name) 

        # Store snapshot and statistics
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
    
    # function responsible for play_pause 
    def control_plot(self, plot_id, start):
        if start:
            self.timers[plot_id].start()
            print(f"Plot {plot_id} started.")
        else:
            self.timers[plot_id].stop()
            print(f"Plot {plot_id} stopped.")

    # function responsible for play_pause and speed
    # def update_timers(self):
    #     for plot_id in self.timers:
    #         if self.play_stop_signals.is_playing(plot_id):
    #             self.timers[plot_id].start()

    def move_signals(self, source_plot, target_plot, source_timer, target_timer):
        move_selected_signal(source_plot, target_plot, source_timer, target_timer)

    def get_plot_data(self, plot_widget):
        items = plot_widget.listDataItems()
        full_y_data = []
        x_data = None
        print("Number of items in plot:", len(items))  # Debugging line

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

