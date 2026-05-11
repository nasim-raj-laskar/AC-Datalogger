import time


def extract_sample(physics, graphic):
    """Extract all telemetry features from physics shared memory."""
    return {
        "timestamp": time.time(),

        # --- World Position ---
        "lap_progress":        graphic.normalizedCarPosition,
        "completed_laps":      graphic.completedLaps,

        # --- Core ---
        "speed_kmh":  physics.speedKmh,
        "rpms":        physics.rpms,
        "gear":        physics.gear - 1,

        # --- Driver Inputs ---
        "throttle":    physics.gas,
        "brake":       physics.brake,
        "clutch":      physics.clutch,
        "steer_angle": physics.steerAngle,

        # --- G-Forces (lateral, vertical, longitudinal) ---
        "g_lat":  physics.accG[0],
        "g_vert": physics.accG[1],
        "g_lon":  physics.accG[2],

        # --- Local Velocity ---
        "vel_x": physics.localVelocity[0],
        "vel_y": physics.localVelocity[1],
        "vel_z": physics.localVelocity[2],

        # --- Slip Angle (lateral/longitudinal local velocity ratio) ---
        "slip_angle": physics.localVelocity[0] / physics.localVelocity[2] if physics.localVelocity[2] > 1 else 0,

        # --- Angular Rates ---
        "yaw_rate":   physics.localAngularVel[1],
        "pitch_rate": physics.localAngularVel[0],
        "roll_rate":  physics.localAngularVel[2],

        # --- Orientation ---
        "heading": physics.heading,
        "pitch":   physics.pitch,
        "roll":    physics.roll,

        # --- Suspension Travel (FL, FR, RL, RR) ---
        "susp_fl": physics.suspensionTravel[0],
        "susp_fr": physics.suspensionTravel[1],
        "susp_rl": physics.suspensionTravel[2],
        "susp_rr": physics.suspensionTravel[3],

        # --- Wheel Load / N (FL, FR, RL, RR) ---
        "load_fl": physics.wheelLoad[0],
        "load_fr": physics.wheelLoad[1],
        "load_rl": physics.wheelLoad[2],
        "load_rr": physics.wheelLoad[3],

        # --- Wheel Slip (FL, FR, RL, RR) ---
        "slip_fl": physics.wheelSlip[0],
        "slip_fr": physics.wheelSlip[1],
        "slip_rl": physics.wheelSlip[2],
        "slip_rr": physics.wheelSlip[3],

        # --- Tyre Pressure (FL, FR, RL, RR) ---
        "psi_fl": physics.wheelsPressure[0],
        "psi_fr": physics.wheelsPressure[1],
        "psi_rl": physics.wheelsPressure[2],
        "psi_rr": physics.wheelsPressure[3],

        # --- Tyre Core Temp (FL, FR, RL, RR) ---
        "tyre_core_fl": physics.tyreCoreTemperature[0],
        "tyre_core_fr": physics.tyreCoreTemperature[1],
        "tyre_core_rl": physics.tyreCoreTemperature[2],
        "tyre_core_rr": physics.tyreCoreTemperature[3],

        # --- Tyre Surface Temps Inner (FL, FR, RL, RR) ---
        "temp_i_fl": physics.tyreTempI[0],
        "temp_i_fr": physics.tyreTempI[1],
        "temp_i_rl": physics.tyreTempI[2],
        "temp_i_rr": physics.tyreTempI[3],

        # --- Tyre Surface Temps Middle ---
        "temp_m_fl": physics.tyreTempM[0],
        "temp_m_fr": physics.tyreTempM[1],
        "temp_m_rl": physics.tyreTempM[2],
        "temp_m_rr": physics.tyreTempM[3],

        # --- Tyre Surface Temps Outer ---
        "temp_o_fl": physics.tyreTempO[0],
        "temp_o_fr": physics.tyreTempO[1],
        "temp_o_rl": physics.tyreTempO[2],
        "temp_o_rr": physics.tyreTempO[3],

        # --- Tyre Wear (FL, FR, RL, RR) ---
        "wear_fl": physics.tyreWear[0],
        "wear_fr": physics.tyreWear[1],
        "wear_rl": physics.tyreWear[2],
        "wear_rr": physics.tyreWear[3],

        # --- Brake Temps (FL, FR, RL, RR) ---
        "brake_temp_fl": physics.brakeTemp[0],
        "brake_temp_fr": physics.brakeTemp[1],
        "brake_temp_rl": physics.brakeTemp[2],
        "brake_temp_rr": physics.brakeTemp[3],

        # --- Wheel Angular Speed (FL, FR, RL, RR) ---
        "wheel_speed_fl": physics.wheelAngularSpeed[0],
        "wheel_speed_fr": physics.wheelAngularSpeed[1],
        "wheel_speed_rl": physics.wheelAngularSpeed[2],
        "wheel_speed_rr": physics.wheelAngularSpeed[3],

        # --- Camber (FL, FR, RL, RR) ---
        "camber_fl": physics.camberRAD[0],
        "camber_fr": physics.camberRAD[1],
        "camber_rl": physics.camberRAD[2],
        "camber_rr": physics.camberRAD[3],

        # --- Aero / Chassis ---
        "ride_height_f": physics.rideHeight[0],
        "ride_height_r": physics.rideHeight[1],
        "cg_height":     physics.cgHeight,
        "turbo_boost":   physics.turboBoost,
        "drs":           physics.drs,

        # --- Aids ---
        "tc":       physics.tc,
        "abs":      physics.abs,
        "brake_bias": physics.brakeBias,

        # --- Environment ---
        "air_temp":  physics.airTemp,
        "road_temp": physics.roadTemp,
        "water_temp": physics.waterTemp,
        "fuel":      physics.fuel,
    }
