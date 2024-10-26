class PlayStopSignals:
    def __init__(self):
        self.plot_states = {
            1: True,  # Plot1 initially running
            2: True,  # Plot2 initially running
        }

    def start_signals(self):
        for plot_id in self.plot_states:
            self.plot_states[plot_id] = True 

    def is_playing(self, plot_id):
        return self.plot_states.get(plot_id, False)

    def start_signal(self, plot_id):
        self.plot_states[plot_id] = True
        print(f"Plot {plot_id} started.")

    def stop_signal(self, plot_id):
        self.plot_states[plot_id] = False
        print(f"Plot {plot_id} stopped.")
