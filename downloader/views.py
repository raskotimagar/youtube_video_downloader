import os
import uuid
import yt_dlp
import threading
from django.shortcuts import render
from django.http import JsonResponse, FileResponse, HttpResponse
from django.core.cache import cache
from .forms import YouTubeForm

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_video(request):
    if request.method == 'POST':
        form = YouTubeForm(request.POST)
        if form.is_valid():
            raw_url = form.cleaned_data['url']
            clean_url = raw_url.split('&list=')[0].split('?feature=')[0]
            
            if '/playlist' in clean_url:
                return JsonResponse({'error': 'Playlist URLs are not supported'}, status=400)

            task_id = str(uuid.uuid4())
            cache.set(task_id, {
                'status': 'pending',
                'progress': '0%',
                'filename': None,
                'error': None
            }, 300)

            threading.Thread(target=download_task, args=(clean_url, task_id)).start()
            return JsonResponse({'task_id': task_id})
        
        return JsonResponse({'error': 'Invalid form data'}, status=400)
    
    return render(request, 'downloader/index.html', {'form': YouTubeForm()})

def download_task(url, task_id):
    final_filename = None

    def progress_hook(d):
        nonlocal final_filename
        if d['status'] == 'downloading':
            cache.set(task_id, {
                'status': 'downloading',
                'progress': d.get('_percent_str', '0%'),
                'filename': None,
                'error': None
            }, 300)
        elif d['status'] == 'finished':
            # Store final filename after merging
            if '_final_filename' in d:
                final_filename = os.path.basename(d['_final_filename'])
                cache.set(task_id, {
                    'status': 'completed',
                    'progress': '100%',
                    'filename': final_filename,
                    'error': None
                }, 300)

    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'progress_hooks': [progress_hook],
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'keepvideo': False,  # Clean up temp files
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            final_filename = ydl.prepare_filename(info)
            
            # Manually trigger completion for merged file
            progress_hook({
                'status': 'finished',
                '_final_filename': final_filename
            })

    except Exception as e:
        cache.set(task_id, {
            'status': 'error',
            'progress': '0%',
            'filename': None,
            'error': f'Download failed: {e}'
        }, 300)

def download_progress(request):
    task_id = request.GET.get('task_id')
    if not task_id:
        return JsonResponse({'error': 'Missing task_id'}, status=400)
    
    data = cache.get(task_id, {'status': 'not_found'})
    return JsonResponse(data)

def download_file(request, filename):
    if '..' in filename or filename.startswith('/'):
        return HttpResponse("Invalid filename", status=400)
    
    file_path = os.path.join(DOWNLOAD_DIR, filename.split('?')[0])  # Remove cache-busting param
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f'attachment; filename="video.mp4"'
        return response
    return HttpResponse("File not found", status=404)