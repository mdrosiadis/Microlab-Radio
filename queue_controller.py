import subprocess
import time
import threading
import constants
from song_data import SongData

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class PlayerController(metaclass=Singleton):

    def __init__(self):
        print("instanciating")
        self.semaphore = threading.Semaphore(0)
        self.__player_queue = []
        self.events = []
        self.now_playing = None
        self.current_state = "STANDBY"
        self.controller_thread = None
        self.player_proc = None


    def start(self):
        if self.controller_thread is not None:
            return

        self.controller_thread = threading.Thread(target=self.controller)
        self.controller_thread.start()

    def stop(self):
        if self.controller_thread is None:
            return

        self.command((constants.KILL,))
        self.controller_thread.join()

    def command(self, comd):
        (cmd, *cmd_args) = comd
        if cmd == constants.NEXT_SONG or cmd == constants.PLAY_SONG:
            song = SongData.fromIDorURL(cmd_args[0])
            if song is not None:
                self.__player_queue.append(song)
                if len(self.__player_queue) == 1:
                    self.__add_event((constants.PLAY_SONG,))

        elif cmd == constants.KILL or cmd == constants.STOP and self.player_thread is not None:
            self.__add_event((constants.KILL, ))
        # self.__player_queue.append(msg)
        # self.semaphore.release()

    def get_playlist(self):
        return {"now_playing": self.now_playing,
                "playlist": self.__player_queue}

    def __add_event(self, evt):
        print("adding event:", evt)
        self.events.append(evt)
        self.semaphore.release()

    def play_song(self, song):
        print("NOW PLAYING:", song)
        self.current_state = "PLAYLIST"
        self.now_playing = song
        try:
            self.player_proc = subprocess.Popen(['mpv', '--no-video', song.yt_link])
            # player_proc = subprocess.Popen(['sleep', '10'])
            self.player_proc.wait()
        except InterruptedError:
            print("Player thread got interupted")
            player_proc.kill()

        self.player_proc = None

        self.current_state = "STANDBY"
        self.now_playing = None
        self.__add_event((constants.SONG_ENDED,))
        print("SONG ENDED:", song)

    def controller(self):
        print("player THREAD STARTED")
        while True:
            print("waiting for events")
            self.semaphore.acquire()
            (cmd, *cmd_args) = self.events.pop(0)
            print("got:", cmd, cmd_args)

            if cmd == constants.KILL:
                break
            elif (cmd == constants.NEXT_SONG or cmd == constants.PLAY_SONG) and \
                len(self.__player_queue) > 0 and self.current_state != "PLAYLIST":
                self.player_thread = threading.Thread(target=self.play_song, args=(self.__player_queue.pop(0),))
                self.player_thread.start()
            elif cmd == constants.STOP and self.player_proc is not None:
                self.player_proc.kill()



def main():
    queue = ["test1", "test2"]

    controller = PlayerController()
    controller.start()

    while True:
        song = input("Enter song (empty to stop): ")
        if song == "":
            break

        controller.command((constants.PLAY_SONG, song))
        # queue_lock.acquire()
        # queue.append(song)
        # print("ADDED! Q:", queue)
        # queue_lock.release()

    # player_thread.join()
    controller.stop()

if __name__ == "__main__":
    main()



