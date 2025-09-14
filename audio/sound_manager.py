import pygame
from pathlib import Path

class SoundManager:
    def __init__(self, sound_folder="assets/sounds"):
        self.sound_folder = Path(sound_folder)
        self.sounds = {}

    def load(self, name, filename):
        """
        Load a sound file and store it under a name.
        """
        path = self.sound_folder / filename
        try:
            self.sounds[name] = pygame.mixer.Sound(str(path))
        except Exception as e:
            print(f"[SoundManager] Failed to load {filename}: {e}")

    def play(self, name):
        """
        Play a sound by its name.
        """
        if name in self.sounds:
            self.sounds[name].play()
        else:
            print(f"[SoundManager] Sound '{name}' not loaded.")
