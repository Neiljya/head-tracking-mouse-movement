import pyautogui
from backend.Rotation2Vector import Vector
import time

CLICK_PAUSE_TIME = 0.1

# One blink for left click, two blinks for right click, three blinks for double click
class Mouse:
    def __init__(self, click_interval=0.2, smoothing_alpha=0.2):
        self.size = pyautogui.size()
        self.position = Vector(0, 0)
        pyautogui.FAILSAFE = False

        self.click_count = 0
        self.last_click_time = time.time()

        self.smoothing_alpha = smoothing_alpha

        self.smoothed_vector = Vector(0,0)
        self.last_action_time = time.time()

        self.click_interval = click_interval

    def setClickInterval(self, newInterval):
        self.click_interval = newInterval

    def vector2pos(self, vector):
        return Vector((1 + vector.x) * (self.size[0] / 2), (1 - vector.y) * (self.size[1] / 2))

    def moveCursor(self, new_vector):
        # apply exponential smoothing to the new_vector

        if time.time() - self.last_action_time < CLICK_PAUSE_TIME:
            return
        
        self.smoothed_vector.x = (
            self.smoothing_alpha * new_vector.x +
            (1 - self.smoothing_alpha) * self.smoothed_vector.x
        )

        self.smoothed_vector.y = (
            self.smoothing_alpha * new_vector.y +
            (1 - self.smoothing_alpha) * self.smoothed_vector.y
        )
        new_pos = self.vector2pos(self.smoothed_vector)
        pyautogui.moveTo(new_pos.x, new_pos.y)

    # needs to be called in loop
    def checkClick(self, verbose= False):
        if self.click_count > 1 and (time.time() - self.last_click_time) > self.click_interval:
            if self.click_count == 2:
                pyautogui.leftClick()
                if verbose: print("left click")
            elif self.click_count == 3:
                pyautogui.rightClick()
                if verbose: print("right click")
            else:
                pyautogui.doubleClick()
                if verbose: print("double click")
            self.click_count = 0
            self.last_action_time = time.time()

    def registerClick(self):
        self.click_count += 1
        self.last_click_time = time.time()

    def left_click(self):
        pyautogui.leftClick()

    def right_click(self):
        pyautogui.rightClick()

    def double_click(self):
        pyautogui.doubleClick()
