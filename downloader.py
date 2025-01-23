import eyed3
import sys
import os
import subprocess
import json
import mimetypes
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


def download(url, downloads_folder, overrides_file, title=None, artist=None):
    download_dir = f"{downloads_folder}/{url.split("?v=")[1]}"
    with open(overrides_file) as overrides:
        overrides = json.load(overrides)

    os.makedirs(download_dir, exist_ok=True)

    filename = title if title else "%(title)s"
    os.system(
        f"yt-dlp {url} -o '{download_dir}/{filename}.%(ext)s' -x --audio-quality 10 --audio-format mp3"
    )

    metadata = json.loads(subprocess.check_output(["yt-dlp", "-J", url]))

    channel_id = metadata["channel_id"]
    channel = metadata["channel"]
    if artist != None:
        artist = artist
    elif channel_id in overrides["by_id"]:
        artist = overrides["by_id"][channel_id]
    elif channel in overrides["by_name"]:
        artist = overrides["by_name"][channel_id]
    else:
        artist = channel

    downloaded_file = f"{download_dir}/{os.listdir(download_dir)[0]}"
    print(f"downloaded to {downloaded_file}")

    audiofile = eyed3.load(downloaded_file)
    audiofile.tag.artist = artist

    thumbnail_url = metadata["thumbnail"]
    imagedata = urlopen(thumbnail_url).read()
    mimetype, _encoding = mimetypes.guess_type(thumbnail_url)
    audiofile.tag.images.set(
        type_=3,
        img_data=imagedata,
        mime_type=mimetype,
    )
    print(f"inferred mimetype: {mimetype} from url: {url}")

    if title != None:
        audiofile.tag.title = title

    audiofile.tag.save()
    return downloaded_file


if __name__ == "__main__":
    url = sys.argv[1]
    print(f"downloading {url}")

    title = sys.argv[2] if len(sys.argv) > 2 else None

    file_path = download(url, "/tmp/music", "channel_overrides.json", title=title)

    print(f"downloaded to {file_path}")
