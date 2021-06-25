class Song:
    """A class to keep track of and manage songs"""

    def __init__(self, name, link, duration, *, data=None):
        self.name = name
        self.link = link
        self.duration = duration
        self.data = data

    @classmethod
    def from_entry(cls, entry):
        return cls(entry["name"], entry["url"], entry["duration"], data=entry)
