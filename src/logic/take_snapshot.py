import os 
import pyqtgraph as pg
from pyqtgraph import exporters 

def take_snapshot(plot_widget, snapshot_folder="snapshots", plot_name="Plot"):
    if not os.path.exists(snapshot_folder):
        os.makedirs(snapshot_folder)

    snapshot_path = os.path.join(snapshot_folder, f"{plot_name}_snapshot_{len(os.listdir(snapshot_folder))}.png")
    exporter = pg.exporters.ImageExporter(plot_widget.plotItem)
    
    # Save the image to the specified path instead of a buffer
    exporter.export(snapshot_path)

    return snapshot_path  # Return the path of the saved snapshot

