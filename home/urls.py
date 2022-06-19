from django.urls import path
from .import views # "." means same directory

urlpatterns = [
    path('',views.index, name="index"),
    path('video/<str:video_id>',views.videoplayer, name="videoplayer"),
    path('video-link',views.videolink, name="videolink"),
    path('video-form/<str:video_id>',views.videoform, name="videoform"),
    path('audio-form/<str:audio_id>',views.audioform, name="audioform"),
    path('comment',views.commentform, name="commentform"),
]
