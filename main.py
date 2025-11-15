import matplotlib.pyplot as plt
import numpy as np
from rocketpy import Environment, SolidMotor, Rocket, Flight
from my_flight_plots import _MyFlightPlots
from load_flight_from_json import load_flight_from_json

def main():
    # Load everything from JSON
    env, motor, rocket, flight = load_flight_from_json("rocket.json")

    flight_info = _MyFlightPlots(flight, motor)

    with open(r".\\Simulation\\Pro98M1450.txt", 'w+', encoding='utf-8') as file:
        
        for k, v in flight_info.motor_tradeoff_json.items():
            file.write(f"{k}, {v}\n")
            
    #flight_info.all()

main()