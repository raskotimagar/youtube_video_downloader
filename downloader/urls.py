from django.urls import path
from . import views

urlpatterns = [
    path('', views.download_video, name='download'),
    path('download/progress/', views.download_progress, name='download_progress'),
    path('download/file/<str:filename>/', views.download_file, name='download_file'),
]