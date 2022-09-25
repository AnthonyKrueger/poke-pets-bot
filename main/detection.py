import cv2 as cv
import os
import time
from vision import Vision
from threading import Thread, Lock


class Detection:

    stopped = True
    lock = None
    rectangles = []
    template = None
    screenshot = None
    path = os.path.dirname(os.path.dirname(__file__))

    def __init__(self, template):
        self.lock = Lock()
        self.vision = Vision()
        self.template = template
        self.img_path = os.path.join(self.path, 'img')

    def update(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def set_template(self, template):
        self.template = template

    def run(self):
        while not self.stopped:
            if self.screenshot is not None and self.template is not None:
                # do object detection
                rectangles = self.vision.find(self.template, self.screenshot, 0.95)
                # lock the thread while updating the results
                self.lock.acquire()
                self.rectangles = rectangles
                self.lock.release()
