function debounce(func, timeout = 300){
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => { func.apply(this, args); }, timeout);
  };
}

function changeActiveSong(song) {
    const songSection = document.querySelector("#songPlaying");

    songSection.innerText = song;
    document.title = '♪ ' + song;
}

function clearAllChildren(element) {
    while (element.firstChild) {
        element.removeChild(element.lastChild);
    }
}
function addPlaylistSong(pSong) {
    const playlistSection = document.querySelector("#playlist");

    const newPlaylistSong = document.createElement('div');
    newPlaylistSong.classList.add("playlist-song")
    newPlaylistSong.innerText = pSong["yt_title"];

    const playlist_song_button = document.createElement("button");
    playlist_song_button.classList.add("play-button-playlist");
    playlist_song_button.innerHTML = `<img src="static/play-com.svg" alt="PLAY" width="35px" id="play"/>`;
    newPlaylistSong.appendChild(playlist_song_button);

    playlistSection.appendChild(newPlaylistSong);
}

const search_bar = document.querySelector("#searchbar");
// data = { 
//     "now_playing": "aufgusaif",
//     "playlist": [
//         "afdafasdf",
//         "afdsafdaf",
//         "safaff"
//     ]
// }

function update() {
    fetch("/playlist")
        .then(data => data.json())
        .then(dj => {
            // console.log(dj);
            
            const playlistSection = document.querySelector("#playlist");
            clearAllChildren(playlistSection);
            dj["playlist"].forEach(addPlaylistSong);
            changeActiveSong(dj["now_playing"]["yt_title"]);
        });
}

// changeActiveSong(data["now_playing"])
// data["playlist"].forEach(addPlaylistSong);

function checkIfPlaylistEmpty(theText) {
    if(document.querySelector("#playlist").childElementCount === 0){
        const playlistSection = document.querySelector("#playlist");

        const text = document.createElement('a');
        text.id = "theText"
        text.innerText = theText;

        playlistSection.appendChild(text);
    }
}

function createSongDiv(song_data) {
    const d = document.createElement("div");

    d.classList.add("search-result-element");
    d.setAttribute('data-yt-link', song_data["yt_link"]);

    const thumb = document.createElement("img");
    thumb.src = song_data["yt_thumbnail_link"];

    d.appendChild(thumb);
    const ttl = document.createElement("h4");
    ttl.innerText = song_data["yt_title"];
    d.appendChild(ttl);

    return d;
}

const results_div = document.querySelector("#search-results");
/*
function sendPOST(link) {
    fetch("/addsong",
        method="POST",
        
};*/
function createClickListener(link) {
    console.log("created listener for", link);

    return (e) => {
        e.stopPropagation();
        
        search_bar.value = link;
        const frm = document.querySelector("#song-form");
        frm.submit();
    };
}

function renderSearchResults() {
    const text = search_bar.value;
    console.log("search:", text)


    if(document.activeElement != search_bar || text.length < 3) {
        results_div.style.visibility = "hidden";
        return;
    }

    fetch("/yt-search?q="+ text)
        .then(r => r.json())
        .then(data => {
            console.log(data);
            // remove children 
            clearAllChildren(results_div);
            // append new 
            for(let song of data) {
                const d = createSongDiv(song);
                d.addEventListener("click", createClickListener(song["yt_link"]));

                results_div.appendChild(d);
            }

            // set results visible
            results_div.style.visibility = "visible";
        });
}


search_bar.addEventListener("input", debounce(renderSearchResults));
document.querySelector("#stop-button").addEventListener("click", e => {
    console.log("stop");
    fetch("/stop", {method:"post"});
    update();
});
document.querySelector("#next-button").addEventListener("click", e => {
    console.log("next");
    fetch("/next-song", {method:"post"});
    update();
});
// search_bar.addEventListener("focusout", evt => {
//     setTimeout(() = > results_div.addEventListener("pointerout", () => {
//         results_div.style.visibility = "hidden";
//     }), 500);
// });
// checkIfPlaylistEmpty("There is no playlist available...")
update();
setInterval(update, 2000);
