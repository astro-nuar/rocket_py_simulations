import matplotlib.pyplot as plt
import numpy as np
from rocketpy import Environment, SolidMotor, Rocket, Flight
from my_flight_plots import _MyFlightPlots
import json
from load_flight_from_json import load_flight_from_json
from rocketpy import EnvironmentAnalysis
from datetime import datetime
import sys
import pandas as pd

config_path = "rocket.json"
config_sensor = "sensors.json"

li = []

def main():
    global m
    SHOW_ENVIORMENT = False
    SHOW_ROCKET_INFO = False
    SHOW_FLIGHT_INFO = False
    SHOW_SENSORS = True

    # Load everything from JSON
    env, motor, rocket, flight, three_axis_sensors, baro, gps = load_flight_from_json(config_path, config_sensor)
    
    """
    This can be usefull to analys a lot of weather condfition in a span of like 20 years!!
    env_analysis = EnvironmentAnalysis(
        start_date=datetime(2002, 10, 6),  # (Year, Month, Day)
        end_date=datetime(2021, 10, 23),  # (Year, Month, Day)
        start_hour=4,
        end_hour=20,
        latitude=39.3897,
        longitude=-8.28896388889,
        surface_data_file=".\specifications\Weather\2b29223b65cdda8d6ace1f38854fb13f\data_stream-oper_stepType-instant.nc",
        pressure_level_data_file=".\specifications\Weather\2b29223b65cdda8d6ace1f38854fb13f\data_stream-oper_stepType-instant.ncc",
        timezone="Portugal",
        unit_system="metric",
    env_analysis.all_info()
    )"""

    flight_info = _MyFlightPlots(flight, motor)

    with open(r".\\Simulation\\Pro98M1450.txt", 'w+', encoding='utf-8') as file:
        
        li.append( ( flight_info.motor_tradeoff_json["Max Z (m) - Altitude"]) ) 

        #for k, v in flight_info.motor_tradeoff_json.items():
        #    file.write(f"{k}, {v}\n")
        #    print(f"{k}, {v}\n")

    if SHOW_FLIGHT_INFO:
        flight_info.all()
        
    if SHOW_ROCKET_INFO:
        rocket.all_info()
    
    if SHOW_ENVIORMENT:
        env.plots.atmospheric_model()
    
    if SHOW_SENSORS:
        i = 0
        for sensor in three_axis_sensors:

            t, mx, my, mz = zip(*sensor.measured_data)

            _, ax = plt.subplots(nrows=1, ncols=3)
            
            ax[0].plot(t, mx, label="lat")
            ax[0].set_xlabel("Time (s)")
            ax[0].set_ylabel("Measurement x")

            ax[1].plot(t, my, label="lon")
            ax[1].set_xlabel("Time (s)")
            ax[1].set_ylabel("Measurement y")
            
            ax[2].plot(t, mz, label="altitude")
            ax[2].set_xlabel("Time (s)")        
            ax[2].set_ylabel("Measurement z")

            plt.title(type(sensor).__name__)
            plt.legend()
            plt.show()

            sensor.export_measured_data(f"sensors_data\\exported_{type(sensor).__name__}_{i}_data.csv")
            i+=1

        time_barometer, pressure_barometer = zip(*baro.measured_data)

        plt.plot(time_barometer, pressure_barometer)
        plt.xlabel("Time (s)")
        plt.ylabel("Measurements")
        plt.title(type(baro).__name__)
        plt.show()

        baro.export_measured_data(f"sensors_data\\exported_{type(baro).__name__}_data.csv")

        time_gps, lat, lon, h  = zip(*gps.measured_data)

        _, ax = plt.subplots(nrows=1, ncols=3)
        
        ax[0].plot(time_gps, lat, label="lat")
        ax[0].set_xlabel("Time (s)")
        ax[0].set_ylabel("Lat")

        ax[1].plot(time_gps, lon, label="lon")
        ax[1].set_xlabel("Time (s)")
        ax[1].set_ylabel("Lon")
        
        ax[2].plot(time_gps, h, label="altitude")
        ax[2].set_xlabel("Time (s)")        
        ax[2].set_ylabel("Altitude (m)")

        plt.title("GPS Position")
        plt.legend()
        plt.show()

        gps.export_measured_data(f"sensors_data\\exported_{type(gps).__name__}_data.csv")

main()

'''
for m in np.arange(18.33, 20.5, 0.01):


def run_simulation(m):
    """
    Updates rocket mass in config file, runs simulation,
    and returns apogee.
    """
    # Load config
    with open(config_path, "r") as f:
        config = json.load(f)

    # Update mass
    config["rocket"]["mass"] = m

    # Save config
    with open(config_path, "w") as f:
        json.dump(config, f)

    # Run simulation
    env, motor, rocket, flight = load_flight_from_json(config_path)
    return env, motor, rocket, flight

import pandas as pd
import matplotlib.pyplot as plt

def plot_mass_vs_apogee(csv_file, target=3000):
    """
    Reads mass and apogee data from a CSV and plots apogee vs mass,
    including target lines and highlighting the closest apogee to target.

    Parameters:
        csv_file (str): Path to the CSV file with 'mass' and 'apogee' columns.
        target (float): Target apogee value in meters.
    """
    # Read CSV
    data = pd.read_csv(csv_file)
    
    # Ensure expected columns exist
    if 'mass' not in data.columns or 'apogee' not in data.columns:
        raise ValueError("CSV must contain 'mass' and 'apogee' columns.")
    
    masses = data['mass'].tolist()
    apogees = data['apogee'].tolist()
    
    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(masses, apogees, 'b-', label="Apogee vs Mass", linewidth=2)
    plt.xlabel("Mass (kg)", fontsize=12)
    plt.ylabel("Max Z (m) - Altitude", fontsize=12)
    plt.title("Rocket Mass Sensitivity Analysis", fontsize=14)

    # Target lines
    plt.axhline(y=target, color='k', linestyle='--', linewidth=1.5,
                label=f"Opt Apogee: {target} m")
    plt.axhline(y=target * 1.04, color='blue', linestyle=':', linewidth=1.2, alpha=0.9, label="±4%")
    plt.axhline(y=target * 0.96, color='blue', linestyle=':', linewidth=1.2, alpha=0.9)
    plt.axhline(y=target * 1.02, color='red', linestyle=':', linewidth=1.2, alpha=0.9, label="±2%")
    plt.axhline(y=target * 0.98, color='red', linestyle=':', linewidth=1.2, alpha=0.9)

    # Find closest to target
    deviations = [abs(a - target) for a in apogees]
    closest_idx = deviations.index(min(deviations))
    plt.plot(masses[closest_idx], apogees[closest_idx], 'ro', markersize=4,
             label=f'Best: {masses[closest_idx]:.2f} kg')

plt.grid(True, alpha=0.3)
plt.legend(loc='best')
plt.tight_layout()
plt.show()


def main():
    SHOW_ENVIRONMENT = False
    SHOW_ROCKET_INFO = False
    SHOW_FLIGHT_INFO = True

    masses = []
    apogees = []

    spinner = ['-', '\\', '|', '/']  # Spinner characters
    mass_values = np.arange(18.33, 22.5, 0.01)
    total = len(mass_values)

    for i, m in enumerate(mass_values):
        # Run simulation
        env, motor, rocket, flight = run_simulation(m)
        flight_info = _MyFlightPlots(flight, motor)

        # Extract apogee
        apogee = flight_info.motor_tradeoff_json["Max Z (m) - Altitude"]
        masses.append(m)
        apogees.append(apogee)

        # Spinner and percentage
        spin_char = spinner[i % len(spinner)]
        percent_complete = (i + 1) / total * 100

        # Print info in the same place using \r and ANSI escape to move up 2 lines
        sys.stdout.write("\033[F\033[F") if i > 0 else None  # move cursor up 2 lines after first loop
        print(f"{spin_char} {percent_complete:.2f}% complete")
        print(f"Current mass: {m:.2f} kg, Current apogee: {apogee:.2f} m")
        sys.stdout.flush()

    # Save to CSV
    df = pd.DataFrame({
        "Mass (kg)": masses,
        "Apogee (m)": apogees
    })
    df.to_csv("mass_apogee_data.csv", index=False)
    print("Saved mass and apogee data to 'mass_apogee_data.csv'.")

    plot_mass_vs_apogee("mass_apogee_data.csv", 3000)


if __name__ == "__main__":
    main()
'''
# Usage
# plot_mass_vs_apogee('mass_apogee_data.csv')