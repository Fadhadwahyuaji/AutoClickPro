import keyboard
import pyautogui
import time
import threading

class AutoClicker:
    def __init__(self):
        self.running = False
        self.thread = None

    def start(self, hours, minutes, seconds, milliseconds, button="left", x=None, y=None):
        interval = (hours * 3600 + minutes * 60 + seconds) + (milliseconds / 1000)
        if interval <= 0:
            return
        self.running = True
        self.thread = threading.Thread(target=self._click_loop, args=(interval, button, x, y), daemon=True)
        self.thread.start()
        # Hotkey stop (F6)
        keyboard.add_hotkey("f6", self.stop)

    def _perform_click(self, button, x, y):
        if button == "double":
            if x is not None and y is not None:
                pyautogui.doubleClick(x=x, y=y)
            else:
                pyautogui.doubleClick()
        else:
            if x is not None and y is not None:
                pyautogui.click(x=x, y=y, button=button)
            else:
                pyautogui.click(button=button)

    def _click_loop(self, interval, button, x, y):
        while self.running:
            self._perform_click(button, x, y)
            time.sleep(interval)

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            # Jangan join bila dipanggil dari hotkey thread lain yang bisa blok
            try:
                self.thread.join(timeout=0.2)
            except RuntimeError:
                pass