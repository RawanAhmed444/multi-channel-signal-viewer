import pyqtgraph as pg 

selected_signal = None

def select_signal(plot, signal):
    global selected_signal
    selected_signal = signal
    print("Some signal was selected")
    print(f"Signal selected on plot {plot.objectName()}")

def move_selected_signal(source_plot, target_plot, source_timer, target_timer):
    print("you are now in move_signals.py")
    global selected_signal

    if selected_signal is None:
        print("No signal selected")
        return

        print(f"Attempting to move signal from {source_plot.objectName()} to {target_plot.objectName()}")

    # Check the current items in the source and target plots
    print("Current items in source plot before moving:", source_plot.listDataItems())
    print("Current items in target plot before moving:", target_plot.listDataItems())


    # Get the full history of the signal (x and y data)
    x_data, y_data = selected_signal.getData()
    print(f"Moving signal with x_data: {x_data} and y_data: {y_data}")
    pen = selected_signal.opts['pen'] 

    # Remove the signal from the source plot
    source_plot.removeItem(selected_signal)

    # Add the signal to the target plot, with the same historical data
    new_signal = pg.PlotDataItem(x_data, y_data, pen=pen)
    target_plot.addItem(new_signal)

    # Ensure the target plot timer is active to keep the signal running
    if not target_timer.isActive():
        target_timer.start()

    # Stop the source plot's timer if no more signals are running on it
    if len(source_plot.listDataItems()) == 0: 
        if source_timer.isActive():
            source_timer.stop()

    print(f"Signal moved from {source_plot.objectName()} to {target_plot.objectName()}")
     # Check the items in the source and target plots after moving
    print("Current items in source plot after moving:", source_plot.listDataItems())
    print("Current items in target plot after moving:", target_plot.listDataItems())

    # Reset the selected signal
    selected_signal = None

# import pyqtgraph as pg 

# selected_signal = None
# # selected_signal_timer = None

# def select_signal(plot, signal):

#     global selected_signal
#     selected_signal = signal

#     print("some siganl was selected")
#     print(f"signal selected on plot{plot.objectName()}")

# def move_selected_signal(source_plot, target_plot, source_timer, target_timer):

#     global selected_signal

#     if selected_signal is None:
#         print("No signal selected")
#         return

#     # Get the full history of the signal (x and y data)
#     x_data, y_data = selected_signal.getData()
#     pen = selected_signal.opts['pen'] 

#     # Remove the signal from the source plot
#     source_plot.removeItem(selected_signal)

#     # Add the signal to the target plot, with the same historical data
#     new_signal = pg.PlotDataItem(x_data, y_data, pen=pen)
#     target_plot.addItem(new_signal)

#     # Ensure the target plot timer is active to keep the signal running
#     if not target_timer.isActive():
#         target_timer.start()

#     # Stop the source plot's timer if no more signals are running on it
#     if len(source_plot.listDataItems()) == 0: 
#         if source_timer.isActive():
#             source_timer.stop()

#     print(f"signal moved from {source_plot.objectName()} to {target_plot.objectName()}")

#     selected_signal = None
