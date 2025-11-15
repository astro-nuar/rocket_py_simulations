package net.sf.openrocket.ORBrake;

import java.lang.Math;
import java.util.ListIterator;

import net.sf.openrocket.rocketcomponent.RocketComponent;
import net.sf.openrocket.rocketcomponent.TubeFinSet;
import net.sf.openrocket.simulation.SimulationStatus;
import net.sf.openrocket.simulation.listeners.AbstractSimulationListener;

public class ORBrakeSimulationListener extends AbstractSimulationListener {
	/**
	 * The simulation listener connects to and influences simulations that is
	 * attached to.
	 */

	//constants
	final double RocketArea = 0.01767;
	
	// Input parameters for PID controller
	double setpoint; // Target altitude in feet
	double Kp; // Proportional gain constant
	double Ki; // Integral gain constant
	double Kd; // Derivative gain constant
	double tau; // Low pass filter time constant
	double T = .05; // Sample time in sec

	// Input parameters for apogee estimator
	double AB_Cd;
	double mass;
	double AB_area;
	double Rocket_Cd;

	// Memory variables for PID controller
	double inte = 0; // Integral term
	double prev_err = 0; // Previous error
	double diff = 0; // Differential term
	double prev_measure = 0; // Previous measurement
	
	//AirBrakes 
    TubeFinSet tubeFin = null;

	public ORBrakeSimulationListener(double setpoint, double Kp, double Ki, double Kd, double tau,double Rocket_Cd, double AB_Cd, double mass, double area){
		super();
		this.setpoint = setpoint;
		this.Kp = Kp;
		this.Ki = Ki;
		this.Kd = Kd;
		this.tau = tau;
		this.Rocket_Cd = Rocket_Cd;
		this.AB_Cd = AB_Cd;
		this.mass = mass;
		this.AB_area = area * 0.000001;
	}

	@Override
	public void startSimulation(SimulationStatus status)
	/**
	 * Gets called at the start of the simulation to initialise time step and find AirBrakes component.
	 * 
	 * @param status The status object at the start of the simulation.
	 * @return void
	 */
	{
		T = status.getSimulationConditions().getTimeStep();
        ListIterator<RocketComponent> rocketComponents = status.getFlightConfiguration().getCoreComponents().listIterator();
        while (rocketComponents.hasNext()) {
        	RocketComponent component = rocketComponents.next();
            if(component.getName().equals("AirBrakes")){
            	tubeFin = (TubeFinSet)component;
            	tubeFin.setOuterRadius(0);
            	break;
            }
        }
	}

	@Override
	public double postSimpleThrustCalculation(SimulationStatus status, double thrust) // throws SimulationException
	/**
	 * Influences the thrust after it is computed at each time step but before it is
	 * applied to the vehicle.
	 * 
	 * @param status Object that contains simulation status details.
	 * @param thrust The computed motor thrust.
	 * @return The modified thrust to be actually applied.
	 */
	{
		double drag = airbrakeForce(status, thrust);
		if(tubeFin == null) 
			return thrust - drag;
		modifyAirBrakes(status, drag);
		return thrust;
	}
	
	double airbrakeForce(SimulationStatus status, double thrust) /**
	 * Calculates the required drag force of the air brakes based on the current simulation status and thrust.
	 * 
	 * @param status The current simulation status object.
	 * @param thrust The current thrust of the vehicle.
	 * @return The required drag force of the air brakes.
	 */{
		double requiredDrag = requiredDrag(status, thrust);
		double maxDrag = surfaceDragForce(status.getRocketPosition().z, status.getRocketVelocity().length(), AB_area, AB_Cd)
				+ surfaceDragForce(status.getRocketPosition().z, status.getRocketVelocity().length(), RocketArea, Rocket_Cd);
		if (requiredDrag > maxDrag){
			requiredDrag = maxDrag;
		} else if (requiredDrag < 0){
			requiredDrag = 0;
		}
		return requiredDrag;
	}

	void modifyAirBrakes(SimulationStatus status, double requiredDrag)/**
	 * Modifies the air brakes based on the required drag force.
	 * 
	 * @param status The current simulation status object.
	 * @param requiredDrag The required drag force.
	 */{
		if(tubeFin == null) return;
		if(requiredDrag == 0) return;
		
		double velocity = status.getRocketVelocity().length();
		double altitude = status.getRocketPosition().z;
		
		double area = calculateABArea(requiredDrag, altitude, velocity, AB_Cd);
		double radius = calculateCircleRadius(area);
        tubeFin.setOuterRadius(radius);
        tubeFin.setInnerRadius(0);
	}
	
	double calculateCircleRadius(double area) /**
	 * Calculates the circle radius given the area.
	 * 
	 * @return The circle radius.
	 */{
		return Math.sqrt(area/Math.PI);
	}
	
	double calculateABArea(double dragForce, double altitude, double velocity, double C_drag)/**
	 * Calculates the required area of the air brakes to achieve the desired drag force.
	 */{
		return 2*dragForce/(C_drag * airDensity(altitude)* Math.pow(velocity, 2));
	}
	
	double predApogee(SimulationStatus status) /**
	 * Calculates the predicted apogee altitude based on current simulation status.
	 * 
	 * @param status The current simulation status object.
	 * @return The predicted apogee altitude.
	 */{
		double alt = status.getRocketPosition().z;
		double vertVelocity = status.getRocketVelocity().z;

		double gravity = status.getSimulationConditions().getGravityModel().getGravity(status.getRocketWorldPosition());
		double refArea = status.getConfiguration().getReferenceArea();

		double termVelocity = Math.sqrt((2 * mass * gravity) / (Rocket_Cd * refArea * 1.225));
		double predApogee = alt + (((Math.pow(termVelocity, 2)) / (2 * gravity))
				* Math.log((Math.pow(vertVelocity, 2) + Math.pow(termVelocity, 2)) / (Math.pow(termVelocity, 2))));	
		return predApogee;
	}
	
	double requiredDrag(SimulationStatus status, double thrust)
	/**
	 * Computes required drag using a PID controller.
	 * 
	 * @param status The current simulation status object.
	 * @param thrust The current thrust of the vehicle.
	 * 
	 * @return required drag
	 */
	{
		// Initial conditions
		double out = 0;
		double alt = status.getRocketPosition().z;
		double velocity = status.getRocketVelocity().length();
		double refArea = status.getConfiguration().getReferenceArea();
		double predApogee = predApogee(status);

		// PID Controller
		
		// Error function
		double err = setpoint - predApogee;

		// Proportional term
		double prop = -Kp * err;

		// Integral term
		inte += 0.5 * Ki * T * (err + prev_err);
		
		// Differential term
		diff = (-2 * Kd * (predApogee - prev_measure) + (2 * tau - T) * diff) / (2 * tau + T);

	    // Anti-wind up (integral clamping)
		double minInte = surfaceDragForce(alt, velocity, refArea, Rocket_Cd);
		double maxInte = surfaceDragForce(alt, velocity, AB_area, AB_Cd) + minInte; 
	    if (inte > maxInte)
	        inte = maxInte;
	    else if (inte < minInte)
	        inte = minInte;
	    
		// Output
		out = prop + inte + diff;

		// Update memory
		prev_err = err;
		prev_measure = predApogee;

		return out;
	}
	
	double airDensity(double altitude) 
	/**
	 * Using a linear approximation (Y = -1.05^{-4} + 1.225) finds the air density for the given altitude.
	 * 
	 * @param altitude
	 * 
	 * @return The air density
	 */{
		return -0.000105 * altitude + 1.225;
	}

	double surfaceDragForce(double altitude, double velocity, double area, double C_drag)
	/**
	 * Finds the drag force of a surfaces given the current velocity, 
	 * altitude and area.
	 * 
	 * @return The drag given altitude, velocity, and area.
	 */{
		return (C_drag * airDensity(altitude)* Math.pow(velocity, 2) * area / 2);
	}

}