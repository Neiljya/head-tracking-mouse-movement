import pyautogui
from Rotation2Vector import Vector
import time

class Mouse:
    def __init__(self):
        self.size = pyautogui.size()
        self.position = Vector(0, 0)
        pyautogui.FAILSAFE = True

        self.first_click = False
        self.first_click_time = time.time()

    def vector2pos(self, vector):
        return Vector((1 + vector.x) * (self.size[0] / 2), (1 - vector.y) * (self.size[1] / 2))
    
    def moveCursor(self, new_vector):
        new_pos = self.vector2pos(new_vector)
        pyautogui.moveTo(new_pos.x, new_pos.y)

    

    def left_click(self):
        pyautogui.leftClick()

    def right_click(self):
        pyautogui.rightClick()