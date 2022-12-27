import os
import threading
from song_data import SongData
import yt_dlp
from python_mpv_jsonipc import MPV
from enum import Enum, auto

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class State(Enum):
    STOPPED = auto()
    PLAYLIST = auto()
    RADIO = auto()
    KILL = auto()


class PlayerController(metaclass=Singleton):


    def __init__(self):
        self.__player_queue = []
        self.now_playing = None
        self.current_state = State.STOPPED
        self.last_played_radio = None
        self.download_thread = None

        self.pipe_name = '.audiopipe'

        try:
            os.mkfifo(self.pipe_name)
        except FileExistsError:
            print("audiopipe already exists")

        ytdl_opts = {
            'format': 'm4a/bestaudio/best', #bestaudio',m4a/bestaudio/best
            'outtmpl': self.pipe_name
        }
        self.ydl = yt_dlp.YoutubeDL(ytdl_opts)
        self.mpv = MPV(no_video="", cache="yes")
        self.mpv.bind_event("end-file", self.on_song_ended)


    def kill(self):
        self.mpv.terminate()

    def stop_playback(self):
        self.set_state(State.STOPPED)


    def get_playlist(self):
        return {"current_state": self.current_state.name,
                "now_playing": self.now_playing,
                "playlist": self.__player_queue}


    def add_playlist_song(self, song):
        self.__player_queue.append(song)
        if self.current_state != State.PLAYLIST:
            self.set_state(State.PLAYLIST)


    def start_downlaod_thread(self, link):
        self.download_thread = threading.Thread(target=self.ydl.download, args=([link],))
        self.download_thread.start()


    def play_radio(self, radio_song):
        prev_state = self.current_state
        self.selected_radio = radio_song
        self.last_played_radio = radio_song
        self.set_state(State.RADIO)


    def set_state(self, new_state):
        prev_state = self.current_state
        self.current_state = new_state
        if prev_state == State.STOPPED:
            self.on_song_ended("Wake up event")
        else:
            self.kill_players()


    def kill_players(self):
        self.mpv.command("stop")


    def play_song(self, song):
        print("NOW PLAYING:", song)
        self.now_playing = song

        if self.current_state == State.RADIO:
            self.mpv.play(song.yt_link)
        elif self.current_state == State.PLAYLIST:
            self.start_downlaod_thread(song.yt_link)
            self.mpv.play(self.pipe_name)


    def on_song_ended(self, event_data):
        print(event_data)

        if self.download_thread is not None and self.download_thread.isAlive():
            self.download_thread.join()
            self.download_thread = None

        next_song = None

        if self.current_state == State.KILL:
            self.kill()
        if self.current_state == State.PLAYLIST:
            if len(self.__player_queue) > 0:
                next_song = self.__player_queue.pop(0)
            else:
                # fallback to last played radio
                self.current_state = State.RADIO
                next_song = self.last_played_radio

        elif self.current_state == State.RADIO:
            next_song = self.selected_radio


        if next_song:
            self.play_song(next_song)
        else:
            self.current_state = State.STOPPED
            self.now_playing = None


