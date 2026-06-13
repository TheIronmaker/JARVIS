from jarvis.core.logger.setup import setup_logger
from jarvis.modules.kinematics.validators import KinematicsValidators

class KinematicsModule:
    def __init__(self, id: int = None):
        self.id = id
        self.log = setup_logger(self.__class__.__name__ + (f"-{id}" if id else ""))
        self.validator = KinematicsValidators(id)