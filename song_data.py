from dataclasses import dataclass
import youtubesearchpython as yts

@dataclass
class SongData:

    yt_id: str
    yt_title: str
    yt_link: str
    yt_thumbnail_link: str
    yt_duration: str

    @classmethod
    def fromDict(cls, dct_data):
        return cls(yt_id=dct_data['id'],
                   yt_title=dct_data['title'],
                   yt_link=dct_data['link'],
                   yt_duration=dct_data['duration'],
                   yt_thumbnail_link=dct_data['richThumbnail']['url'])

    @classmethod
    def fromIDorURL(cls, id_or_url):
        try:
            res = yts.Video.getInfo(id_or_url)
            song_data = cls(yt_id=res['id'], yt_title=res['title'],
                                 yt_duration=res['duration'], yt_link=res['link'],
                                 yt_thumbnail_link=res['thumbnails'][1]['url'])
            return song_data
        except Exception as e:
            return None

    @classmethod
    def search_youtube(cls, query, limit=5):
        try:
            res = yts.VideosSearch(query, limit=limit).result()
            # print(res)
            ret_data = [SongData(yt_id=e["id"], yt_link=e["link"], yt_title=e["title"],
                                 yt_duration=e["duration"], yt_thumbnail_link=e["thumbnails"][0]["url"])
                        for e in res["result"]]
            return ret_data
        except Exception as e:
            # print(e)
            return []

