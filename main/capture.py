import numpy as np
from time import sleep
import win32gui
import win32ui
import win32con
from threading import Thread, Lock


def get_chrome_window_name():
    windows = list_window_names()
    for window in windows:
        if "Google Chrome" in window["name"]:
            return window["name"]


def list_window_names():
    windows = []
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            windows.append({"hex": hex(hwnd), "name": win32gui.GetWindowText(hwnd)})
    win32gui.EnumWindows(winEnumHandler, None)
    return windows


class WindowCapture:

    def __init__(self):

        self.lock = Lock()

        self.hwnd_target = get_chrome_window_name()
        self.hwnd = win32gui.FindWindow(None, self.hwnd_target)
        self.window_name = None
        self.ow = 1920
        self.oh = 1080

        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.MoveWindow(self.hwnd, window_rect[0], window_rect[1], 1200, 900, True)

    def set_window(self):
        self.hwnd_target = get_chrome_window_name()
        self.hwnd = win32gui.FindWindow(None, self.hwnd_target)
        try:
            window_rect = win32gui.GetWindowRect(self.hwnd)
            self.w = window_rect[2] - window_rect[0]
            self.h = window_rect[3] - window_rect[1]
            win32gui.SetForegroundWindow(self.hwnd)
        except Exception as e:
            self.set_window()


    def get_screenshot(self):
        self.set_window()
        hdesktop = win32gui.GetDesktopWindow()
        wdc = win32gui.GetWindowDC(hdesktop)
        dc_obj = win32ui.CreateDCFromHandle(wdc)
        cdc = dc_obj.CreateCompatibleDC()
        data_bit_map = win32ui.CreateBitmap()
        data_bit_map.CreateCompatibleBitmap(dc_obj, self.w, self.h)
        cdc.SelectObject(data_bit_map)
        cdc.BitBlt((0, 0), (self.w, self.h), dc_obj, (0, 0), win32con.SRCCOPY)

        signed_ints_array = data_bit_map.GetBitmapBits(True)
        img = np.fromstring(signed_ints_array, dtype='uint8')
        img.shape = (self.h, self.w, 4)
        # Free Resources
        dc_obj.DeleteDC()
        cdc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wdc)
        win32gui.DeleteObject(data_bit_map.GetHandle())

        # Drop Alpha Channel
        img = img[..., :3]
        img = np.ascontiguousarray(img)

        return img

    # def get_screen_position(self, pos):
    #     return (pos[0] + self.offset_x, pos[1] + self.offset_y)
