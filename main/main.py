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

def execute():
    trainer = Trainer()
    trainer.click_screen()
    template = cv.imread(os.path.join(img_path, "atk.png"))
    loop = True
    while loop:
        time.sleep(0.5)
        trainer.step()
        sc = trainer.screen_shot()
        res = cv.matchTemplate(sc, template, cv.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(res)
        if(max_val > 0.95):
            trainer.enter()
            time.sleep(1)
            trainer.battle()
        else:
            trainer.run_away()


execute()