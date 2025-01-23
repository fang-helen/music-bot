FROM python:3.12 
RUN apt-get update -qq && apt-get install ffmpeg -y
RUN pip install yt-dlp eyeD3 discord python-dotenv
ADD main.py downloader.py channel_overrides.json ./
CMD ["python", "main.py"] 