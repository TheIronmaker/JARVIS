import numpy as np

from jarvis.modules.kinematics.base import KinematicsModule

class DOF3(KinematicsModule):
    """
    Modular 3 DOF Leg Inverse Kinematics Class using NumPy.
    Internal Standard Format:
        Positions: [X, Y, Z]
        Lengths:   [Coxa, Femur, Tibia]
        Angles:    [Coxa, Femur, Tibia]

    This base class handles inverse kinematics for 3 Joint Radials,
    also known as an Insectoid Leg. This is the most common leg configuration
    for quadrupeds and hexapods A good starting point for any legged robot.
    """
    def __init__(self,
            id: int=0,
            positions=[0, 0, 0],
            pos_format="xyz",
            lengths={'coxa': None, 'femur': None, 'tibia': None},
            length_format="cft"
            ):
        super().__init__(id)

        self._DOF_num = 3

        self._pos_map = {'x': 0, 'y': 1, 'z': 2}
        self._len_map = {'c': 0, 'f': 1, 't': 2}
        self._angle_map = {'c': 0, 'f': 1, 't': 2}

        self._positions = np.zeros(3)
        self._lengths = np.zeros(3)
        self._angles = np.zeros(3)

        self.angle_limits = np.array(self._DOF_num*[[0, 360]])
        self.update(positions, pos_format, lengths, length_format)
        
    def _parse_input(self, data, format_str, mapping):
        out = np.zeros(len(format_str))

        if isinstance(data, list):
            pass

    def update(self,
               positions: dict[str, float] | list[float | int] = None,
               pos_format: str = None,
               lengths: dict[str, float] | list[float | int] = None,
               length_format: str = None,
               angles: dict[str, float] | list[float | int] = None,
               angle_format: str = None):
        
        if pos_format:
            if len(pos_format) != self._DOF_num:
                self.log.error(f"Position format length {len(pos_format)} does not match expected DOF number {self._DOF_num}\n"
                               f"Recommendation: Provide a position format string with length matching the DOF number: {self._DOF_num}")
            self._pos_map = {char: idx for idx, char in enumerate(pos_format)}

    def inverse_kinematics(self):
        pass

    @property
    def public_positions(self):
        return dict(zip(self.pos_format, self._positions))

    @property
    def public_lengths(self):
        return dict(zip(self.length_format, self._lengths))
    
    @property
    def public_angles(self):
        return dict(zip(self.angle_format, self._angles))


if __name__ == "__main__":
    leg = DOF3()
