import cv2 as cv
import os
from time import time, sleep
from capture import WindowCapture
from vision import Vision
from trainer import Trainer

path = os.path.dirname(os.path.dirname(__file__))
img_path = os.path.join(path, 'img')
img = cv.imread(os.path.join(img_path, "test_screenshot.png"))
img2 = img.copy()


def execute(ev):
    trainer = Trainer()
    trainer.click_screen()
    loop_time = time()
    window_capture = WindowCapture()
    while True:

        screenshot = window_capture.get_screenshot()

        trainer.decide_action(screenshot, ev, "3")

        cv.imshow('Bot_Feed', screenshot)

        print(f'FPS {1 / (time() - loop_time)}')
        loop_time = time()

        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            break


execute("atk")
