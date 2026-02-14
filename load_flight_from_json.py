import json
import datetime
import warnings
import numpy as np
from rocketpy import Environment, SolidMotor, Rocket, Flight
from rocketpy import Accelerometer, Barometer, GnssReceiver, Gyroscope

def load_flight_from_json(config_path, sensor_path: str):

    # Load configuration file
    with open(config_path, "r") as f:
        config  =  json.load(f)

    with open(sensor_path, "r") as f:
        config_sensor  =  json.load(f)
    
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

    accel = Accelerometer(
    sampling_rate=config_sensor["Acc-high-g"]["sampling_rate"],
    consider_gravity=False,
    noise_density=config_sensor["Acc-high-g"]["noise_density"],      
    constant_bias=config_sensor["Acc-high-g"]["constant_bias"],       
    measurement_range=config_sensor["Acc-high-g"]["measurement_range"],
    resolution=config_sensor["Acc-high-g"]["resolution"],   
    name=config_sensor["Acc-high-g"]["name"],
    cross_axis_sensitivity=config_sensor["Acc-high-g"]["cross_axis_sensitivity"]
    )

    rocket.add_sensor(accel, 1.278)

    imu_acc = Accelerometer(
    sampling_rate=config_sensor["IMU_Acc"]["sampling_rate"],
    consider_gravity=False,
    noise_density=config_sensor["IMU_Acc"]["noise_density"],     
    measurement_range=config_sensor["IMU_Acc"]["measurement_range"],
    resolution=config_sensor["IMU_Acc"]["resolution"], 
    name=config_sensor["IMU_Acc"]["name"],
    )

    rocket.add_sensor(imu_acc, 1.278)

    imu_gyro = Gyroscope(
    sampling_rate=config_sensor["IMU_Gyro"]["sampling_rate"],
    noise_density=config_sensor["IMU_Gyro"]["noise_density"],
    measurement_range=config_sensor["IMU_Gyro"]["measurement_range"],
    resolution=config_sensor["IMU_Gyro"]["resolution"],       
    name=config_sensor["IMU_Gyro"]["name"],
    )

    rocket.add_sensor(imu_gyro, 1.278)

    baro = Barometer(
    sampling_rate=config_sensor["Barometer"]["sampling_rate"],
    noise_density=config_sensor["Barometer"]["noise_density"],      
    measurement_range=config_sensor["Barometer"]["measurement_range"],
    resolution=config_sensor["Barometer"]["resolution"],       
    name=config_sensor["Barometer"]["name"],
    )

    rocket.add_sensor(baro, 1.278)

    gps = GnssReceiver(
    sampling_rate = config_sensor["GPS"]["sampling_rate"],
    position_accuracy = config_sensor["GPS"]["position_accuracy"],
    altitude_accuracy = config_sensor["GPS"]["altitude_accuracy"]
    )

    rocket.add_sensor(gps, 1.278)


    '''
     # --- Controller for air brakes ---
    # This function will close over env and motor variables defined above.
    def controller_function(time, sampling_rate, state, state_history, observed_variables, air_brakes):
        """
        Controller function signature expected by RocketPy:
        state = [x, y, z, vx, vy, vz, e0, e1, e2, e3, wx, wy, wz]
        """
        altitude_ASL = state[2]
        altitude_AGL = altitude_ASL - env.elevation
        vx, vy, vz = state[3], state[4], state[5]

        # Get winds in x and y directions
        wind_x, wind_y = env.wind_velocity_x(altitude_ASL), env.wind_velocity_y(altitude_ASL)

        # Calculate Mach number
        free_stream_speed = (
            (wind_x - vx) ** 2 + (wind_y - vy) ** 2 + (vz) ** 2
        ) ** 0.5
        mach_number = free_stream_speed / env.speed_of_sound(altitude_ASL)

        # Get previous state from state_history
        previous_state = state_history[-1]
        previous_vz = previous_state[5]

        # If we wanted to we could get the returned values from observed_variables:
        # returned_time, deployment_level, drag_coefficient = observed_variables[-1]

        # Check if the rocket has reached burnout
        if time < motor.burn_out_time:
            return None
        
        if altitude_AGL < 0:
            air_brakes.deployment_level = 0
        elif 0 < altitude_AGL <2000:
            air_brakes.deployment_level = 1
        elif 2000 < altitude_AGL <= 3000:
            air_brakes.deployment_level = 0.75
        
        new_deployment_level = 0

        if time <= 11.4:
            new_deployment_level = 1
        else:
            new_deployment_level = (
                -0.002906 * np.power(time, 3)
                + 0.1497 * np.power(time, 2)
                + -2.563 * time
                + 14.96
            )

        if time > 19.6:
            new_deployment_level = 0

        if time < 3.8:
            new_deployment_level = 0

        air_brakes.deployment_level = new_deployment_level

            
        
        # If below 1500 meters above ground level, air_brakes are not deployed
        if altitude_AGL < 1500:
            air_brakes.deployment_level = 0

        # Else calculate the deployment level
        else:
            # Controller logic
            new_deployment_level = (
                air_brakes.deployment_level + 0.1 * vz + 0.01 * previous_vz**2
            )

            # Limiting the speed of the air_brakes to 0.2 per second
            # Since this function is called every 1/sampling_rate seconds
            # the max change in deployment level per call is 0.2/sampling_rate
            max_change = 0.2 / sampling_rate
            lower_bound = air_brakes.deployment_level - max_change
            upper_bound = air_brakes.deployment_level + max_change
            new_deployment_level = min(max(new_deployment_level, lower_bound), upper_bound)

            air_brakes.deployment_level = new_deployment_level    
        
        return (
            time,
            air_brakes.deployment_level,
            air_brakes.drag_coefficient(air_brakes.deployment_level, mach_number),
        )
    
    # --- Air Brakes ---
    air_brakes_data = rocket_data["Airbrakes"]

    if air_brakes_data:
        # Expect that drag_coefficient_curve path is relative to 'path'

        warnings.filterwarnings("ignore", category=UserWarning, module="rocketpy")

        cd_curve = air_brakes_data["drag_coefficient_curve"]
        
        air_brakes = rocket.add_air_brakes(
        drag_coefficient_curve=
        path + cd_curve,
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
        air_brakes = None
    '''

    # Parachutes
    for chute_name, chute_data in rocket_data["parachutes"].items():
        
        rocket.add_parachute(
        
            chute_data["name"],
        
            cd_s =  int(chute_data["drag_coefficient"]) * int(chute_data["area"]),
        
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

    return env, motor, rocket, flight, [accel, imu_acc, imu_gyro], baro, gps
    
    ''' 
        [
        # Mach 0.1
        [0, 0.1, 0.7692],
        [10 / 100, 0.1, 0.7663],
        [20 / 100, 0.1, 0.7762],
        [30 / 100, 0.1, 0.7847],
        [40 / 100, 0.1, 0.7999],
        [50 / 100, 0.1, 0.8246],
        [60 / 100, 0.1, 0.8310],
        [70 / 100, 0.1, 0.8499],
        [80 / 100, 0.1, 0.8738],
        [90 / 100, 0.1, 0.8945],
        [100 / 100, 0.1, 1.1018],
        # Mach 0.2
        [0, 0.2, 0.7508],
        [10 / 100, 0.2, 0.7513],
        [20 / 100, 0.2, 0.7670],
        [30 / 100, 0.2, 0.7782],
        [40 / 100, 0.2, 0.7943],
        [50 / 100, 0.2, 0.8063],
        [60 / 100, 0.2, 0.8243],
        [70 / 100, 0.2, 0.8493],
        [80 / 100, 0.2, 0.8781],
        [90 / 100, 0.2, 0.8925],
        [100 / 100, 0.2, 0.9851],
        # Mach 0.3
        [0, 0.3, 0.7445],
        [10 / 100, 0.3, 0.7571],
        [20 / 100, 0.3, 0.7699],
        [30 / 100, 0.3, 0.7828],
        [40 / 100, 0.3, 0.7985],
        [50 / 100, 0.3, 0.8114],
        [60 / 100, 0.3, 0.8379],
        [70 / 100, 0.3, 0.8634],
        [80 / 100, 0.3, 0.8834],
        [90 / 100, 0.3, 0.8947],
        [100 / 100, 0.3, 0.9782],
        # Mach 0.4
        [0, 0.4, 0.7492],
        [10 / 100, 0.4, 0.7566],
        [20 / 100, 0.4, 0.7698],
        [30 / 100, 0.4, 0.7840],
        [40 / 100, 0.4, 0.7994],
        [50 / 100, 0.4, 0.8136],
        [60 / 100, 0.4, 0.8399],
        [70 / 100, 0.4, 0.8665],
        [80 / 100, 0.4, 0.8834],
        [90 / 100, 0.4, 0.8969],
        [100 / 100, 0.4, 0.9659],
        # Mach 0.5
        [0, 0.5, 0.7454],
        [10 / 100, 0.5, 0.7537],
        [20 / 100, 0.5, 0.7651],
        [30 / 100, 0.5, 0.7811],
        [40 / 100, 0.5, 0.7987],
        [50 / 100, 0.5, 0.8163],
        [60 / 100, 0.5, 0.8404],
        [70 / 100, 0.5, 0.8631],
        [80 / 100, 0.5, 0.8788],
        [90 / 100, 0.5, 0.8951],
        [100 / 100, 0.5, 0.9416],
        # Mach 0.6
        [0, 0.6, 0.7036],
        [10 / 100, 0.6, 0.7237],
        [20 / 100, 0.6, 0.7359],
        [30 / 100, 0.6, 0.7496],
        [40 / 100, 0.6, 0.7684],
        [50 / 100, 0.6, 0.7899],
        [60 / 100, 0.6, 0.8153],
        [70 / 100, 0.6, 0.8406],
        [80 / 100, 0.6, 0.8539],
        [90 / 100, 0.6, 0.8712],
        [100 / 100, 0.6, 0.9286],
        # Mach 0.7
        [0, 0.7, 0.6810],
        [10 / 100, 0.7, 0.6948],
        [20 / 100, 0.7, 0.7076],
        [30 / 100, 0.7, 0.7233],
        [40 / 100, 0.7, 0.7427],
        [50 / 100, 0.7, 0.7629],
        [60 / 100, 0.7, 0.7876],
        [70 / 100, 0.7, 0.8073],
        [80 / 100, 0.7, 0.8272],
        [90 / 100, 0.7, 0.8453],
        [100 / 100, 0.7, 0.8960],
        # Mach 0.8
        [0, 0.8, 0.6578],
        [10 / 100, 0.8, 0.6739],
        [20 / 100, 0.8, 0.6870],
        [30 / 100, 0.8, 0.7036],
        [40 / 100, 0.8, 0.7240],
        [50 / 100, 0.8, 0.7457],
        [60 / 100, 0.8, 0.7676],
        [70 / 100, 0.8, 0.7880],
        [80 / 100, 0.8, 0.8098],
        [90 / 100, 0.8, 0.8278],
        [100 / 100, 0.8, 0.8799],
        # Mach 0.9
        [0, 0.9, 0.6574],
        [10 / 100, 0.9, 0.6634],
        [20 / 100, 0.9, 0.6794],
        [30 / 100, 0.9, 0.6958],
        [40 / 100, 0.9, 0.7201],
        [50 / 100, 0.9, 0.7395],
        [60 / 100, 0.9, 0.7618],
        [70 / 100, 0.9, 0.7844],
        [80 / 100, 0.9, 0.8057],
        [90 / 100, 0.9, 0.8278],
        [100 / 100, 0.9, 0.8628],
        # Mach 1.0
        [0, 1.0, 0.8350],
        [10 / 100, 1.0, 0.8241],
        [20 / 100, 1.0, 0.8403],
        [30 / 100, 1.0, 0.8593],
        [40 / 100, 1.0, 0.8832],
        [50 / 100, 1.0, 0.9070],
        [60 / 100, 1.0, 0.9358],
        [70 / 100, 1.0, 0.9639],
        [80 / 100, 1.0, 0.9881],
        [90 / 100, 1.0, 1.0093],
        [100 / 100, 1.0, 1.0347],
        # Mach 1.1
        [0, 1.1, 0.8610],
        [10 / 100, 1.1, 0.8447],
        [20 / 100, 1.1, 0.8617],
        [30 / 100, 1.1, 0.8800],
        [40 / 100, 1.1, 0.9027],
        [50 / 100, 1.1, 0.9244],
        [60 / 100, 1.1, 0.9515],
        [70 / 100, 1.1, 0.9810],
        [80 / 100, 1.1, 1.0069],
        [90 / 100, 1.1, 1.0253],
        [100 / 100, 1.1, 1.0560],
    ],
    '''