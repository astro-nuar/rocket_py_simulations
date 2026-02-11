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

# Usage
# plot_mass_vs_apogee('mass_apogee_data.csv')


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

