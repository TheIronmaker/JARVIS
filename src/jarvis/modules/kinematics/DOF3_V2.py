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

        """
        self.valid_formats = {
            "position": ["xyz", "zyx", "xzy"],
            "length": ["cft", "ctf", "fct", "ftc", "tcf", "tfc"]
        }

        self.validator.format(pos_format, self.valid_formats["position"], "position")
        self.validator.format(length_format, self.valid_formats["length"], "length")

        # Add validation for positions and lenghts
        self.positions = positions
        self.pos_format = pos_format
        self.lengths = lengths
        self.length_format = length_format

        self.update(positions, lengths)
        self.end_pos = self.inverse_kinematics()
        """
        
    def _parse_input(self, data, format_str, mapping):
        out = np.zeros(len(format_str))

        if isinstance(data, list):
            pass

    # Forgot what keys were for
    def update_keys(self, keys: list[str] | dict[str, str]):
        if isinstance(keys, list):
            self.validator.keys(keys, self.pos_format)

            
            keys = {name: key for name, key in zip(self.pos_format, keys)}

        for name, key in keys.items():
            if name not in self.positions:
                self.log.error(f"Invalid position name: {name}\nRecommendation: Use available position names: {list(self.positions.keys())}")

            if not isinstance(key, str):
                self.log.error(f"Key must be a string: {key}\nRecommendation: Use a string for the key.")

            if key is not None:
                self.keys[name] = key

    def update_positions(self,
                         positions: dict[str, float] | list[float | int],
                         pos_format: str = None):
        
        if isinstance(positions, list):
            self.validator.positions(positions, self.pos_format, "Position")
            if not pos_format: pos_format = self.pos_format
            positions = {name: value for name, value in zip(pos_format, positions)}

        for name, value in positions.items():
            if value is not None:
                self.positions[name] = value

    def update(self,
               positions: dict[str, float] | list[float | int] = None,
               lengths: dict[str, float] | list[float | int] = None,
               keys: list[str] | dict[str, str] = None
               ):

        if self.log.isEnabledFor(10):
            self.validator.positions(positions, list(self.positions.keys()), "Position")
            self.validator.lengths(lengths, list(self.lengths.keys()), "Length")

        if positions: self.update_positions(positions)
        if lengths: self.update_lengths(lengths)
        if keys: pass

    def update_positions(self, positions: dict[str, float] | list[float | int], pos_format: str = None):
        if pos_format:
            self.validator.format(pos_format, self.valid_formats["position"], "position")
            self.pos_format = pos_format

        if isinstance(positions, list):
            positions = self.validator.list_to_dict(positions, self.pos_format)
        
        if self.validator.ensure_int_or_float(positions, "Position"):
            self.positions = positions

    
    def update_lengths(self, lengths: dict[str, float] | list[float | int]):
        if isinstance(lengths, list):
            pass

        for name, value in lengths.items():

            if name not in self.lengths:
                self.log.error(f"Invalid length name: {name}\n Recommendation: Use available length names: {list(self.lengths.keys())}")

            if not isinstance(value, (int, float)):
                self.log.error(f"Length value must be a number: {value}\nRecommendation: Use a number for the length value.")
                    
            if value < 0:
                self.log.warning(f"Negative length value: {value}\nRecommendation: Use a positive number for the length value.")

            if value is not None:
                self.lengths[name] = value

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
