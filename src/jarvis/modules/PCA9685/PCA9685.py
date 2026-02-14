from jarvis.core.threaded import ThreadedResource

class PCA9685Node(ThreadedResource):
    def __init__(self, name, bus, address="", busnum=None):
        super().__init__(0.1)
        try:
            self.name = name
            self.bus = bus.namespaced(name)
            self.address = address
            self.busnum = busnum

            import os
            if os.uname().sysname == "Linux":
                from adafruit_servokit import ServoKit
            else:
                from jarvis.modules.PCA9685.mock_servokit import MockServoKit as ServoKit

            self.kit = ServoKit(channels=16, address=self.address, busnum=self.busnum)
        except Exception as e:
            print(f"Error initializing PCA9685Node: {e}")
            raise e
        
    def loop(self):
        while self.running:
            #angle = input("Enter servo angle (0-180): ")
            #self.set_servo_angle(0, int(angle))
            self.cycle_sleep()
    
    def set_servo_angle(self, channel, angle):
        if angle < 0 or angle > 180:
            raise ValueError("Angle must be between 0 and 180 degrees.")
        self.kit.servo[channel].angle = angle
        return True

    def get_servo_angle(self, channel):
        return self.kit.servo[channel].angle