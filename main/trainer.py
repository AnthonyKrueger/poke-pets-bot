import cv2 as cv
import os
import time
import sys
from pynput import mouse, keyboard
from pynput.mouse import Button
import numpy as np
import mss
import pydirectinput
from vision import Vision

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
        self.current_action = "start_heal"
        self.vision = Vision()
        self.moves_empty = False

    def decide_action(self, screenshot, target_ev, slot):
        print(self.current_action)

        if self.current_action == "start_heal":
            self.action_move_to_adventure(screenshot, "heal")

        elif self.current_action == "click_fly_button_heal":
            self.action_click_fly_button(screenshot, "go_starfall")

        elif self.current_action == "go_starfall":
            self.action_fly_to_starfall(screenshot)

        elif self.current_action == "click_heal":
            self.action_click_heal(screenshot)

        elif self.current_action == "exit_heal":
            self.action_click_exit_heal(screenshot)

        elif self.current_action == "begin_reset":
            self.action_move_to_adventure(screenshot, "solar")

        elif self.current_action == "click_fly_button_solar":
            self.action_click_fly_button(screenshot, 'go_solar')

        elif self.current_action == "go_solar":
            self.action_fly_to_solar(screenshot)

        elif self.current_action == "reset_position":
            self.action_reset_position()

        elif self.current_action == "walk_for_battle":
            self.action_walk_for_battle(screenshot, target_ev)

        elif self.current_action == "begin_battle":
            self.action_begin_battle(screenshot, slot)

        elif self.current_action == "battle":
            self.determine_battle_action(screenshot)

        elif self.current_action == "exit_battle":
            self.action_exit_battle(screenshot)

        elif self.current_action == "surrender_battle":
            self.action_surrender_battle(screenshot)

    def action_move_to_adventure(self, screenshot, next_action):
        points = self.find_and_draw(screenshot, 'adv.png', 0.9)
        if points:
            pydirectinput.moveTo(points[0][0], points[0][1])
            self.current_action = f"click_fly_button_{next_action}"
        else:
            self.press_key(keyboard.Key.up, 1, 0)
            time.sleep(0.1)

    def action_click_fly_button(self, screenshot, next_action):
        points = self.find_and_draw(screenshot, 'fly.png', 0.9)
        if points:
            pydirectinput.click(points[0][0], points[0][1])
            self.current_action = next_action

    def action_fly_to_starfall(self, screenshot):
        points = self.find_and_draw(screenshot, 'starfall.png', 0.95)
        if points:
            pydirectinput.click(points[0][0], points[0][1])
            time.sleep(0.5)
            self.press_key(keyboard.Key.up, 5, 0.25)
            self.current_action = "click_heal"
        else:
            self.press_key(keyboard.Key.down, 1, 0)
            time.sleep(0.1)

    def action_fly_to_solar(self, screenshot):
        points = self.find_and_draw(screenshot, 'solar.png', 0.95)
        if points:
            pydirectinput.click(points[0][0], points[0][1])
            time.sleep(0.5)
            self.current_action = "reset_position"
        else:
            self.press_key(keyboard.Key.down, 1, 0)
            time.sleep(0.1)

    def action_reset_position(self):
        self.press_key(keyboard.Key.right, 4, 0.2)
        self.press_key(keyboard.Key.up, 3, 0.2)
        self.current_action = "walk_for_battle"

    def action_click_heal(self, screenshot):
        points = self.find_and_draw(screenshot, 'heal.png', 0.95)
        if points:
            pydirectinput.click(points[0][0], points[0][1])
            self.current_action = "exit_heal"

    def action_click_exit_heal(self, screenshot):
        points = self.find_and_draw(screenshot, 'heal_return.png', 0.95)
        if points:
            pydirectinput.click(points[0][0], points[0][1])
            self.current_action = "begin_reset"

    def action_walk_for_battle(self, screenshot, target_ev):
        points = self.find_and_draw(screenshot, f'{target_ev}.png', 0.95)
        if points:
            self.keyboard.press(keyboard.Key.enter)
            self.current_action = "begin_battle"
        else:
            self.press_key("r", 1, 0.2)
            self.step()

    def action_begin_battle(self, screenshot, slot):
        points = self.find_and_draw(screenshot, 'in_battle.png', 0.95)
        if points:
            self.current_action = "battle"
        else:
            self.press_key(slot, 1, 0.5)

    def action_exit_battle(self, screenshot):
        points = self.find_and_draw(screenshot, 'out_battle.png', 0.95)
        if points:
            self.current_action = "walk_for_battle"
        else:
            self.press_key(keyboard.Key.enter, 1, 0.2)

    def action_surrender_battle(self, screenshot):
        points = self.find_and_draw(screenshot, 'surrender.png', 0.95)
        if points:
            pydirectinput.click(points[0][0], points[0][1])
            self.press_key(keyboard.Key.enter, 5, 1)
            self.current_action = "start_heal"

    def determine_battle_action(self, screenshot):
        used_moves = self.determine_used_moves(screenshot)
        dead = self.check_if_dead(screenshot)
        if dead == "enemy":
            self.current_action = "exit_battle"
        elif dead == "self" or self.check_for_struggle(screenshot):
            print(dead)
            print(used_moves)
            self.current_action = "surrender_battle"
        else:
            move_to_use = 1 + used_moves
            if move_to_use > 4:
                move_to_use = 1
            self.press_key(f"{move_to_use}", 1, 0.1)

    def check_for_struggle(self, screenshot):
        points = self.find_and_draw(screenshot, 'struggle.png', 0.95)
        if points:
            return True
        return False

    def click_screen(self):
        self.mouse.position = (250, 250)
        self.mouse.press(Button.left)
        time.sleep(0.2)
        self.mouse.release(Button.left)

    def find_and_draw(self, screenshot, template, threshold):
        rectangles = self.vision.find(template, screenshot, threshold)
        if len(rectangles) > 0:
            points = self.vision.get_click_points(rectangles)
            self.vision.draw_crosshairs(screenshot, points)
            print(points)
            return points

    def step(self):
        if self.direction == 0:
            self.direction = 1
            key = keyboard.Key.up
        else:
            self.direction = 0
            key = keyboard.Key.down
        self.keyboard.press(key)
        time.sleep(0.2)

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

    def press_key(self, key, amount, delay):
        key_presses = amount
        while key_presses > 0:
            self.keyboard.press(key)
            key_presses = key_presses - 1
            time.sleep(delay)

    def check_if_dead(self, screenshot):
        points = self.find_and_draw(screenshot, "0hp.png", 0.95)
        if points:
            if points[0][0] > 900:
                return "enemy"
            else:
                return "self"
        return False

    def determine_used_moves(self, screenshot):
        used_moves = 0
        points = self.find_and_draw(screenshot, "0pp.png", 0.95)
        if points:
            used_moves += len(points)
        return used_moves

    @staticmethod
    def template_match(template, screenshot):
        res = cv.matchTemplate(screenshot, template, cv.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(res)
        return max_val
