import cv2 as cv
import numpy as np
import os

path = os.path.dirname(os.path.dirname(__file__))
img_path = os.path.join(path, 'img')


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
        print(locations)
        rectangles = []
        for loc in locations:
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
        marker_color = (255, 0, 255)
        marker_type = cv.MARKER_CROSS

        for (center_x, center_y) in points:
            # draw the center point
            cv.drawMarker(screenshot, (center_x, center_y), marker_color, marker_type)

        return screenshot