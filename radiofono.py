from flask import Flask, request, render_template, redirect, Response, g
from queue_controller import PlayerController
from song_data import SongData
import json
import dataclasses

app = Flask(__name__)

radios = {
    "KIIS Extra" : SongData(yt_title="[RADIO] KIIS Extra", yt_link="https://onlineradiobox.com/json/gr/kissextra/play"),
    "RED 96.3" : SongData(yt_title="[RADIO] RED 96.3", yt_link="https://stream.radiojar.com/redfm963"),
    "Pepper FM": SongData(yt_title="[RADIO] Pepper FM", yt_link="https://stream.radiojar.com/pepper"),
    "Picasso": SongData(yt_title="[RADIO] Picasso", yt_link="https://stream.radiojar.com/s87smqqfewzuv"),
}

def get_player():
    if 'player' not in g:
        g.player = PlayerController()
        g.player.start()

    return g.player

@app.route("/")
def index_page():
    return render_template("index.html", radios=radios)


@app.post("/addsong")
def add_song():
    url = request.form.get('url', '');
    if url.startswith('https://www.youtube.com/watch'):
        song = SongData.fromIDorURL(url)
        if song:
            get_player().add_playlist_song(song)

    return redirect("/")

@app.post("/play-radio")
def play_radio():
    station = request.form.get("radio_name", "")

    if station in radios:
        get_player().play_radio(radios[station])

    return redirect("/")


@app.post("/stop")
def stop_player():
    get_player().stop_playback()

    return redirect("/")

@app.post("/next-song")
def next_playlist_song():
    get_player().next_song()

    return redirect("/")


@app.get("/playlist")
def get_playlist():
    data = get_player().get_playlist()

    if data["now_playing"] is None:
        data["now_playing"] = {"yt_title":"Player stopped"}
    else:
        data["now_playing"] = dataclasses.asdict(data["now_playing"])
    data["playlist"] = [dataclasses.asdict(sng) for sng in data["playlist"]]

    return data


@app.get("/yt-song-data")
def get_song_data():
    yt_video_id = request.args.get('id', '')

    return dataclasses.asdict(SongData.fromIDorURL(yt_video_id))

@app.get("/yt-search")
def search_youtube():
    query_text = request.args.get("q", "")
    results = [dataclasses.asdict(s) for s in SongData.search_youtube(query_text, limit=3)]

    return Response(json.dumps(results),  mimetype='application/json')

if __name__ == "__main__":
    try:
        # player = PlayerController()
        # player.start()
        app.run(host='0.0.0.0')
    except KeyboardInterrupt:
        print("SERVER CLOSING")
    finally:
        PlayerController().kill_players()
        PlayerController().kill()

