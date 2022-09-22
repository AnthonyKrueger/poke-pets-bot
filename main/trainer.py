import cv2 as cv
import os
import time
import sys
from pynput import mouse, keyboard
from pynput.mouse import Button
import numpy as np
import mss
import pydirectinput


# noinspection PyTypeChecker
class Trainer:
    def __init__(self):
        self.stc = mss.mss()
        path = os.path.dirname(os.path.dirname(__file__))

        self.img_path = os.path.join(path, 'img')
        self.mouse = mouse.Controller()
        self.keyboard = keyboard.Controller()
        self.mode = "EV"
        self.target_ev = None
        self.continue_walking = True
        self.direction = 0

    def click_screen(self):
        self.mouse.position = (250, 250)
        self.mouse.press(Button.left)
        time.sleep(0.1)
        self.mouse.release(Button.left)

    def step(self):
        if self.direction == 0:
            self.direction = 1
            key = keyboard.Key.up
        else:
            self.direction = 0
            key = keyboard.Key.down
        self.keyboard.press(key)
        time.sleep(0.2)

    @staticmethod
    def screen_shot(left=0, top=0, width=1920, height=1080):
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
        self.keyboard.tap("r")

    def enter(self):
        self.keyboard.tap(keyboard.Key.enter)

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
            is_enemy_dead = self.check_if_dead("enemy")
            if is_enemy_dead:
                in_battle = False
            is_self_dead = self.check_if_dead("self")
            if is_self_dead:
                print("I'm Dead!")
                sys.exit()
        self.keyboard.press(keyboard.Key.enter)
        time.sleep(0.5)
        self.keyboard.press(keyboard.Key.enter)
        time.sleep(1)

    def heal_and_reset(self):
        self.go_to_fly_page()
        time.sleep(2)
        self.press_key(keyboard.Key.down, 35, 0)
        time.sleep(0.5)
        self.click_template("starfall.png")
        time.sleep(2)
        self.press_key(keyboard.Key.up, 5, 0.3)
        time.sleep(2)
        self.click_template("heal.png")
        time.sleep(1)
        self.click_template("heal_return.png")
        time.sleep(1)
        self.go_to_fly_page()
        time.sleep(1)
        self.press_key(keyboard.Key.down, 10, 0)
        time.sleep(0.5)
        self.click_template("solar.png")
        time.sleep(1)
        self.press_key(keyboard.Key.right, 6, 0.3)
        self.press_key(keyboard.Key.up, 1, 0.3)

    def go_to_fly_page(self):
        self.move_to_adventure_button()
        time.sleep(1)
        self.click_template("fly.png")

    def press_key(self, key, amount, delay):
        key_presses = amount
        while key_presses > 0:
            self.keyboard.press(key)
            key_presses = key_presses - 1
            time.sleep(delay)

    def move_to_adventure_button(self):
        sc = self.screen_shot()
        template = cv.imread(os.path.join(self.img_path, "adv.png"))
        res = cv.matchTemplate(sc, template, cv.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(res)
        pydirectinput.moveTo(max_loc[0], max_loc[1])

    def click_template(self, image):
        sc = self.screen_shot()
        template = cv.imread(os.path.join(self.img_path, image))
        res = cv.matchTemplate(sc, template, cv.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(res)
        pydirectinput.click(max_loc[0], max_loc[1])

    def check_if_dead(self, target):
        template = cv.imread(os.path.join(self.img_path, "0hp.png"))
        sc = self.screen_shot()
        res = cv.matchTemplate(sc, template, cv.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(res)
        if max_val > 0.98 and max_loc[0] < 980 and target == "enemy":
            print(max_loc[0])
            return True
        elif max_val > 0.98 and max_loc[0] > 980 and target == "self":
            print(max_loc[0])
            return True
        else:
            return False

    def determine_used_moves(self):
        used_moves = 0
        template = cv.imread(os.path.join(self.img_path, "0pp.png"))
        sc = self.screen_shot()
        res = cv.matchTemplate(sc, template, cv.TM_CCOEFF_NORMED)
        threshold = 0.95
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            print(pt)
            used_moves += 1
        return used_moves

    @staticmethod
    def template_match(template, screenshot):
        res = cv.matchTemplate(screenshot, template, cv.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(res)
        return max_val
