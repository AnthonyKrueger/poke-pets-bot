import cv2 as cv
import os
import time
import sys
from pynput import mouse, keyboard
from pynput.mouse import Button
import random
import numpy as np
import mss
from trainer import Trainer

path = os.path.dirname(os.path.dirname(__file__))
img_path = os.path.join(path, 'img')
img = cv.imread(os.path.join(img_path, "test_screenshot.png"))
img2 = img.copy()

def execute(ev):
    trainer = Trainer()
    trainer.click_screen()
    template = cv.imread(os.path.join(img_path, f"{ev}.png"))
    loop = True
    while loop:
        time.sleep(0.25)
        trainer.step()
        sc = trainer.screen_shot()
        match_percent = trainer.template_match(template, sc)
        if match_percent > 0.9:
            trainer.enter()
            time.sleep(0.5)
            trainer.battle()
        else:
            trainer.run_away()

execute("atk")
# trainer = Trainer()
# trainer.click_screen()
# time.sleep(1)
# trainer.heal_and_reset()