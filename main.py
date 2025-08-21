import customtkinter as ctk
from tkinter import filedialog
from recorder import MacroRecorder
from player import MacroPlayer
from storage import MacroStorage
from settings import SettingsManager
import threading

class PilotMacroApp:
    def __init__(self):
        # Core objects
        self.recorder = MacroRecorder()
        self.player = MacroPlayer()
        self.storage = MacroStorage()
        self.settings = SettingsManager()

        # App setup
        ctk.set_appearance_mode("dark")
        self.app = ctk.CTk()
        self.app.title("PilotMacro")
        self.app.geometry("400x100")
        self.app.configure(bg="#2b2b2b")

        # Always on top toggle
        self.app.attributes("-topmost", self.settings.always_on_top)

        # Status
        self.status_label = ctk.CTkLabel(self.app, text="Idle")
        self.status_label.pack(pady=5)

        # Buttons
        self.play_btn = ctk.CTkButton(self.app, text="Play", command=self.toggle_play)
        self.play_btn.pack(side="left", padx=5, pady=5)

        self.rec_btn = ctk.CTkButton(self.app, text="Rec", command=self.toggle_record)
        self.rec_btn.pack(side="left", padx=5, pady=5)

        self.open_btn = ctk.CTkButton(self.app, text="Open", command=self.open_macro)
        self.open_btn.pack(side="left", padx=5, pady=5)

        self.save_btn = ctk.CTkButton(self.app, text="Save", command=self.save_macro)
        self.save_btn.pack(side="left", padx=5, pady=5)

        self.settings_btn = ctk.CTkButton(self.app, text="Settings", command=self.open_settings)
        self.settings_btn.pack(side="left", padx=5, pady=5)

    def toggle_record(self):
        if not self.recorder.recording:
            self.status_label.configure(text="Recording...")
            self.rec_btn.configure(text="Stop")
            self.recorder.start()
        else:
            self.status_label.configure(text="Stopped")
            self.rec_btn.configure(text="Rec")
            self.recorder.stop()

    def toggle_play(self):
        if not self.player.playing:
            self.status_label.configure(text="Playing...")
            self.play_btn.configure(text="Stop")
            threading.Thread(target=self.run_playback, daemon=True).start()
        else:
            self.player.stop()
            self.play_btn.configure(text="Play")
            self.status_label.configure(text="Idle")

    def run_playback(self):
        self.player.play(self.recorder.events, self.settings.playback_count)
        self.play_btn.configure(text="Play")
        self.status_label.configure(text="Idle")

    def open_macro(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filename:
            self.recorder.events = self.storage.load(filename)
            self.status_label.configure(text="Macro Loaded")

    def save_macro(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json",
                                                filetypes=[("JSON Files", "*.json")])
        if filename:
            self.storage.save(filename, self.recorder.events)
            self.status_label.configure(text="Macro Saved")

    def open_settings(self):
        self.settings.open_window(self.app, self)

    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    PilotMacroApp().run()
