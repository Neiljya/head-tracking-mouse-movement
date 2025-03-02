import numpy as np

# play around with values 
MAX_PITCH = 35
MAX_YAW = 40

class RotationVector:
    def __init__(self, roll, pitch, yaw):
        self.roll = roll
        self.yaw = yaw
        self.pitch = pitch

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class SensitivityParams: 
    def __init__(self, sensitivity, deadzone):
        self.sensitivity = sensitivity
        self.deadzone = deadzone

def filterDeadzone(val, deadzone):
    if ((val > 0 and val > deadzone) or (val < 0 and val < deadzone)):
        return val
    return 0

def rot2MouseVector(rotation: RotationVector, sensitivity: SensitivityParams):
    scale = sensitivity.sensitivity
    thresh = sensitivity.deadzone
    yaw = np.clip(rotation.yaw / MAX_YAW * scale, -1, 1)
    pitch = np.clip(rotation.pitch / MAX_PITCH * scale, -1, 1)
    return Vector(filterDeadzone(yaw, thresh), filterDeadzone(pitch, thresh))