import threading
import time
import pyautogui

class AutoClicker:
    def __init__(self):
        self.running = False
        self.thread = None

    def start(self, interval_seconds: float, mouse_button: str = "left",
              click_type: str = "single", repeat: int | None = None,
              x: int | None = None, y: int | None = None):
        if self.running:
            return
        if interval_seconds <= 0:
            return
        self.running = True
        self.thread = threading.Thread(
            target=self._loop,
            args=(interval_seconds, mouse_button, click_type, repeat, x, y),
            daemon=True
        )
        self.thread.start()

    def _do_click(self, mouse_button, click_type, x, y):
        # click_type: single|double
        kwargs = {}
        if x is not None and y is not None:
            kwargs["x"] = x
            kwargs["y"] = y
        if click_type == "double":
            pyautogui.doubleClick(button=mouse_button, **kwargs)
        else:
            pyautogui.click(button=mouse_button, **kwargs)

    def _loop(self, interval, mouse_button, click_type, repeat, x, y):
        count = 0
        while self.running:
            self._do_click(mouse_button, click_type, x, y)
            count += 1
            if repeat is not None and count >= repeat:
                break
            time.sleep(interval)
        self.running = False

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            try:
                self.thread.join(timeout=0.3)
            except RuntimeError:
                pass