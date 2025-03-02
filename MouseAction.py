import pyautogui
from Rotation2Vector import Vector

class Mouse:
    def __init__(self):
        self.size = pyautogui.size()
        self.position = Vector(0, 0)
        pyautogui.FAILSAFE = True

    def vector2pos(self, vector):
        return Vector((1 + vector.x) * (self.size[0] / 2), (1 - vector.y) * (self.size[1] / 2))
    
    def moveCursor(self, new_vector):
        new_pos = self.vector2pos(new_vector)
        pyautogui.moveTo(new_pos.x, new_pos.y)