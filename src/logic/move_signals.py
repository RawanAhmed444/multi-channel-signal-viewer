import pyqtgraph as pg 

selected_signal = None

def select_signal(plot , signal):

    global selected_signal
    selected_signal = signal

    print("some siganl was selected")
    print(f"signal selected on plot{plot.objectName()}")

# def get_selected_signal_data(signal):
#     global select_signal
#     if isinstance(selected_signal, pg.PlotDataItem):
#         x_data, y_data = signal.getData()
#         return x_data, y_data
#     else:
#         return None, None

def move_selected_signal(source_plot, target_plot):

    global selected_signal
    if selected_signal is None:
        print("No signal selected")
        return
    
    x_data, y_data = selected_signal.getData()
    pen = selected_signal.opts['pen'] 

    new_signal = pg.PlotDataItem(x_data, y_data, pen=pen)
    target_plot.addItem(new_signal)
    
    target_plot.plot(x_data, y_data, pen=pen)
    source_plot.removeItem(selected_signal)

    print(f"signal moved from {source_plot.objectName()} to {target_plot.objectName()}")

    selected_signal = None
