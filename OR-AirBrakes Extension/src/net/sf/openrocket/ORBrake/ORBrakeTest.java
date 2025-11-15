package net.sf.openrocket.ORBrake;

import org.junit.jupiter.api.BeforeAll;

import net.sf.openrocket.rocketcomponent.FlightConfiguration;

class ORBrakeTest {
	static ORBrakeSimulationListener listener;
	static FlightConfiguration configuration;

	@BeforeAll
	static void setUpBeforeClass() throws Exception {
		//ORBrakeSimulationListener(getSetpoint(), getKp(), getKi(), getKd(), getTau(), getRocket_Cd(), getAB_Cd(), getMass(), getArea()));
		listener = new ORBrakeSimulationListener(3000.0, 8.0, 1.0, 1.0, 1.0, 0.5, 1.17, 23.088, 4484.0);
	}
	
}
