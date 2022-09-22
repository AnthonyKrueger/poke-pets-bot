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
        self.direction = 0

    def click_screen(self):
        self.mouse.position = (250, 250)
        self.mouse.press(Button.left)

    def step(self):
        key = None
        if self.direction == 0:
            self.direction = 1
            key = keyboard.Key.up
        else:
            self.direction = 0
            key = keyboard.Key.down
        self.keyboard.press(key)
        time.sleep(0.2)

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
        time.sleep(0.5)
        self.keyboard.press("1")
        time.sleep(0.5)
        in_battle = True
        while in_battle:
            used_moves = self.determine_used_moves()
            move_to_use = 2 + used_moves
            if move_to_use > 4:
                print("Out of moves")
                sys.exit()
            self.keyboard.press(str(move_to_use))
            time.sleep(0.5)
            is_dead = self.check_if_dead()
            if is_dead:
                in_battle = False
        self.keyboard.press(keyboard.Key.enter)
        time.sleep(0.5)
        self.keyboard.press(keyboard.Key.enter)
        time.sleep(1)

    def check_if_dead(self):
        template = cv.imread(os.path.join(self.img_path, "0hp.png"))
        sc = self.screen_shot()
        match_percent = self.template_match(template, sc)
        print(match_percent)
        if match_percent > 0.95:
            return True

    def determine_used_moves(self):
        used_moves = 0
        template = cv.imread(os.path.join(self.img_path, "0pp.png"))
        sc = self.screen_shot()
        res = cv.matchTemplate(sc, template, cv.TM_CCOEFF_NORMED)
        threshold = 0.95
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            used_moves += 1
        return used_moves

    def template_match(self, template, screenshot):
        res = cv.matchTemplate(screenshot, template, cv.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(res)
        return max_val

    def test_image_load(self):
        img = cv.imread(os.path.join(self.img_path, 'test_screenshot.png'), cv.IMREAD_UNCHANGED)
        if img is None:
            sys.exit("Could not read the image.")
        cv.imshow("Display window", img)
        k = cv.waitKey(0)
        if k == ord("s"):
            cv.imwrite("starry_night.png", img)