FROM python:3.12 
RUN apt-get update -qq && apt-get install ffmpeg -y
RUN pip install yt-dlp eyeD3 discord python-dotenv requests
ADD main.py downloader.py ./
CMD ["python", "main.py"] 