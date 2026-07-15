from jarvis.modules.kinematics.DOF3 import DOF3

"""
Thoughts:
- Some type of easy config editor to set up a new leg, or mirror/copy-paste/modify existing leg configs.
- Maybe add some forward kinematics functions as well, for completeness.
- Eventually add some path planning functions that can take a desired foot trajectory and calculate the necessary joint angles over time to achieve it.
- Add some visualization functions to help debug the IK calculations
- Add some error handling for unreachable positions, or singularities in the IK calculations.
- Have different coordinate systems, like body-relative vs world-relative coordinates.
- Create leg configurations, like a 4 DOF leg with an additional joint for the foot, or a 2 DOF leg with just a Coxa and Femur.
- Handle actuators, like servos vs stepper motors, and the necessary conversions between angles and pulse widths or steps [handled by the actuator class].
- Use sensors, like encoders or potentiometers, and the necessary conversions between sensor readings and joint angles [handled by the sensor class].
- Apply control algorithms, like PID control or model predictive control, and the necessary conversions between desired joint angles and actuator commands [handled by the controller class].
- Eventually integrate with a physics engine for simulation, and a real robot for testing, and handle the necessary conversions between the simulated environment and the real world [handled by the robot class].
- Overall, the goal is to create a modular and extensible framework for legged robot kinematics, that can be easily adapted to different leg configurations, actuators, sensors, and control algorithms, and can be used for both simulation and real-world applications.
"""

# This is an attemp at an API fasion quadruped manager
# Name for any amount of legs is: polyped, or multipod.
class Quadruped:
    def __init__(self):
        self.legs = [DOF3() for _ in range(4)]


if __name__ == "__main__":
    quadruped = Quadruped()