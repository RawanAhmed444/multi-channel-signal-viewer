import sys 
import os 
from PyQt5 import QtWidgets
from ui.main_window import Ui_MainWindow
from PyQt5.QtWidgets import QFileDialog
from logic.calculate_stats import calculate_statistics
from logic.take_snapshot import take_snapshot
from logic.generate_pdf import generate_pdf
from logic.move_signals import select_signal, move_selected_signal

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #list to store snapshots and statistics
        self.snapshots = []
        self.statistics_data = []

        # Connect snapshot buttons to functions
        self.ui.Snapshot1.clicked.connect(lambda: self.take_snapshot(self.ui.Plot1, "Plot1"))
        self.ui.Snapshot2.clicked.connect(lambda: self.take_snapshot(self.ui.Plot2, "Plot2"))
        self.ui.Snapshot3.clicked.connect(lambda: self.take_snapshot(self.ui.Plot3, "Plot3"))
        self.ui.Snapshot4.clicked.connect(lambda: self.take_snapshot(self.ui.Plot4, "Plot4"))

        # connect move buttons to function
        # self.ui.Move1.clicked.connect(lambda: self.move_signal(self.ui.Plot1, self.ui.Plot2))
        # self.ui.Move2.clicked.connect(lambda: self.move_signal(self.ui.Plot2, self.ui.Plot1))

        # connect generate pdf button to function ( now it is linked with zoomin1 cause
        # there is no generate pdf button at the moment)
        self.ui.Report.clicked.connect(self.generate_pdf)

        # Connect plots to select signal
        self.ui.Plot1.scene().sigMouseClicked.connect(lambda event: self.on_plot_click(event, self.ui.Plot1))
        self.ui.Plot2.scene().sigMouseClicked.connect(lambda event: self.on_plot_click(event, self.ui.Plot2))

    def on_plot_click(self, event, plot_widget):
        items = plot_widget.listDataItems()
        if items:
            signal = items[0]
            select_signal(plot_widget, signal)
    
    def move_signal(self, source_plot, target_plot):
        move_selected_signal(source_plot, target_plot)

    # linking this to take_snapshot file
    def take_snapshot(self, plot_widget, plot_name):
        data = self.get_plot_data(plot_widget)  
        stats = calculate_statistics(data)     
        snapshot_path = take_snapshot(plot_widget, plot_name=plot_name) 

        # Store snapshot and statistics
        self.snapshots.append(snapshot_path)
        self.statistics_data.append(stats)

    #this would be changed
    def get_plot_data(self, plot_widget):
        items = plot_widget.listDataItems()
        if items:
            signal = items[0]  
            x_data, y_data = signal.getData()
            return y_data
        return None

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

