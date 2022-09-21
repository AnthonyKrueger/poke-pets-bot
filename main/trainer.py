import cv2 as cv
import os
import time
import sys
from pynput import mouse, keyboard
from pynput.mouse import Button
import random
import numpy as np
import mss


class Trainer:
    def __init__(self):
        self.stc = mss.mss()
        path = os.path.dirname(os.path.dirname(__file__))

        self.img_path = os.path.join(path, 'img')
        self.mouse = mouse.Controller()
        self.keyboard = keyboard.Controller()
        self.mode = "EV"
        self.targetted_ev = None
        self.continue_walking = True

    def click_screen(self):
        self.mouse.position = (250, 250)
        self.mouse.press(Button.left)

    def step(self):
        time.sleep(0.3)
        self.keyboard.press(keyboard.Key.up)
        print("Up")
        time.sleep(0.3)
        self.keyboard.press(keyboard.Key.down)
        print("Down")
        time.sleep(0.3)

    def screen_shot(self, left=0, top=0, width=1920, height=1080):
        stc = mss.mss()
        scr = stc.grab({
            'left': left,
            'top': top,
            'width': width,
            'height': height
        })

        img = np.array(scr)
        img = cv.cvtColor(img, cv.IMREAD_COLOR)

        return img

    def run_away(self):
        self.keyboard.press("r")

    def enter(self):
        self.keyboard.press(keyboard.Key.enter)

    def battle(self):
        time.sleep(1)
        self.keyboard.press("1")
        time.sleep(1)
        self.keyboard.press("3")
        time.sleep(1)
        self.keyboard.press(keyboard.Key.enter)
        time.sleep(1)
        self.keyboard.press(keyboard.Key.enter)
        time.sleep(2)

    def test_image_load(self):
        img = cv.imread(os.path.join(self.img_path, 'test_screenshot.png'), cv.IMREAD_UNCHANGED)
        if img is None:
            sys.exit("Could not read the image.")
        cv.imshow("Display window", img)
        k = cv.waitKey(0)
        if k == ord("s"):
            cv.imwrite("starry_night.png", img)