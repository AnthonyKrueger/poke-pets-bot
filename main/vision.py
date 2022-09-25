import cv2 as cv
import numpy as np
import os
from time import time

path = os.path.dirname(os.path.dirname(__file__))
img_path = os.path.join(path, 'img')
green = (0, 255, 0)
red = (0, 0, 255)
yellow = (0, 255, 255)

class Vision:

    def __init__(self, method=cv.TM_CCOEFF_NORMED):

        self.method = method

    def find(self, template_name, screenshot, threshold=0.5):

        template = cv.imread(os.path.join(img_path, template_name), cv.IMREAD_UNCHANGED)[..., :3]
        template_w = template.shape[1]
        template_h = template.shape[0]
        result = cv.matchTemplate(screenshot, template, self.method)

        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))
        rectangles = []
        for loc in locations:
            # print(loc)
            rect = [int(loc[0]), int(loc[1]), template_w, template_h]
            # Add every box to the list twice in order to retain single (non-overlapping) boxes
            rectangles.append(rect)
            rectangles.append(rect)

        rectangles, weights = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)

        return rectangles

    def get_click_points(self, rectangles):
        points = []
        for (x, y, w, h) in rectangles:
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            points.append((center_x, center_y))
        return points

    def draw_rectangles(self, screenshot, rectangles):
        line_color = (0, 255, 0)
        line_type = cv.LINE_4
        for (x, y, w, h) in rectangles:
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            # Draw the box
            cv.rectangle(screenshot, top_left, bottom_right, color=line_color,
                         lineType=line_type, thickness=2)
        return screenshot

    def draw_crosshairs(self, screenshot, points):
        # these colors are actually BGR
        marker_color = (150, 0, 255)
        marker_type = cv.MARKER_CROSS

        for (center_x, center_y) in points:
            # draw the center point
            cv.drawMarker(screenshot, (center_x, center_y), marker_color, marker_type, thickness=3)

        return screenshot

    def write_and_draw_output(self, screenshot, trainer, points, fps):
        font = cv.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5

        fps_color = yellow if fps > 10 else red
        tsc_color = self.determine_tsc_color(trainer)
        thickness = 1

        cv.rectangle(screenshot, (25, 30), (600, 120), (25, 25, 25), -1)
        cv.putText(screenshot, f'FPS: {fps}', (50, 50), font, font_scale, fps_color, thickness, cv.LINE_AA)
        cv.putText(screenshot, f'Action: {trainer.current_action}', (50, 75), font, font_scale, (0, 255, 255), thickness,
                   cv.LINE_AA)
        cv.putText(screenshot, f'TSC: {round(trainer.time_since_change, 2)}', (50, 100), font, font_scale, tsc_color, thickness,
                   cv.LINE_AA)
        cv.putText(screenshot, f'RT: {round((time() - trainer.init_time), 0)}', (150, 50), font, font_scale, green, thickness,
                   cv.LINE_AA)
        if points:
            display_screenshot = self.draw_crosshairs(screenshot, points)
        else:
            display_screenshot = screenshot

        return display_screenshot

    def determine_tsc_color(self, trainer):

        longer_actions = ['walk_for_battle', 'battle']
        if trainer.current_action in longer_actions:
            if trainer.time_since_change > 30:
                return red
            elif trainer.time_since_change > 10:
                return yellow
            else:
                return green

        if trainer.current_action not in longer_actions:
            if trainer.time_since_change > 10:
                return red
            elif trainer.time_since_change > 5:
                return yellow
            else:
                return green
