import pyqtgraph as pg 

selected_signal = None

def select_signal(plot, signal):
    global selected_signal
    selected_signal = signal
    print("Some signal was selected")
    print(f"Signal selected on plot {plot.objectName()}")

def move_signal_between_plots(ui_instance, moving_x, moving_y, target_plot_id, source_timer, source_plot_id):
    print(f"Moving signal to Plot {target_plot_id}") 

    source_timer.stop()
    # Remove the signal from the source plot
    if source_plot_id == 1:
        ui_instance.x1 = []  # Clear the data for Plot1
    elif source_plot_id == 2:
        ui_instance.x2 = []  # Clear the data for Plot2


    # Append the signal to the target plot
    if target_plot_id == 1:
        ui_instance.x1.extend(moving_x)  # Append the moving signal to existing signals
        ui_instance.y1.extend(moving_y)
        print(f"Appended data to Plot1: {len(ui_instance.x1)} points now") 
        ui_instance.ui.Plot1.clear() 
        ui_instance.ui.Plot1.plot(ui_instance.x1, ui_instance.y1)
    elif target_plot_id == 2:
        ui_instance.x2.extend(moving_x)
        ui_instance.y2.extend(moving_y)
        print(f"Appended data to Plot2: {len(ui_instance.x2)} points now")  
        ui_instance.ui.Plot2.clear()
        ui_instance.ui.Plot2.plot(ui_instance.x2, ui_instance.y2)

    # Update the plot indices to reset and avoid index errors
    ui_instance.plot_index1 = 0
    ui_instance.plot_index2 = 0

