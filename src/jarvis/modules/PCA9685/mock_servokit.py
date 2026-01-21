
class MockServo:
    def __init__(self, channel):
        self.channel = channel
        self._angle = None
    
    @property
    def angle(self):    
        return self._angle
    
    @angle.setter
    def angle(self, value):
        if value != self._angle:
            self._angle = value
            print(f"[MockServoKit] Servo on channel {self.channel} set to angle {value}")


class MockServoKit:
    def __init__(self, channels=16, address=0x40, busnum=None):
        self.channels = channels
        self.address = address
        self.busnum = busnum
        self.servo = [MockServo(i) for i in range(channels)]