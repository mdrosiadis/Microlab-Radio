from flask import Flask, request, render_template, redirect, Response
from queue_controller import PlayerController
from song_data import SongData
import json
import constants
import dataclasses

app = Flask(__name__)


# player_queue = []
# status = []
# now_playing = []

# radios = {
# }

# control_semaphore = Semaphore(0)
# player = Thread(target=player_controller, args=(control_semaphore, player_queue))
# player.start()
player = PlayerController()
player.start()

@app.route("/")
def index_page():
    return render_template("index.html")


@app.post("/addsong")
def add_song():
    print("adding", request.form)
    if not request.form.get('url', '').startswith('https://www.youtube.com/watch'):
            return {"status": "Error", "message":"Invalid url"}

    player.command((constants.PLAY_SONG, request.form['url']))

    # return {"status": "Ok", "message": "Song added to the queue"}
    return redirect("/")

@app.get("/playlist")
def get_playlist():
    data = player.get_playlist()
    data["now_playing"] = dataclasses.asdict(data["now_playing"])
    data["playlist"] = [dataclasses.asdict(sng) for sng in data["playlist"]]
    return data


@app.get("/yt-song-data")
def get_song_data():
    yt_video_id = request.args.get('id', '')
    return dataclasses.asdict(SongData.fromIDorURL(yt_video_id))
    # return {'status' : 'error'}

@app.get("/yt-search")
def search_youtube():
    query_text = request.args.get("q", "")
    print(request.args)
    print(query_text)
    results = [dataclasses.asdict(s) for s in SongData.search_youtube(query_text, limit=3)]

    return Response(json.dumps(results),  mimetype='application/json')

if __name__ == "__main__":
    app.run(host='0.0.0.0')

    player.command((constants.KILL,))
    player.stop()
