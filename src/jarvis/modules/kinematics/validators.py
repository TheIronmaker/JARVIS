from jarvis.core.logger.setup import setup_logger


class KinematicsValidators:
    def __init__(self, id: int = None):
        self.id = id
        self.log = setup_logger(self.__class__.__name__ + (f"-{id}" if id else ""))

    def format(self, format: str, possible_formats: list[str], format_type: str):
        status = None
        if not isinstance(format, str):
            self.log.error(f"{format_type} format must be a string: {format}\n"
                           f"Recommendation: Provide a {format_type} format string, e.g. {', '.join(possible_formats)}.")
            status = True
        if format not in possible_formats:  
            self.log.error(f"Invalid {format_type} format: {format}\n"
                           f"Recommendation: Provide a {format_type} format string, e.g. {', '.join(possible_formats)}.")
            status = True
        
        return status
    
    def angles(self, angles: dict[str, float], possible_names: list[str]):
        for name, value in angles.items():
            if name not in possible_names:
                self.log.error(f"Invalid angle name: {name}\n"
                               f"Recommendation: Use available angle names: {possible_names}")

            if not isinstance(value, (int, float)):
                self.log.error(f"Angle values must be numbers. {name} set at value: {value}\n"
                               "Recommendation: Use a number for the angle value.")

            if not (0 <= value <= 360):
                self.log.warning(f"Angle beyond typical range (0-360): {value}\nRecommendation: Double check the final value is sufficient.")

    def positions(self, positions: dict[str, float] | list[float | int], possible_names: list[str]=['x', 'y', 'z']):

        if isinstance(positions, list):
            positions = {name: value for name, value in zip(possible_names, positions)}

        for name, value in positions.items():
            if name not in possible_names:
                self.log.error(f"Invalid position name: {name}\nRecommendation: Use available position names: {possible_names}")

            if not isinstance(value, (int, float)):
                self.log.error(f"Position values must be numbers. {name} set at value: {value}\nRecommendation: Use a number for the position value.")

    def lengths(self, lengths: dict[str, float], possible_names: list[str]):
        for name, value in lengths.items():
            if name not in possible_names:
                self.log.error(f"Invalid length name: {name}\nRecommendation: Use available length names: {possible_names}")

            if not isinstance(value, (int, float)):
                self.log.error(f"Length values must be numbers: {name} set at value {value}\nRecommendation: Use a number for the length value.")
                        
            if value < 0:
                self.log.warning(f"Negative length value: {value}\nRecommendation: Use a positive number for the length value.")



cls = KinematicsValidators()
#cls.log.warning(cls.get_message("missing position format", value="abc") + "\nRecommendation: " + cls.rec["missing position format"].format(possible_formats="xyz, zyx, xzy"))
cls.format("abc", possible_formats=["xyz", "zyx", "xzy"], format_type="Position")