from pyexpat import model
from statistics import mode
from django.db import models
from pytube import YouTube
from django.conf import settings
import requests

# Create your models here.
class ObjHandler(models.Model):
    title = models.CharField(max_length=100, blank=True)
    video_id = models.CharField(max_length=50,blank=True)
    channel_id = models.CharField(max_length=50,blank=True)
    author = models.CharField(max_length=50, blank=True)
    publish_date = models.DateTimeField()
    views = models.BigIntegerField(blank=True)
    description = models.TextField(max_length=1000,blank=True)
    thumbnail_url = models.URLField(blank=True)
    length = models.IntegerField(blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class PopularChannel(models.Model):
    choices = [
        ('Popular Song','Song'),
        ('Popular Video','Video')
    ]
    channel_category = models.CharField(max_length=100,choices=choices)
    channel_video_link = models.CharField(max_length=100,blank=True)
    channel_name = models.CharField(max_length=100,blank=True,editable=False)
    channel_image = models.CharField(max_length=100,blank=True,editable=False)

    def save(self, *args, **kwargs):
        yt_obj = YouTube(self.channel_video_link)
        url = 'https://youtube.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id={}&key={}'.format(yt_obj.channel_id,settings.YOUTUBE_API_KEY)
        response = requests.get(url)
        response_json = response.json()
        self.channel_image = response_json["items"][0]["snippet"]["thumbnails"]["default"]["url"]
        self.channel_name = yt_obj.author
        super(PopularChannel,self).save(*args,**kwargs)
        
    def __str__(self):
        return self.channel_name


    