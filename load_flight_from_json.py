import json
import datetime
import numpy as np
from rocketpy import Environment, SolidMotor, Rocket, Flight

def load_flight_from_json(config_path: str):

    # Load configuration file
    with open(config_path, "r") as f:
        config = json.load(f)
    
    path = config["path"]

    # --- Environment ---
    env_data = config["environment"]
    env = Environment(
        latitude=env_data["latitude"],
        longitude=env_data["longitude"],
        elevation=env_data["elevation"],
    )

    # Parse date
    date_obj = datetime.date.fromisoformat(env_data["date"])
    env.set_date((date_obj.year, date_obj.month, date_obj.day, 12))
    env.set_atmospheric_model(type=env_data["atmospheric_model"])
    #env.set_atmospheric_model(type=env_data["atmospheric_model"]["type"],
    #                            file=env_data["atmospheric_model"]["file"],
    #                            dictionary=env_data["atmospheric_model"]["dictionary"])
    #env.set_atmospheric_model(
    #type="Reanalysis",
    #file="../../data/weather/euroc_2023_all_windows.nc",
    #dictionary="ECMWF",
#)

    # --- Motor ---
    motor_data = config["motor"]
    motor = SolidMotor(
        thrust_source=path + motor_data["thrust_source"],
        dry_mass=motor_data["dry_mass"],
        dry_inertia=tuple(motor_data["dry_inertia"]),
        nozzle_radius=motor_data["nozzle_radius"],
        grain_number=motor_data["grain_number"],
        grain_density=motor_data["grain_density"],
        grain_outer_radius=motor_data["grain_outer_radius"],
        grain_initial_inner_radius=motor_data["grain_initial_inner_radius"],
        grain_initial_height=motor_data["grain_initial_height"],
        grain_separation=motor_data["grain_separation"],
        grains_center_of_mass_position=motor_data["grains_center_of_mass_position"],
        center_of_dry_mass_position=motor_data["center_of_dry_mass_position"],
        nozzle_position=motor_data["nozzle_position"],
        burn_time=motor_data["burn_time"],
        throat_radius=motor_data["throat_radius"],
        coordinate_system_orientation=motor_data["coordinate_system_orientation"],
    )

    # --- Rocket ---
    rocket_data = config["rocket"]
    
    rocket = Rocket(
        radius=rocket_data["radius"],
        mass=rocket_data["mass"],
        inertia=tuple(rocket_data["inertia"]),
        power_off_drag=path + rocket_data["power_off_drag"],
        power_on_drag=path + rocket_data["power_on_drag"],
        center_of_mass_without_motor=rocket_data["center_of_mass_without_motor"],
        coordinate_system_orientation=rocket_data["coordinate_system_orientation"],
    )

    # Rail buttons
    rb = rocket_data["rail_buttons"]
    
    rocket.set_rail_buttons(
        upper_button_position=rb["upper_button_position"],
        lower_button_position=rb["lower_button_position"],
        angular_position=rb["angular_position"],
    )

    # Add motor
    rocket.add_motor(motor, position=-1.255)

    # Nose cone
    nose = rocket_data["nose_cone"]
    rocket.add_nose(length=nose["length"], kind=nose["kind"], position=nose["position"])

    # Fins
    fins = rocket_data["fins"]
    
    rocket.add_trapezoidal_fins(
        n=fins["number"],
        root_chord=fins["root_chord"],
        tip_chord=fins["tip_chord"],
        span=fins["span"],
        position=fins["position"],
        cant_angle=fins["cant_angle"],
        airfoil=(path + fins["airfoil"], "radians"),
    )

    # Tail
    tail = rocket_data["tail"]
    rocket.add_tail(
        top_radius=tail["top_radius"],
        bottom_radius=tail["bottom_radius"],
        length=tail["length"],
        position=tail["position"],
    )

    # Parachutes
    for chute_name, chute_data in rocket_data["parachutes"].items():
        
        rocket.add_parachute(
        
            chute_data["name"],
        
            cd_s=chute_data["cd_s"],
        
            trigger=chute_data["trigger"],
        
            sampling_rate=chute_data["sampling_rate"],
        
            lag=chute_data["lag"],
        
            noise=tuple(chute_data["noise"]),
        )

    # --- Flight ---
    flight_data = config["flight"]
    flight = Flight(
        rocket=rocket,
    
        environment=env,
    
        rail_length=flight_data["rail_length"],
    
        inclination=flight_data["inclination"],
    
        heading=flight_data["heading"],
    )
    return env, motor, rocket, flight