import os
import glob

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["YOUTUBE_REFRESH_TOKEN"]

TITLE = os.environ["VIDEO_TITLE"]
DESCRIPTION = os.environ.get("VIDEO_DESCRIPTION", "")
PRIVACY = os.environ.get("PRIVACY", "private")


credentials = Credentials(
    None,
    refresh_token=REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scopes=["https://www.googleapis.com/auth/youtube.upload"]
)

youtube = build(
    "youtube",
    "v3",
    credentials=credentials
)


video_files = []

for pattern in ["*.mp4", "*.mov", "*.mkv", "*.webm"]:
    video_files.extend(glob.glob(pattern))

if not video_files:
    raise Exception("No video file found.")

video_file = video_files[0]

print(f"Uploading: {video_file}")
print(f"Title: {TITLE}")
print(f"Privacy: {PRIVACY}")


body = {
    "snippet": {
        "title": TITLE,
        "description": DESCRIPTION,
        "categoryId": "10"
    },
    "status": {
        "privacyStatus": PRIVACY
    }
}


media = MediaFileUpload(
    video_file,
    chunksize=8 * 1024 * 1024,
    resumable=True
)


request = youtube.videos().insert(
    part="snippet,status",
    body=body,
    media_body=media
)


response = None

while response is None:
    status, response = request.next_chunk()

    if status:
        progress = int(status.progress() * 100)
        print(f"Upload progress: {progress}%")


video_id = response["id"]

print("=" * 50)
print("UPLOAD SUCCESSFUL")
print(f"https://www.youtube.com/watch?v={video_id}")
print("=" * 50)
