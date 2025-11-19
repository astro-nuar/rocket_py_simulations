import matplotlib.pyplot as plt
import numpy as np
from rocketpy import Environment, SolidMotor, Rocket, Flight
from my_flight_plots import _MyFlightPlots
from load_flight_from_json import load_flight_from_json
from rocketpy import EnvironmentAnalysis
from datetime import datetime

def main():
    SHOW_ENVIORMENT = True
    SHOW_ROCKET_INFO = False
    SHOW_FLIGHT_INFO = False

    # Load everything from JSON
    env, motor, rocket, flight = load_flight_from_json("rocket.json")
    
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
        
        for k, v in flight_info.motor_tradeoff_json.items():
            file.write(f"{k}, {v}\n")
            print(f"{k}, {v}\n")

    if SHOW_FLIGHT_INFO:
        flight_info.all()
    if SHOW_ROCKET_INFO:
        rocket.all_info()
    if SHOW_ENVIORMENT:
        env.plots.atmospheric_model()

main()