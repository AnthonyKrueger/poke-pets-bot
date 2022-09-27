import cv2 as cv
import os
from time import time
from capture import WindowCapture
from trainer import Trainer
from vision import Vision

path = os.path.dirname(os.path.dirname(__file__))
img_path = os.path.join(path, 'img')


def execute(mode="ev", ev="any", poke_slot="1", hunt_threshold=5, start_action=None):
    window_capture = WindowCapture()
    vision = Vision()
    trainer = Trainer(window_capture, mode, start_action=start_action, target_ev=ev, slot=poke_slot)
    loop_time = time()
    fps = 0

    trainer.start()

    while True:

        screenshot = window_capture.get_screenshot()

        points = None

        if trainer.target is not None:
            trainer.update_screenshot(screenshot)
            rectangles = vision.find(trainer.target, screenshot, 0.95)
            if len(rectangles) > 0:
                points = vision.get_click_points(rectangles)
                trainer.update_points(points)

        display_screenshot = screenshot.copy()
        display_screenshot = vision.write_and_draw_output(display_screenshot, trainer, points, fps)

        cv.imshow('Bot_Feed', display_screenshot)

        fps = round(1 / (time() - loop_time))
        loop_time = time()

        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            trainer.stop()
            break


execute(mode="ev", hunt_threshold=5, ev="atk", poke_slot="2", start_action="start_heal")
