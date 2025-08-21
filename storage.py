import json

class MacroStorage:
    def save(self, filename, events):
        with open(filename, "w") as f:
            json.dump(events, f, indent=4)

    def load(self, filename):
        with open(filename, "r") as f:
            return json.load(f)
