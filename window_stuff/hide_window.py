import ctypes.wintypes
import win32gui
import win32api
import win32process
from win32con import *
import ctypes


def find_window(name):
    try:
        return win32gui.FindWindow(None, name)
    except win32gui.error:
        print("Error while finding the window")
        return None


def hide_from_taskbar(hw):
    try:
        win32gui.ShowWindow(hw, SW_HIDE)

        ex_style = win32gui.GetWindowLong(hw, GWL_EXSTYLE)

        new_ex_style = (ex_style | WS_EX_TOOLWINDOW) & ~WS_EX_APPWINDOW

        win32gui.SetWindowLong(hw, GWL_EXSTYLE, new_ex_style)
        win32gui.ShowWindow(hw, SW_SHOW)
        #win32gui.SetWindowPos(hw, 0, 0, 0, 0, 0,
        #                      SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)

        # # Set to lowest priority
        # handle = ctypes.windll.kernel32.GetCurrentProcess()
        # ctypes.windll.kernel32.SetPriorityClass(handle, IDLE_PRIORITY_CLASS)

        return True
    except win32gui.error as e:
        print(f"Error while hiding window from taskbar: {e}")
        return False


def set_topmost(hw):
    try:
        win32gui.SetWindowPos(hw, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
        set_window_band(hw)
    except win32gui.error:
        print("Error while move window on top")


def set_window_band(hwnd, band_id=14):
    try:
        # Method 1: Set to desktop band (band 0 - highest priority)
        ctypes.windll.user32.SetWindowPos(
            hwnd,
            -1,  # HWND_TOPMOST
            0, 0, 0, 0,
            0x0001 | 0x0002 | 0x0010  # SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE
        )

        # Method 2: Use SetWindowDisplayAffinity for system-level priority
        ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0x00000011)  # WDA_EXCLUDEFROMCAPTURE | WDA_MONITOR

        # Method 3: Force to Z-order band 0 (desktop/system level)
        user32 = ctypes.windll.user32
        user32.SetWindowPos(
            hwnd,
            0,  # HWND_BOTTOM first
            0, 0, 0, 0,
            0x0001 | 0x0002 | 0x0010
        )

        # Then immediately to absolute top
        user32.SetWindowPos(
            hwnd,
            -1,  # HWND_TOPMOST
            0, 0, 0, 0,
            0x0001 | 0x0002 | 0x0010 | 0x0040  # + SWP_SHOWWINDOW
        )

        return True
    except:
        return False


def get_taskbar_height():
    try:
        spi_getworkarea = 0x0030
        user32 = ctypes.windll.user32

        # Get screen size
        sw, sh = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

        # Get work area (excluding taskbar)
        rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.SystemParametersInfoW(spi_getworkarea, 0, ctypes.byref(rect), 0)

        taskbar_height = sh - (rect.bottom - rect.top)
        return taskbar_height
    except:
        return 0


_running = False
_thread = None


import win32con
import threading, time


def enforce_topmost(hwnd):
    global _running, _thread

    _running = True

    def keep_on_top():
        while _running:
            try:
                # get idle game window
                hwnd_second = win32gui.FindWindow(None, "Idle - game - ui_window")

                # win32gui.SetWindowPos(hwnd_second, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                #                       win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)

                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW)

                ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0013)
                ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0013)

            except:
                pass
            time.sleep(0.2)

    _thread = threading.Thread(target=keep_on_top, daemon=True)
    _thread.start()


def stop_enforcer():
    global _running
    _running = False