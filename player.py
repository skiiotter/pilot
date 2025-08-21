import time
import pyautogui
import keyboard as kb

class MacroPlayer:
    def __init__(self):
        self.playing = False

    def play(self, events, repeat_count=1):
        self.playing = True
        count = 0
        while self.playing and (repeat_count == 0 or count < repeat_count):
            start_time = time.time()
            for event in events:
                if not self.playing:
                    break
                delay = event["time"] - (time.time() - start_time)
                if delay > 0:
                    time.sleep(delay)

                if event["type"] == "click" and event["data"]["pressed"]:
                    pyautogui.click(event["data"]["x"], event["data"]["y"])
                elif event["type"] == "move":
                    pyautogui.moveTo(event["data"]["x"], event["data"]["y"])
                elif event["type"] == "key_press":
                    try:
                        kb.press(event["data"]["key"].replace("'", ""))
                    except:
                        pass
                elif event["type"] == "key_release":
                    try:
                        kb.release(event["data"]["key"].replace("'", ""))
                    except:
                        pass
            count += 1
        self.playing = False

    def stop(self):
        self.playing = False
