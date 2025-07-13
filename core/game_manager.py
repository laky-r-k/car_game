from scenes import name_input, lobby
from audio.sound_manager import SoundManager
class GameManager:
    def __init__(self, win):
        self.win = win
        self.player = None
        self.soundmanager = SoundManager()
        self.soundmanager.load("click","button-124476.mp3")

    def run(self):
        self.player = name_input.enter_name(self.win)
        lobby.show_lobby(self.win, self.player,self)
