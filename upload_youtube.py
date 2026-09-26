import os
import sys
import glob

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# ============================================================
# Environment variables
# ============================================================

CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")

VIDEO_TITLE = os.environ.get(
    "VIDEO_TITLE",
    "Uploaded Video"
)

VIDEO_DESCRIPTION = os.environ.get(
    "VIDEO_DESCRIPTION",
    ""
)

PRIVACY = os.environ.get(
    "PRIVACY",
    "private"
)


# ============================================================
# Validate environment
# ============================================================

if not CLIENT_ID:
    print("ERROR: GOOGLE_CLIENT_ID is missing.")
    sys.exit(1)

if not CLIENT_SECRET:
    print("ERROR: GOOGLE_CLIENT_SECRET is missing.")
    sys.exit(1)

if not REFRESH_TOKEN:
    print("ERROR: YOUTUBE_REFRESH_TOKEN is missing.")
    sys.exit(1)


# ============================================================
# Find downloaded video
# ============================================================

video_extensions = [
    "*.mp4",
    "*.mov",
    "*.mkv",
    "*.avi",
    "*.webm",
    "*.m4v"
]

video_files = []

for extension in video_extensions:
    video_files.extend(
        glob.glob(extension)
    )


if not video_files:
    print("ERROR: No video file found.")
    sys.exit(1)


# Use the first video found
video_file = video_files[0]


print("")
print("======================================")
print("YouTube Upload")
print("======================================")
print(f"Video file : {video_file}")
print(f"Title      : {VIDEO_TITLE}")
print(f"Privacy    : {PRIVACY}")
print("======================================")
print("")


# ============================================================
# YouTube credentials
# ============================================================

credentials = Credentials(
    token=None,
    refresh_token=REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scopes=[
        "https://www.googleapis.com/auth/youtube.upload"
    ]
)


# ============================================================
# Build YouTube API client
# ============================================================

youtube = build(
    "youtube",
    "v3",
    credentials=credentials
)


# ============================================================
# Video metadata
# ============================================================

body = {
    "snippet": {
        "title": VIDEO_TITLE,
        "description": VIDEO_DESCRIPTION,
        "categoryId": "10"
    },

    "status": {
        "privacyStatus": PRIVACY,
        "selfDeclaredMadeForKids": False
    }
}


# ============================================================
# Upload
# ============================================================

media = MediaFileUpload(
    video_file,
    chunksize=8 * 1024 * 1024,
    resumable=True
)


print("Starting YouTube upload...")
print("")


request = youtube.videos().insert(
    part="snippet,status",
    body=body,
    media_body=media
)


response = None


while response is None:

    status, response = request.next_chunk()

    if status:

        progress = int(
            status.progress() * 100
        )

        print(
            f"Upload progress: {progress}%"
        )


# ============================================================
# Result
# ============================================================

video_id = response.get("id")


if video_id:

    print("")
    print("======================================")
    print("UPLOAD SUCCESSFUL")
    print("======================================")
    print(f"Video ID: {video_id}")
    print(
        f"YouTube URL: "
        f"https://www.youtube.com/watch?v={video_id}"
    )
    print("======================================")

else:

    print("ERROR: Upload completed but no video ID returned.")
    sys.exit(1)
