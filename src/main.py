import sys 
import os 
from PyQt5 import QtWidgets
from ui.signal_viewer import Ui_MainWindow
from PyQt5.QtWidgets import QFileDialog
from logic.calculate_stats import calculate_statistics
from logic.take_snapshot import take_snapshot
from logic.generate_pdf import generate_pdf

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

        # connect generate pdf button to function ( now it is linked with zoomin1 cause
        # there is no generate pdf button at the moment)
        self.ui.ZoomIn1.clicked.connect(self.generate_pdf)

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
        return [1, 2, 3, 4, 5]  # Dummy data

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