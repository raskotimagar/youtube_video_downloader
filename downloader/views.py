import os
import uuid
import yt_dlp
from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from .forms import YouTubeForm

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_video(request):
    if request.method == 'POST':
        form = YouTubeForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            try:
                filename = str(uuid.uuid4()) + '.mp4'
                output_path = os.path.abspath(os.path.join(DOWNLOAD_DIR, filename))

                # Use yt-dlp directly within Python
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': output_path,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    result = ydl.download([url])

                # Check if the file was created
                if not os.path.exists(output_path):
                    return HttpResponse("File not found.", status=500)

                # Send the video file directly to the browser as a download
                response = FileResponse(open(output_path, 'rb'), as_attachment=True, filename='video.mp4')
                response['Content-Type'] = 'video/mp4'
                return response

            except Exception as e:
                return HttpResponse(f"<h2>Error:</h2><pre>{str(e)}</pre>", status=500)
    else:
        form = YouTubeForm()

    return render(request, 'downloader/index.html', {'form': form})
