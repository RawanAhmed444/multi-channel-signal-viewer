import pyqtgraph as pg 

selected_signal = None
selected_signal_timer = None

def select_signal(plot , signal):

    global selected_signal
    selected_signal = signal

    print("some siganl was selected")
    print(f"signal selected on plot{plot.objectName()}")

def move_selected_signal(source_plot, target_plot, source_timer, target_timer):

    global selected_signal, selected_signal_timer

    if selected_signal is None:
        print("No signal selected")
        return
    
    x_data, y_data = selected_signal.getData()
    pen = selected_signal.opts['pen'] 

    source_plot.removeItem(selected_signal)

    new_signal = pg.PlotDataItem(x_data, y_data, pen=pen)
    target_plot.addItem(new_signal)

    if not target_timer.isActive():
        target_timer.start()


    if len(source_plot.listDataItems()) == 0: 
        if source_timer.isActive():
            source_timer.stop()

    print(f"signal moved from {source_plot.objectName()} to {target_plot.objectName()}")

    selected_signal = None
