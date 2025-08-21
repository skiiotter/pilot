import json
import threading
import time
from tkinter import (
    Tk, Button, filedialog, messagebox, Checkbutton,
    IntVar, StringVar, Toplevel, Label, Entry
)

from pynput import mouse, keyboard


class MacroRecorder:
    """Record mouse and keyboard events."""

    def __init__(self):
        self.events = []
        self.recording = False
        self._last_time = None
        self._k_listener = None
        self._m_listener = None

    def _time_delta(self):
        now = time.time()
        delta = 0 if self._last_time is None else now - self._last_time
        self._last_time = now
        return delta

    # Mouse callbacks
    def _on_move(self, x, y):
        if not self.recording:
            return
        self.events.append({
            'type': 'move',
            'pos': (x, y),
            'delay': self._time_delta(),
        })

    def _on_click(self, x, y, button, pressed):
        if not self.recording:
            return
        self.events.append({
            'type': 'click',
            'pos': (x, y),
            'button': button.name,
            'pressed': pressed,
            'delay': self._time_delta(),
        })

    def _on_scroll(self, x, y, dx, dy):
        if not self.recording:
            return
        self.events.append({
            'type': 'scroll',
            'pos': (x, y),
            'dx': dx,
            'dy': dy,
            'delay': self._time_delta(),
        })

    # Keyboard callbacks
    def _on_press(self, key):
        if not self.recording:
            return
        name = getattr(key, 'char', None) or key.name
        self.events.append({
            'type': 'key',
            'event': 'press',
            'name': name,
            'delay': self._time_delta(),
        })

    def _on_release(self, key):
        if not self.recording:
            return
        name = getattr(key, 'char', None) or key.name
        self.events.append({
            'type': 'key',
            'event': 'release',
            'name': name,
            'delay': self._time_delta(),
        })

    def start(self):
        self.events = []
        self.recording = True
        self._last_time = None
        self._k_listener = keyboard.Listener(
            on_press=self._on_press, on_release=self._on_release
        )
        self._m_listener = mouse.Listener(
            on_move=self._on_move, on_click=self._on_click, on_scroll=self._on_scroll
        )
        self._k_listener.start()
        self._m_listener.start()

    def stop(self):
        self.recording = False
        if self._k_listener:
            self._k_listener.stop()
            self._k_listener = None
        if self._m_listener:
            self._m_listener.stop()
            self._m_listener = None


class MacroPlayer:
    """Play back recorded events."""

    def __init__(self, events):
        self.events = events

    def play(self, repeat=1, stop_event=None):
        m_controller = mouse.Controller()
        k_controller = keyboard.Controller()
        count = 0
        while repeat <= 0 or count < repeat:
            for ev in self.events:
                if stop_event and stop_event.is_set():
                    return
                time.sleep(ev.get('delay', 0))
                etype = ev['type']
                if etype == 'move':
                    m_controller.position = ev['pos']
                elif etype == 'click':
                    m_controller.position = ev['pos']
                    button = getattr(mouse.Button, ev['button'])
                    if ev['pressed']:
                        m_controller.press(button)
                    else:
                        m_controller.release(button)
                elif etype == 'scroll':
                    m_controller.position = ev['pos']
                    m_controller.scroll(ev['dx'], ev['dy'])
                elif etype == 'key':
                    name = ev['name']
                    key = getattr(keyboard.Key, name, None)
                    if key is None and len(name) == 1:
                        key = name
                    if ev['event'] == 'press':
                        k_controller.press(key)
                    else:
                        k_controller.release(key)
            count += 1


class MacroApp:
    """Tkinter user interface for macro recording/playback."""

    def __init__(self, root):
        self.root = root
        self.root.title('Pilot')
        self.root.configure(bg='#2e2e2e')
        self.root.resizable(False, False)

        self.recorder = MacroRecorder()
        self.macro = []
        self.play_thread = None
        self.stop_playback = threading.Event()

        self.always_on_top = IntVar(value=0)
        self.playback_times = StringVar(value='1')
        self.record_hotkey = StringVar(value='f10')
        self.play_hotkey = StringVar(value='f6')

        self._hotkey_listener = None

        self._build_ui()
        self._set_hotkeys()
        self._update_on_top()

    def _build_ui(self):
        self.play_btn = Button(
            self.root, text='Play', width=8, command=self.toggle_play,
            bg='#3a3a3a', fg='white', relief='flat'
        )
        self.rec_btn = Button(
            self.root, text='Rec', width=8, command=self.toggle_record,
            bg='#3a3a3a', fg='white', relief='flat'
        )
        self.open_btn = Button(
            self.root, text='Open', width=8, command=self.open_macro,
            bg='#3a3a3a', fg='white', relief='flat'
        )
        self.save_btn = Button(
            self.root, text='Save', width=8, command=self.save_macro,
            bg='#3a3a3a', fg='white', relief='flat'
        )
        self.settings_btn = Button(
            self.root, text='Settings', width=8, command=self.open_settings,
            bg='#3a3a3a', fg='white', relief='flat'
        )
        self.play_btn.grid(row=0, column=0, padx=5, pady=5)
        self.rec_btn.grid(row=0, column=1, padx=5, pady=5)
        self.open_btn.grid(row=0, column=2, padx=5, pady=5)
        self.save_btn.grid(row=0, column=3, padx=5, pady=5)
        self.settings_btn.grid(row=0, column=4, padx=5, pady=5)

    def toggle_record(self):
        if self.recorder.recording:
            self.recorder.stop()
            self.macro = list(self.recorder.events)
            self.rec_btn.configure(text='Rec')
        else:
            self.recorder.start()
            self.rec_btn.configure(text='Stop')

    def toggle_play(self):
        if self.play_thread and self.play_thread.is_alive():
            self.stop_playback.set()
            self.play_thread.join()
            self.play_btn.configure(text='Play')
            return
        if not self.macro:
            messagebox.showinfo('Pilot', 'No macro recorded')
            return
        try:
            repeat = int(self.playback_times.get())
        except ValueError:
            repeat = 1
        self.stop_playback.clear()

        def run():
            player = MacroPlayer(self.macro)
            player.play(repeat=repeat, stop_event=self.stop_playback)
            self.play_btn.configure(text='Play')

        self.play_btn.configure(text='Stop')
        self.play_thread = threading.Thread(target=run, daemon=True)
        self.play_thread.start()

    def open_macro(self):
        path = filedialog.askopenfilename(filetypes=[('Macro files', '*.json')])
        if not path:
            return
        with open(path, 'r') as f:
            self.macro = json.load(f)

    def save_macro(self):
        if not self.macro:
            messagebox.showinfo('Pilot', 'No macro to save')
            return
        path = filedialog.asksaveasfilename(
            defaultextension='.json', filetypes=[('Macro files', '*.json')]
        )
        if not path:
            return
        with open(path, 'w') as f:
            json.dump(self.macro, f)

    def open_settings(self):
        win = Toplevel(self.root)
        win.title('Settings')
        win.configure(bg='#2e2e2e')
        Checkbutton(
            win, text='Always on top', variable=self.always_on_top,
            command=self._update_on_top, bg='#2e2e2e', fg='white', selectcolor='#2e2e2e'
        ).grid(row=0, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        Label(win, text='Playback:', bg='#2e2e2e', fg='white').grid(
            row=1, column=0, sticky='e', padx=5, pady=5
        )
        Entry(win, textvariable=self.playback_times, width=5).grid(
            row=1, column=1, sticky='w', padx=5, pady=5
        )
        Button(
            win, text=f'Recording Hotkey ({self.record_hotkey.get().upper()})',
            command=lambda: self._change_hotkey('record'), bg='#3a3a3a', fg='white', relief='flat'
        ).grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        Button(
            win, text=f'Playback Hotkey ({self.play_hotkey.get().upper()})',
            command=lambda: self._change_hotkey('play'), bg='#3a3a3a', fg='white', relief='flat'
        ).grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

    def _update_on_top(self):
        self.root.attributes('-topmost', bool(self.always_on_top.get()))

    def _change_hotkey(self, which):
        messagebox.showinfo('Pilot', 'Press a key for the new hotkey')

        def on_press(key):
            name = getattr(key, 'char', None) or key.name
            if which == 'record':
                self.record_hotkey.set(name.lower())
            else:
                self.play_hotkey.set(name.lower())
            self._set_hotkeys()
            listener.stop()

        listener = keyboard.Listener(on_press=on_press)
        listener.start()

    def _set_hotkeys(self):
        if self._hotkey_listener:
            self._hotkey_listener.stop()
        self._hotkey_listener = keyboard.GlobalHotKeys({
            f'<{self.record_hotkey.get()}>': self.toggle_record,
            f'<{self.play_hotkey.get()}>': self.toggle_play,
        })
        self._hotkey_listener.start()


def main():
    root = Tk()
    app = MacroApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
