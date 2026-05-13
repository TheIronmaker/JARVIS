from jarvis.modules.kinematics.base import KinematicsModule

class DOF3(KinematicsModule):
    """
    3 DOF Leg Inverse Kinematics Class
    Angles: [Coxa, Femur, Tibia]
    Lengths: [Coxa, Femur, Tibia]

    This base class handles inverse kinematics for 3 Joint Radials,
    also known as an Insectoid Leg. This is the most common leg configuration
    for quadrupeds and hexapods A good starting point for any legged robot.
    """
    def __init__(self,
            id: int = 0,
            positions: dict[str, float] | list[float | int] = [0, 0, 0],
            pos_format="xyz",
            lengths: dict[str, float] | list[float | int] = {'coxa': None, 'femur': None, 'tibia': None},
            length_format="cft"
            ):
        super().__init__(id=id)
 
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
        if isinstance(positions, list):
            if not pos_format: pos_format = self.pos_format
            positions = {name: value for name, value in zip(pos_format, positions)}

        for name, value in positions.items():
            if value is not None:
                self.positions[name] = value
    
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