import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Label, Text, END
import random
import time, os, csv, threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
FILE_PATH_SIM = "current_flight_test.csv"
FILE_PATH_IRL = "real_flight_kinda.csv"

class RocketGroundStation:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Rocket Ground Station")
        self.root.geometry("1000x700")
        self.root.configure(bg="#111")

        self.connected = False
        self.running = False
        self.altitude_data = []
        self.time_data = []
        self.start_time = None
        self.csv_file = None
        self.last_position = 0

        # --- UI Layout ---
        self.create_header()
        self.create_telemetry_panel()
        self.create_plot_panel()
        self.create_console()

    def create_header(self):
        frame = tk.Frame(self.root, bg="#222")
        frame.pack(fill="x", pady=10)

        tk.Label(frame, text="Rocket Ground Station", fg="white", bg="#222",
                 font=("Arial", 20, "bold")).pack(side="left", padx=20)

        self.connect_btn = ttk.Button(frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.pack(side="right", padx=10)

    def create_telemetry_panel(self):
        frame = tk.LabelFrame(self.root, text="Telemetry", fg="white", bg="#111",
                              font=("Arial", 14, "bold"), labelanchor="n")
        frame.pack(fill="x", padx=20, pady=10)

        self.telemetry_vars = {
            "Altitude (m)": tk.StringVar(value="0"),
            "Velocity (m/s)": tk.StringVar(value="0"),
            "Temperature (°C)": tk.StringVar(value="0"),
            "Pressure (mbar)": tk.StringVar(value="0"),
            "Acceleration (m/s²)": tk.StringVar(value="0"),
        }

        for i, (label, var) in enumerate(self.telemetry_vars.items()):
            tk.Label(frame, text=label, fg="white", bg="#111", font=("Arial", 12)).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            tk.Label(frame, textvariable=var, fg="#00ff00", bg="#111", font=("Consolas", 12)).grid(row=i, column=1, sticky="w", padx=10)

    def create_plot_panel(self):
        frame = tk.LabelFrame(self.root, text="Altitude Graph", fg="white", bg="#111",
                              font=("Arial", 14, "bold"), labelanchor="n")
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Altitude over Time")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Altitude (m)")
        self.ax.grid(True)

        # Initialize the line object for dynamic updates
        self.line, = self.ax.plot([], [], color="cyan")

        self.canvas = FigureCanvasTkAgg(self.figure, frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_console(self):
        frame = tk.LabelFrame(self.root, text="Console Log", fg="white", bg="#111",
                              font=("Arial", 14, "bold"), labelanchor="n")
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.console = scrolledtext.ScrolledText(frame, height=8, bg="#000", fg="#0f0", insertbackground="white",
                                                 font=("Consolas", 10))
        self.console.pack(fill="both", expand=True)
        self.log("System initialized. Waiting for connection...")

    # --- Core logic ---
    def toggle_connection(self):
        if not self.connected:
            self.connected = True
            self.connect_btn.config(text="Disconnect")
            self.start_time = time.time()
            self.running = True

            # Clear existing data and reset the graph
            self.time_data.clear()
            self.altitude_data.clear()
            self.line.set_data([], [])
            self.ax.set_xlim(left=0)
            self.ax.set_ylim(bottom=0)
            self.canvas.draw()

            self.log("Connected to rocket telemetry system.")
            threading.Thread(target=self.update_telemetry_loop_irl, daemon=True).start()
        else:
            self.connected = False
            self.connect_btn.config(text="Connect")
            self.running = False
            self.log("Disconnected from rocket.")
    
    def update_telemetry_loop_simulation(self):
        last_timestamp = None  # Track the last timestamp from the CSV

        while self.running:
            try:
                with open(FILE_PATH_SIM, 'r') as f:
                    for line in f:
                        if not self.running:
                            break

                        if line.startswith("#"):
                            self.log(line.strip())  # Log comments
                        else:
                            data = line.strip().split(',')
                            try:
                                start_time = time.time()  # Start timing

                                timestamp = float(data[0])  # First column is the timestamp
                                altitude = float(data[1])
                                velocity = float(data[3])
                                temperature = float(data[47])  
                                pressure = float(data[48])      
                                acceleration = float(data[6])

                                # Only update time_data if the timestamp changes
                                if timestamp != last_timestamp:
                                    elapsed = timestamp  # Use the timestamp directly
                                    self.time_data.append(elapsed)
                                    last_timestamp = timestamp

                                self.telemetry_vars["Altitude (m)"].set(f"{altitude:.2f}")
                                self.telemetry_vars["Velocity (m/s)"].set(f"{velocity:.2f}")
                                self.telemetry_vars["Temperature (°C)"].set(f"{temperature:.2f}")
                                self.telemetry_vars["Pressure (mbar)"].set(f"{pressure:.2f}")
                                self.telemetry_vars["Acceleration (m/s²)"].set(f"{acceleration:.2f}")

                                self.altitude_data.append(altitude)

                                # Update the line data instead of clearing the plot
                                self.line.set_data(self.time_data, self.altitude_data)

                                # Adjust the plot limits dynamically
                                self.ax.set_xlim(left=0, right=max(self.time_data) if self.time_data else 1)
                                self.ax.set_ylim(bottom=0, top=max(self.altitude_data) if self.altitude_data else 1)

                                # Redraw the canvas
                                self.canvas.draw()

                                #it takes around 40ms to process each line of the csv file
                            except (ValueError, IndexError) as e:
                                self.log(f"Error processing line: {line.strip()} | {e}")

                time.sleep(0.01)  # Read the file every 0.01 seconds

            except FileNotFoundError:
                self.log(f"File not found: {FILE_PATH_SIM}")
                time.sleep(0.01)
            except Exception as e:
                self.log(f"Unexpected error: {e}")
                time.sleep(0.01)

    def update_telemetry_loop_irl(self):
        last_position = 0  # Track the last read position in the file

        while self.running:
            try:
                if not os.path.exists(FILE_PATH_IRL):
                    time.sleep(0.01)  #if it cannot find a file, it retries after 0.01 sec, this could happen when other process is writing to this file
                    continue

                with open(FILE_PATH_IRL, 'r', encoding='utf-8-sig') as f:
                    f.seek(last_position)

                    for line in f:
                        if not self.running:
                            break

                        if line.startswith("#"):
                            self.log(line.strip())
                        else:
                            data = line.strip().split(',')
                            try:
                                timestamp = float(data[0])
                                altitude = float(data[1])
                                velocity = float(data[2])
                                temperature = float(data[3])  
                                pressure = float(data[4])      
                                acceleration = float(data[5])

                                #Update telemetry variables
                                self.telemetry_vars["Altitude (m)"].set(f"{altitude:.2f}")
                                self.telemetry_vars["Velocity (m/s)"].set(f"{velocity:.2f}")
                                self.telemetry_vars["Temperature (°C)"].set(f"{temperature:.2f}")
                                self.telemetry_vars["Pressure (mbar)"].set(f"{pressure:.2f}")
                                self.telemetry_vars["Acceleration (m/s²)"].set(f"{acceleration:.2f}")

                                #Append data to the plot
                                self.time_data.append(timestamp)
                                self.altitude_data.append(altitude)

                                #Update the line data instead of clearing the plot
                                self.line.set_data(self.time_data, self.altitude_data)

                                #Adjust the plot limits dynamically                                            
                                x_min, x_max = 0, max(self.time_data) if self.time_data else 1
                                y_min, y_max = 0, max(self.altitude_data) if self.altitude_data else 1

                                #fix stupid graph warning
                                if x_min == x_max:
                                    x_min -= 0.1

                                if y_min == y_max:
                                    y_min -= 0.1
                        

                                self.ax.set_xlim(left=x_min, right=x_max)
                                self.ax.set_ylim(bottom=y_min, top=y_max)

                                # Redraw the canvas
                                self.canvas.draw()
                            except (ValueError, IndexError) as e:
                                self.log(f"Error processing line: {line.strip()} | {e}")

                    # Update the last read position
                    last_position = f.tell()

            except FileNotFoundError:
                self.log(f"File not found: {FILE_PATH_IRL}")
                time.sleep(0.1)  # Retry after a short delay
            except Exception as e:
                self.log(f"Unexpected error: {e}")
                time.sleep(0.1)

            time.sleep(0.01)  # Check for updates every 0.01 seconds

    def log(self, message):
        self.console.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.console.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = RocketGroundStation(root)
    root.mainloop()
