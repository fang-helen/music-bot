import eyed3
import sys
import os
import subprocess
import json
import mimetypes
import requests
from urllib.request import urlopen


def set_overrides(overrides_file, type_, key, value):
    with open(overrides_file) as overrides:
        overrides = json.load(overrides)

    overrides[type_][key] = value

    with open(overrides_file, "w", encoding="utf-8") as f:
        json.dump(overrides, f, ensure_ascii=False)


def add_override_by_id(overrides_file, id, name):
    set_overrides(overrides_file, type_="by_id", key=id, value=name)


def add_override_by_name(overrides_file, channel_name, name):
    set_overrides(overrides_file, type_="by_name", key=channel_name, value=name)


def get_metadata(url, overrides_file, title=None, artist=None):

    yt_api = os.getenv("YT_API")
    print(f"yt api key: {yt_api}")

    metadata = json.loads(subprocess.check_output(["yt-dlp", "-J", url]))
    channel_id = metadata["channel_id"]

    request_url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet&id={channel_id}&fields=items%2Fsnippet%2Fthumbnails&key={yt_api}"

    response = requests.get(request_url).json()
    print(f"response: {response}")
    thumbnails = response["items"][0]["snippet"]["thumbnails"].values()
    for item in thumbnails:
        print(item)
    max_res_thumbnail = sorted(thumbnails, key=lambda x: -1 * x["width"])[0]["url"]

    with open(overrides_file) as overrides:
        overrides = json.load(overrides)

    title = title or metadata["title"]

    channel = metadata["channel"]
    if artist == None:
        if channel_id in overrides["by_id"]:
            artist = overrides["by_id"][channel_id]
        elif channel in overrides["by_name"]:
            artist = overrides["by_name"][channel_id]
        else:
            artist = channel

    return title, artist, max_res_thumbnail


def download(url, downloads_folder, title, artist, thumbnail_url):
    download_dir = f"{downloads_folder}/{url.split("?v=")[1]}"

    os.makedirs(download_dir, exist_ok=True)

    os.system(
        f"yt-dlp {url} -o '{download_dir}/%(title)s.%(ext)s' -x --audio-quality 10 --audio-format mp3"
    )

    downloaded_file = f"{download_dir}/{os.listdir(download_dir)[0]}"
    print(f"downloaded to {downloaded_file}")

    audiofile = eyed3.load(downloaded_file)
    audiofile.tag.artist = artist

    imagedata = urlopen(thumbnail_url).read()
    mimetype, _encoding = mimetypes.guess_type(thumbnail_url)
    print(mimetype, thumbnail_url)
    audiofile.tag.images.set(
        type_=3,
        img_data=imagedata,
        mime_type=(mimetype or "image/jpeg"),
    )
    print(f"inferred mimetype: {mimetype} from image url: {thumbnail_url}")

    if title != None:
        audiofile.tag.title = title

    audiofile.tag.save()
    return downloaded_file


if __name__ == "__main__":
    url = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    print(f"downloading {url}")

    title, artist, thumbnail_url = get_metadata(
        url,
        overrides_file="config/channel_overrides.json",
        title=title,
        artist=None,
    )
    downloaded_file = download(
        url,
        downloads_folder="/tmp/music",
        title=title,
        artist=artist,
        thumbnail_url=thumbnail_url,
    )

    print(f"downloaded to {downloaded_file}")
