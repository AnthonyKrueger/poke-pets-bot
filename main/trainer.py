import os
import time
from pynput import mouse, keyboard
from pynput.mouse import Button
import pydirectinput
from vision import Vision
from threading import Thread, Lock


# noinspection PyTypeChecker
class Trainer:
    def __init__(self, window_capture, mode, start_action=None, target_ev="atk", slot="1"):

        # Threading properties
        self.lock = Lock()
        self.stopped = True

        # Path to images
        path = os.path.dirname(os.path.dirname(__file__))
        self.img_path = os.path.join(path, 'img')

        # Utilities for image processing
        self.vision = Vision()
        self.window_capture = window_capture

        # Controllers
        self.mouse = mouse.Controller()
        self.keyboard = keyboard.Controller()

        # General properties
        self.current_target = f'{target_ev}.png'
        self.slot = slot
        self.mode = mode
        self.points = None
        self.screenshot = None

        # Time Keeping
        self.time_since_change = 0
        self.last_change_time = time.time()

        # EV Training Variables
        self.target_ev = target_ev
        self.direction = 0

        # Action Tracking
        self.pre_fix_action = None
        self.last_action = None
        if start_action is not None:
            self.current_action = start_action
        elif mode == "ev":
            self.current_action = "start_heal"
        elif mode == "hunt":
            self.current_action = "hunt"

        # Stat Tracking
        self.init_time = time.time()
        self.kills = 0
        self.surrenders = 0

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()
        print(self.current_target)

    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            self.check_last_action()
            fix_needed = self.determine_if_need_fix()
            if self.screenshot is not None:
                if self.mode == "ev":
                    if fix_needed and self.current_action != 'debug_ev':
                        self.pre_fix_action = self.current_action
                        self.current_action = "debug_ev"
                    self.decide_action_ev(self.screenshot)
                if self.mode == "hunt":
                    self.decide_action_hunt(self.screenshot, 4)

    def update_screenshot(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def update_points(self, points):
        self.lock.acquire()
        self.points = points
        self.lock.release()

    def decide_action_ev(self, screenshot):
        # self.debug_print()

        match self.current_action:
            case "start_heal":
                self.action_move_to_adventure("heal")

            case "click_fly_button_heal":
                self.action_click_fly_button("go_starfall")

            case "go_starfall":
                self.action_fly_to_starfall()

            case "click_heal":
                self.action_click_heal()

            case "exit_heal":
                self.action_click_exit_heal()

            case "begin_reset":
                self.action_move_to_adventure("solar")

            case "click_fly_button_solar":
                self.action_click_fly_button('go_solar')

            case "go_solar":
                self.action_fly_to_solar()

            case "reset_position":
                self.action_reset_position()

            case "walk_for_battle":
                self.check_for_captcha(screenshot)
                self.action_walk_for_battle()

            case "click_battle_button":
                self.action_click_battle_button()

            case "begin_battle":
                self.action_begin_battle()

            case "battle":
                self.determine_battle_action(screenshot)

            case "exit_battle":
                self.action_exit_battle()

            case "surrender_battle":
                self.action_surrender_battle()

            case "click_surrender_ok":
                self.action_click_ok_surrender()

            case "debug_ev":
                self.action_click_ok_surrender()

    def decide_action_hunt(self, screenshot, threshold):
        self.check_for_captcha(screenshot)
        match self.current_action:

            case "hunt":
                stars = self.determine_rare_mon_type()
                if threshold > stars > 3:
                    time.sleep(0.3)
                    self.current_action = "click_try_run"

            case "click_try_run":
                self.action_click_try_run()

            case "click_confirm_escape":
                self.action_click_confirm_escape()

    def debug_print(self):
        print(f"Points: {self.points}, Target: {self.current_target}, Action: {self.current_action}")

    def action_move_to_adventure(self, next_action):
        self.current_target = 'adv.png'
        # points = self.find_and_draw(screenshot, 'adv.png', 0.9)
        if self.points:
            time.sleep(0.2)
            pydirectinput.moveTo(self.points[0][0], self.points[0][1])
            self.current_action = f"click_fly_button_{next_action}"
            self.reset_points_and_target()
            time.sleep(0.1)

    def action_click_confirm_escape(self):
        self.current_target = 'esc_conf.png'
        if self.points:
            pydirectinput.click(self.points[0][0], self.points[0][1])
            self.reset_points_and_target()
            time.sleep(0.5)
            self.current_action = "hunt"

    def action_click_battle_button(self):
        self.current_target = 'any.png'
        if self.points:
            pydirectinput.click(self.points[0][0], self.points[0][1])
            self.reset_points_and_target()
            self.current_action = "begin_battle"

    def action_click_try_run(self):
        self.current_target = 'try_run.png'
        if self.points:
            pydirectinput.click(self.points[0][0], self.points[0][1])
            self.reset_points_and_target()
            self.current_action = "click_confirm_escape"

    def action_click_fly_button(self, next_action):
        self.current_target = 'fly.png'
        if self.points:
            time.sleep(0.3)
            pydirectinput.click(self.points[0][0], self.points[0][1])
            self.reset_points_and_target()
            self.current_action = next_action

    def action_fly_to_starfall(self):
        self.current_target = 'starfall.png'
        if self.points:
            pydirectinput.click(self.points[0][0], self.points[0][1])
            time.sleep(0.5)
            self.press_key(keyboard.Key.up, 5, 0.25)
            self.reset_points_and_target()
            self.current_action = "click_heal"
        else:
            self.press_key(keyboard.Key.down, 1, 0.1)
            time.sleep(0.1)

    def reset_points_and_target(self):
        self.current_target = None
        time.sleep(0.1)
        self.points = None

    def action_fly_to_solar(self):
        self.current_target = 'solar.png'
        if self.points:
            time.sleep(0.2)
            pydirectinput.click(self.points[0][0], self.points[0][1])
            self.reset_points_and_target()
            time.sleep(0.5)
            self.current_action = "reset_position"
        else:
            self.press_key(keyboard.Key.down, 1, 0.1)
            time.sleep(0.1)

    def action_reset_position(self):
        self.press_key(keyboard.Key.right, 5, 0.2)
        self.press_key('r', 1, 0.2)
        self.press_key(keyboard.Key.up, 1, 0.2)
        self.press_key('r', 1, 0.2)
        self.press_key(keyboard.Key.up, 1, 0.2)
        self.press_key('r', 1, 0.2)
        self.press_key(keyboard.Key.up, 1, 0.2)
        self.press_key('r', 1, 0.2)
        self.press_key(keyboard.Key.right, 1, 0.2)
        self.press_key('r', 1, 0.2)
        self.current_action = "walk_for_battle"

    def action_click_heal(self):
        self.current_target = 'heal.png'
        if self.points:
            pydirectinput.click(self.points[0][0], self.points[0][1])
            self.reset_points_and_target()
            self.current_action = "exit_heal"

    def action_click_exit_heal(self):
        self.current_target = 'heal_return.png'
        if self.points:
            pydirectinput.click(self.points[0][0], self.points[0][1])
            self.reset_points_and_target()
            self.current_action = "begin_reset"

    def action_walk_for_battle(self):
        self.current_target = f'{self.target_ev}.png'
        if self.points:
            self.reset_points_and_target()
            self.current_action = "click_battle_button"
        else:
            self.press_key("r", 1, 0.2)
            self.step()

    def action_begin_battle(self):
        self.current_target = 'in_battle.png'
        if self.points:
            self.reset_points_and_target()
            self.current_action = "battle"
        else:
            self.press_key(self.slot, 1, 0.5)

    def action_exit_battle(self):
        self.current_target = 'out_battle.png'
        if self.points:
            self.reset_points_and_target()
            self.press_key(keyboard.Key.enter, 2, 0.2)
            self.current_action = "walk_for_battle"
        else:
            self.press_key(keyboard.Key.enter, 1, 0.2)

    def action_surrender_battle(self):
        self.current_target = 'surrender.png'
        if self.points:
            pydirectinput.click(self.points[0][0], self.points[0][1])
            self.reset_points_and_target()
            self.current_action = "click_surrender_ok"

    def action_click_ok_surrender(self):
        self.current_target = 'chrome_ok.png'
        if self.points:
            pydirectinput.leftClick(self.points[0][0], self.points[0][1], 0.1, 1)
            self.press_key(keyboard.Key.enter, 2, 0.5)
            pydirectinput.leftClick(self.points[0][0], self.points[0][1], 0.2, 1)
            self.press_key(keyboard.Key.enter, 1, 0.5)
            self.reset_points_and_target()
            self.current_action = "start_heal"

    def determine_if_need_fix(self):
        longer_actions = ['walk_for_battle', 'battle']
        if self.current_action not in longer_actions and self.time_since_change > 10:
            return True
        elif self.current_action in longer_actions and self.time_since_change > 30:
            return True
        else:
            return False

    def determine_fix_ev(self):
        return True

    def determine_battle_action(self, screenshot):
        used_moves = self.determine_used_moves(screenshot)
        dead = self.check_if_dead(screenshot)
        if dead == "enemy":
            self.current_action = "exit_battle"
            self.reset_points_and_target()
        elif dead == "self" or self.check_for_struggle(screenshot):
            print(dead)
            print(used_moves)
            self.current_action = "surrender_battle"
            self.reset_points_and_target()
        else:
            move_to_use = 1 + used_moves
            if move_to_use > 4:
                move_to_use = 1
            self.press_key(f"{move_to_use}", 1, 0.1)

    def determine_rare_mon_type(self):
        self.current_target = 'rarity_star.png'
        if self.points:
            self.reset_points_and_target()
            return len(self.points)
        return 0

    def check_last_action(self):
        if self.current_action == self.last_action:
            self.time_since_change = time.time() - self.last_change_time
        else:
            self.time_since_change = 0
            self.last_change_time = time.time()
            self.last_action = self.current_action

    def check_for_captcha(self, screenshot):
        self.current_target = 'cap2.png'
        points = self.find_and_draw(screenshot, 'cap2.png', 0.95)
        if points:
            time.sleep(2)
            pydirectinput.click(points[0][0], points[0][1])
            time.sleep(3)
            points = self.find_and_draw(screenshot, 'cap1.png', 0.95)
            pydirectinput.click(points[0][0], points[0][1])
            time.sleep(1)

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
        self.current_target = template
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
        time.sleep(0.3)

    def press_key(self, key, amount, delay):
        key_presses = amount
        while key_presses > 0:
            self.keyboard.press(key)
            key_presses = key_presses - 1
            time.sleep(delay)

    def check_if_dead(self, screenshot):
        points = self.find_and_draw(screenshot, "0hp.png", 0.95)
        if points:
            if points[0][0] > self.window_capture.w / 2:
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
