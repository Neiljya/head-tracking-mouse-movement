import pyautogui
from backend.Rotation2Vector import Vector
import time

CLICK_LISTEN_INTERVAL = 0.2 # max interval between clicks to end listening (calibrate as needed)

# One blink for left click, two blinks for right click, three blinks for double click
class Mouse:
    def __init__(self):
        self.size = pyautogui.size()
        self.position = Vector(0, 0)
        pyautogui.FAILSAFE = False

        self.click_count = 0
        self.last_click_time = time.time()
 
    def vector2pos(self, vector):
        return Vector((1 + vector.x) * (self.size[0] / 2), (1 - vector.y) * (self.size[1] / 2))
    
    def moveCursor(self, new_vector):
        new_pos = self.vector2pos(new_vector)
        pyautogui.moveTo(new_pos.x, new_pos.y)

    # needs to be called in loop
    def checkClick(self, verbose= False):
        if self.click_count > 0 and (time.time() - self.last_click_time) > CLICK_LISTEN_INTERVAL:
            if self.click_count == 1:
                pyautogui.leftClick()
                if verbose: print("left click")
            elif self.click_count == 2:
                pyautogui.rightClick()
                if verbose: print("right click")
            else:
                pyautogui.doubleClick()
                if verbose: print("double click")
            self.click_count = 0

    def registerClick(self):
        self.click_count += 1
        self.last_click_time = time.time()

    def left_click(self):
        pyautogui.leftClick()

    def right_click(self):
        pyautogui.rightClick()

    def double_click(self):
        pyautogui.doubleClick()