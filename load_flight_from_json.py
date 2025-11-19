import json
import datetime
import warnings
import numpy as np
from rocketpy import Environment, SolidMotor, Rocket, Flight

def load_flight_from_json(config_path: str):

    # Load configuration file
    with open(config_path, "r") as f:
        config  =  json.load(f)
    
    path  =  config["path"]

    # --- Environment ---
    env_data  =  config["environment"]

    env  =  Environment(
        date=(2023, 10, 14, 14),
        latitude = env_data["latitude"],
        longitude = env_data["longitude"],
        elevation = env_data["elevation"],
    )

    # Parse date
    d = env_data["date"]
    env.set_date((d["year"], d["month"], d["day"], d["hour"]))
    env.set_elevation(env_data["elevation"])
    env.set_atmospheric_model(type = env_data["atmospheric_model"]["type"],
                                file = env_data["atmospheric_model"]["file_location"],
                                dictionary = env_data["atmospheric_model"]["dictionary"])
    
    # --- Motor ---
    motor_data  =  config["motor"]
    motor  =  SolidMotor(
        thrust_source = path + motor_data["thrust_source"],
        dry_mass = motor_data["dry_mass"],
        dry_inertia = tuple(motor_data["dry_inertia"]),
        nozzle_radius = motor_data["nozzle_radius"],
        grain_number = motor_data["grain_number"],
        grain_density = motor_data["grain_density"],
        grain_outer_radius = motor_data["grain_outer_radius"],
        grain_initial_inner_radius = motor_data["grain_initial_inner_radius"],
        grain_initial_height = motor_data["grain_initial_height"],
        grain_separation = motor_data["grain_separation"],
        grains_center_of_mass_position = motor_data["grains_center_of_mass_position"],
        center_of_dry_mass_position = motor_data["center_of_dry_mass_position"],
        nozzle_position = motor_data["nozzle_position"],
        burn_time = motor_data["burn_time"],
        throat_radius = motor_data["throat_radius"],
        coordinate_system_orientation = motor_data["coordinate_system_orientation"],
    )

    # --- Rocket ---
    rocket_data  =  config["rocket"]
    
    rocket  =  Rocket(
        radius = rocket_data["radius"],
        mass = rocket_data["mass"],
        inertia = tuple(rocket_data["inertia"]),
        power_off_drag = path + rocket_data["power_off_drag"],
        power_on_drag = path + rocket_data["power_on_drag"],
        center_of_mass_without_motor = rocket_data["center_of_mass_without_motor"],
        coordinate_system_orientation = rocket_data["coordinate_system_orientation"],
    )

    # Rail buttons
    rb  =  rocket_data["rail_buttons"]
    rocket.set_rail_buttons(
        upper_button_position = rb["upper_button_position"],
        lower_button_position = rb["lower_button_position"],
        angular_position = rb["angular_position"],
    )

    # Add motor
    rocket.add_motor(motor, position = 0)

    # Nose cone
    nose  =  rocket_data["nose_cone"]
    rocket.add_nose(length = nose["length"], kind = nose["kind"], position = nose["position"])

    # Fins
    fins  =  rocket_data["fins"]
    
    rocket.add_trapezoidal_fins(
        n = fins["number"],
        root_chord = fins["root_chord"],
        tip_chord = fins["tip_chord"],
        span = fins["span"],
        position = fins["position"],
        cant_angle = fins["cant_angle"]
        # airfoil = (path + fins["airfoil"], "radians"),
    )

    # Tail
    tail  =  rocket_data["tail"]
    rocket.add_tail(
        top_radius = tail["top_radius"],
        bottom_radius = tail["bottom_radius"],
        length = tail["length"],
        position = tail["position"],
    )

     # --- Controller for air brakes ---
    # This function will close over env and motor variables defined above.
    def controller_function(time, sampling_rate, state, state_history, observed_variables, air_brakes):
        """
        Controller function signature expected by RocketPy:
        state = [x, y, z, vx, vy, vz, e0, e1, e2, e3, wx, wy, wz]
        """
        mach_number = 0
        # Return the observed variables (they will be saved)

        return (
            time,
            air_brakes.deployment_level,
            air_brakes.drag_coefficient(air_brakes.deployment_level, mach_number),
        )
    """
    # --- Air Brakes ---
    air_brakes_data = rocket_data["Airbrakes"]

    if air_brakes_data:
        # Expect that drag_coefficient_curve path is relative to 'path'

        warnings.filterwarnings("ignore", category=UserWarning, module="rocketpy")

        cd_curve = air_brakes_data["drag_coefficient_curve"]
        
        air_brakes = rocket.add_air_brakes(
                drag_coefficient_curve=path + cd_curve,
                controller_function=controller_function,
                sampling_rate=air_brakes_data["sampling_rate"],
                reference_area=air_brakes_data["reference_area"],
                clamp=True,
                initial_observed_variables=[0, 0, 0],
                override_rocket_drag=False,
                name="Air Brakes",
            )
            # optional info printing
        
        air_brakes.all_info()
        #except Exception as e:
        #    warnings.warn(f"Failed to add air brakes: {e}")
        #    air_brakes = None
    """

    # Parachutes
    for chute_name, chute_data in rocket_data["parachutes"].items():
        
        rocket.add_parachute(
        
            chute_data["name"],
        
            cd_s =  int(chute_data["drag_coefficiente"]) * int(chute_data["area"]),
        
            trigger = chute_data["trigger"],
        
            sampling_rate = chute_data["sampling_rate"],
        
            lag = chute_data["lag"],
        
            noise = tuple(chute_data["noise"]),
        )

    # --- Flight ---
    flight_data  =  config["flight"]
    flight  =  Flight(
        rocket = rocket,
    
        environment = env,
    
        rail_length = flight_data["rail_length"],
    
        inclination = flight_data["inclination"],
    
        heading = flight_data["heading"],
    )

    return env, motor, rocket, flight