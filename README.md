# YouTube Video Downloader 🎥

A simple Django-based web application to download YouTube videos in MP4 format.

## Features

- 🎯 Download individual YouTube videos (no playlists)
- ⚙️ Background video download with progress tracking (via HTMX + Django cache)
- 💾 Video is downloaded directly to the user's browser (not stored in DB)
- 🔥 Auto-cleanup of temporary files from the server

## Tech Stack

- Python 🐍
- Django 🧩
- yt-dlp 🎬
- Docker (optional for deployment)

## Setup Instructions

1. **Clone the repo:**

```bash
git clone https://github.com/raskotimagar/youtube_video_downloader.git
cd youtube_video_downloader
