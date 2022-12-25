import subprocess
import os
import threading
from song_data import SongData
import yt_dlp

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class PlayerController(metaclass=Singleton):

    def __init__(self):
        self.semaphore = threading.Semaphore(0)
        self.__player_queue = []
        self.now_playing = None
        self.current_state = "STANDBY"
        self.controller_thread = None
        self.last_played_radio = None
        self.player_proc = None
        self.qlock = threading.Lock()
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


    def start(self):
        if self.controller_thread is not None:
            return

        self.controller_thread = threading.Thread(target=self.controller)
        self.controller_thread.start()

    def kill(self):
        if self.controller_thread is None:
            return

        self.current_state == "KILL"
        self.kill_players()
        self.controller_thread.join()


    def stop_playback(self):
        self.current_state = "STOPPED"
        self.kill_players()

    def get_playlist(self):
        return {"current_state": self.current_state,
                "now_playing": self.now_playing,
                "playlist": self.__player_queue}

    def next_song(self):
        self.current_state = "PLAYLIST"
        self.kill_players()

    def add_playlist_song(self, song):
        self.__player_queue.append(song)
        if self.current_state != "PLAYLIST":
            self.next_song()

    def start_downlaod_thread(self, link):
        self.download_thread = threading.Thread(target=self.ydl.download, args=([link],))
        self.download_thread.start()

    def play_radio(self, radio_song):
        self.current_state = "RADIO"
        self.selected_radio = radio_song
        self.last_played_radio = radio_song
        self.kill_players()


    def kill_players(self):
        subprocess.Popen(["killall", "mpv"]).wait()
        self.semaphore.release()


    def play_song(self, song):
        print("NOW PLAYING:", song)
        self.now_playing = song
        try:
            if self.current_state == "RADIO":
                self.player_proc = subprocess.Popen(['mpv', '--no-video', song.yt_link])
            else:
                self.player_proc = subprocess.Popen(['mpv', '-cache=yes', '--no-video', self.pipe_name])
                self.start_downlaod_thread(song.yt_link)

            self.player_proc.wait()
        except InterruptedError:
            self.player_proc.kill()

        if self.download_thread is not None and self.download_thread.isAlive():
            self.download_thread.join()
            self.download_thread = None

        self.now_playing = None
        self.semaphore.release()


    def controller(self):
        print("player THREAD STARTED")
        while True:
            self.semaphore.acquire()
            next_song = None

            if self.current_state == "KILL":
                break
            if self.current_state == "PLAYLIST":
                if len(self.__player_queue) > 0:
                    next_song = self.__player_queue.pop(0)
                else:
                    # fallback to last played radio
                    self.current_state = "RADIO"
                    next_song = self.last_played_radio

            elif self.current_state == "RADIO":
                next_song = self.selected_radio


            if next_song:
                self.play_song(next_song)
            else:
                self.current_state = "STOPPED"
