import matplotlib.pyplot as plt
import numpy as np
from rocketpy import Environment, SolidMotor, Rocket, Flight
from my_flight_plots import _MyFlightPlots
import json
from load_flight_from_json import load_flight_from_json
from rocketpy import EnvironmentAnalysis
from datetime import datetime

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

    with open(config_path, "r") as f:
        config  =  json.load(f)

        config["rocket"]["mass"] = m

        with open(config_path, 'w') as f:
            json.dump(config, f)
            f.close()
        
        main()

masses, apogees = zip(*li)

plt.figure(figsize=(10, 6))
plt.plot(masses, apogees, 'b-', label="Apogee vs Mass", linewidth=2)
plt.xlabel("Mass (kg)", fontsize=12)
plt.ylabel("Max Z (m) - Altitude", fontsize=12)
plt.title("Rocket Mass Sensitivity Analysis", fontsize=14)

# Target lines
target = 3000
plt.axhline(y=target, color='k', linestyle='--', linewidth=1.5, label=f"Opt Apogee: {target} m")

plt.axhline(y=target*1.04, color='blue', linestyle=':', linewidth=1.2, alpha=0.9, label="±4%")

plt.axhline(y=target*0.96, color='blue', linestyle=':', linewidth=1.2, alpha=0.9)

plt.axhline(y=target*1.02, color='red', linestyle=':', linewidth=1.2, alpha=0.9, label="±2%")

plt.axhline(y=target*0.98, color='red', linestyle=':', linewidth=1.2, alpha=0.9)

# Find closest to target
deviations = [abs(apogee - target) for apogee in apogees]

closest_idx = deviations.index(min(deviations))

plt.plot(masses[closest_idx], apogees[closest_idx], 'ro', markersize=4, 
            label=f'Best: {masses[closest_idx]:.2f} kg')

plt.grid(True, alpha=0.3)
plt.legend(loc='best')
plt.tight_layout()
plt.show()
'''