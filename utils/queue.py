"""A file for the queue class
"""
import random

from utils.song import Song


class Queue:
    """A class to keep track of and manage queues"""

    def __init__(self, songs):
        self.songs = songs
        self.current_song = 0

    def __getitem__(self, index):
        return self.songs[index]

    @classmethod
    def from_entries(cls, entries):
        songs = []
        for entry in entries:
            songs.append(Song.from_entry(entry))
        return cls(songs)

    def add(self, song):
        """Adds a song to the queue


        Parameters
        ----------
                song (Song): the song that should be added
        """
        self.songs.append(song)

    def remove(self, index):
        """Removes a song from the queue


        Parameters
        ----------
                index (int): The index of the song that should be removed
        """
        del self.songs[index]

    def next(self):
        """Returns the next song in the queue

            Returns
        -------
                Song: the next song in the queue
        """
        self.current_song += 1
        return self.songs[self.current_song]

    def prev(self):
        """Returns the previous song in the queue

            Returns
        -------
                Song: the previous song in the queue
        """
        self.current_song -= 1
        return self.songs[self.current_song]

    def clear(self):
        """Clears the queue"""
        self.songs = []

    def shuffle(self):
        """Shuffles the queue"""
        random.shuffle(self.songs)
