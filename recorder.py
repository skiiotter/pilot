from pynput import mouse, keyboard
import time

class MacroRecorder:
    def __init__(self):
        self.events = []
        self.start_time = None
        self.mouse_listener = None
        self.keyboard_listener = None
        self.recording = False

    def start(self):
        self.events = []
        self.start_time = time.time()
        self.recording = True

        self.mouse_listener = mouse.Listener(on_click=self.on_click, on_move=self.on_move)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)

        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop(self):
        self.recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()

    def record_event(self, event_type, data):
        timestamp = time.time() - self.start_time
        self.events.append({"type": event_type, "time": timestamp, "data": data})

    def on_click(self, x, y, button, pressed):
        self.record_event("click", {"x": x, "y": y, "button": str(button), "pressed": pressed})

    def on_move(self, x, y):
        self.record_event("move", {"x": x, "y": y})

    def on_press(self, key):
        self.record_event("key_press", {"key": str(key)})

    def on_release(self, key):
        self.record_event("key_release", {"key": str(key)})
