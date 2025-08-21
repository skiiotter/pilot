import customtkinter as ctk

class SettingsManager:
    def __init__(self):
        self.always_on_top = False
        self.playback_count = 1
        self.record_hotkey = "F10"
        self.playback_hotkey = "F6"

    def open_window(self, parent, app_ref):
        win = ctk.CTkToplevel(parent)
        win.title("Settings")
        win.geometry("300x200")

        # Always on top toggle
        toggle = ctk.CTkCheckBox(win, text="Always on Top",
                                 command=lambda: self.toggle_always_on_top(app_ref))
        toggle.pack(pady=5)

        # Playback count
        ctk.CTkLabel(win, text="Playback Count (0 = infinite)").pack()
        entry = ctk.CTkEntry(win)
        entry.insert(0, str(self.playback_count))
        entry.pack(pady=5)

        def save_count():
            try:
                val = int(entry.get())
                self.playback_count = val
            except:
                self.playback_count = 1
        ctk.CTkButton(win, text="Save Playback Count", command=save_count).pack(pady=5)

        # Hotkey labels
        ctk.CTkLabel(win, text=f"Recording Hotkey: {self.record_hotkey}").pack(pady=5)
        ctk.CTkLabel(win, text=f"Playback Hotkey: {self.playback_hotkey}").pack(pady=5)

    def toggle_always_on_top(self, app_ref):
        self.always_on_top = not self.always_on_top
        app_ref.app.attributes("-topmost", self.always_on_top)
