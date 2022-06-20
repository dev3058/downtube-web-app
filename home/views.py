from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import BadRequest
from pytube import YouTube
from pytube import Search
from django.template.loader import render_to_string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from .forms import SearchForm, linkSearchForm, FeedbackForm
from django.shortcuts import redirect, render
from .models import ObjHandler, PopularChannel
from django.utils.text import Truncator
from django.utils import timezone
import requests
import re
import os
import string
from .spotify_link_handler import SpotifyLinkHandler
from .youtube_music_handler import YouTubeMusicSearch

# Create your views here.
def popular_content(num):
    id_list = []
    api_response = 'https://www.googleapis.com/youtube/v3/videos?part=contentDetails&chart=mostPopular&regionCode=IN&maxResults={}&key={}'.format(num,settings.YOUTUBE_API_KEY)
    result = requests.get(api_response).json()
    for a in range(num):
        id_list.append(result['items'][a]['id'])
    return id_list

def yt_obj_fun(id_list=['dummy'],v_link=False,all_data = False):
    yt_obj_list = []
    for vid in id_list:
        link = 'https://www.youtube.com/watch?v={}'.format(vid) if not v_link else v_link 
        try:
            yt_obj = YouTube(link)
        except:
            return False
        if len(id_list) > 1:
            ObjHandler.objects.create(title = yt_obj.title,video_id = yt_obj.video_id, author = yt_obj.author,publish_date = yt_obj.publish_date,views = yt_obj.views,description = Truncator(yt_obj.description).chars(250), thumbnail_url = yt_obj.thumbnail_url,length = yt_obj.length,channel_id = yt_obj.channel_id)
        yt_obj_list.append(yt_obj)
    return yt_obj_list if not all_data else ObjHandler.objects.all()

def search_data_cookie(cookie_data,data=False):
    if data is False:
        search_history = []
        if cookie_data is None:
            return search_history
        cookie_data = cookie_data[1:len(cookie_data)-1]
        cookie_data = cookie_data.split(',')
        for data in cookie_data:
            data =  data.translate(str.maketrans('', '', string.punctuation)).strip()
            search_history.append(data)
        return search_history
    if cookie_data is not None:
        cookie_data = cookie_data[1:len(cookie_data)-1]
        li = cookie_data.split(',')
    else:
        li = []
    valid_data = data.strip()
    if valid_data not in search_data_cookie(cookie_data):
        li.append(valid_data)
    return li

def index(request):
    cookie_data = request.COOKIES.get('search_data')
    db_update_test = ObjHandler.objects.all()[:1]
    db_update_test = timezone.now() - db_update_test.get().last_modified if len(db_update_test) != 0 else ''
    db_update_test = datetime.timedelta(days=2,seconds=15200)- datetime.timedelta() if db_update_test == '' else db_update_test
    if db_update_test.seconds < 16200 and db_update_test.days < 1:
        yt_objs = ObjHandler.objects.all()
    searchform = SearchForm(data=request.POST)
    template = "index.html"
    if request.method == "POST":
        if 'db_update' in request.POST:
            videos_ids = popular_content(10)
            yt_objs = ObjHandler.objects.all()
            yt_objs.delete()
            yt_objs = yt_obj_fun(videos_ids,all_data = True)
        if searchform.is_valid():   
            search_data = Search(searchform.cleaned_data.get('search_data'))
            if 'search_data' in request.POST:
                cookie_data = search_data_cookie(request.COOKIES.get('search_data'),(searchform.cleaned_data.get('search_data')).lower())
            search_data.fetch_query()
            yt_objs = search_data.results[:10]    
            template = "pages/search-results.html"
    db_update_test = 'False' if db_update_test.seconds < 16200 and db_update_test.days < 1 else 'True'
    channel_images = channel_profile_image(yt_objs) if request.method == "POST" or db_update_test == 'False' else 'False'
    response = render(request,template,context={
        'yt_obj' : yt_objs if channel_images != 'False' else 'False',
        "channel_images" : channel_images,
        "famous_video" : PopularChannel.objects.all(),
        "form" : SearchForm(),
        "linkform" : linkSearchForm(),
        "feedbackform" : FeedbackForm(),
        'search_history' : search_data_cookie(request.COOKIES.get('search_data'))
    })
    if request.method == "POST" and 'link_search_data' not in request.POST:
        response.set_cookie('search_data',cookie_data,max_age=80000)    
    return response

def channel_profile_image(yt_objs_list):
    channel_images = {}
    for obj in yt_objs_list:
        url = 'https://youtube.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id={}&key={}'.format(obj.channel_id,settings.YOUTUBE_API_KEY)
        response = requests.get(url)
        response_json = response.json()
        channel_images[obj.channel_id] = response_json["items"][0]["snippet"]["thumbnails"]["default"]["url"]
    return channel_images

def videoplayer(request,video_id = False, video_obj = False, is_shorts = False):
    id_list=[]
    id_list.append(video_id)
    yt_obj = video_obj if video_obj else yt_obj_fun(id_list)
    channel_image = channel_profile_image(yt_obj)
    return render(request,"pages/video-single.html",context={
        'yt_obj' : yt_obj[0],
        'high_resol' : yt_obj[0].streams.get_by_itag(399),
        'channel_image' : channel_image[yt_obj[0].channel_id],
        'shorts' : 'True' if is_shorts else 'False'
    })

def audiohandler(request, audio_link, spotify = False):
    try:
        link_data =  SpotifyLinkHandler(audio_link) if spotify else YouTube(audio_link)
    except:
        message = "Wrong {} Link Detected".format('Spotify' if spotify else 'YouTube Music')
        messages.warning(request,message)
        raise BadRequest 
    else:
        search_keyword = (link_data["name"] + " " + link_data["album"] if link_data["name"] != link_data["album"] else link_data["name"] + " " + link_data["artists_list"][0] ) if spotify else link_data.title
        print(search_keyword)
        song_id, video_id = YouTubeMusicSearch(search_keyword)
        return render(request,"pages/audio-player.html",context={
                'track_name' : link_data['name'] if spotify else link_data.title,
                'song_image' : link_data["song_image"] if spotify else link_data.thumbnail_url,
                'artists_list' : link_data["artists_list"] if spotify else [link_data.author],
                'release_date' : link_data["release_date"] if spotify else datetime.date(link_data.publish_date),
                'video_id' : video_id if video_id else None,
                'audio_id' : song_id,
                'duration' : link_data['length'] if spotify else round(link_data.length/60),
            })

def videolink(request):
    if request.method == "POST":
        linkform = linkSearchForm(data=request.POST)
        is_shorts = False
        if 'link_search_data' in request.POST and linkform.is_valid():
            link_data = linkform.cleaned_data.get('link_search_data')
            if '/shorts/' in link_data :
                link_data = link_data.replace('/shorts/','/watch?v=')
                is_shorts = True
            elif 'spotify.com/track/' in link_data: 
                return audiohandler(request, link_data, spotify=True)
            elif 'music.youtube' in link_data:
                return audiohandler(request, link_data, spotify=False) 
            yt_objs =  yt_obj_fun(v_link = link_data)
            if yt_objs is False:
                messages.warning(request,'Wrong YouTube Link Detected')
                raise BadRequest
            return videoplayer(request,video_obj=yt_objs,is_shorts = is_shorts) 
    return redirect('/')

def audioform(request,audio_id):
    yt_obj = YouTube('https://www.youtube.com/watch?v={}'.format(audio_id))
    response = request.POST
    stream_id = int(response.get('audioformoptions'))
    stream = yt_obj.streams.get_by_itag(stream_id)
    if stream.filesize > 31457280:
        messages.warning(request,'File Size Out of Box')
        raise BadRequest
    out_filename = re.sub('[^A-Za-z0-9]+', ' ', yt_obj.title)[:20]+'.mp3'
    filename = 'DownTubeAudio' + '.mp3'
    fs = FileSystemStorage(os.path.abspath(''))  
    stream.download(output_path='{}/downloads/audio'.format(os.path.abspath('')), filename = filename)
    file_path = "downloads/audio/{}".format(filename)  
    with fs.open(file_path) as audio:
        response = HttpResponse(audio, content_type='audio/mpeg3')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(out_filename)
    return response
        
def videoform(request,video_id):
    yt_obj = YouTube('https://www.youtube.com/watch?v={}'.format(video_id))
    response = request.POST
    stream_id = 18 #resolution 360px
    if response.get('videoformoptions') == '720px':
        stream_id = 22 #resolution 720px  
    elif response.get('videoformoptions') == '1080px':
        stream_id = 399 #resolution 1080px 
     
    stream = yt_obj.streams.get_by_itag(stream_id)
    if stream.filesize > 60817408:
        messages.warning(request,'File Size Out of Box')
        raise BadRequest
    out_filename = re.sub('[^A-Za-z0-9]+', ' ', yt_obj.title)[:20]+'.mp4'
    filename = 'DownTubeVideo' + '.mp4'
    fs = FileSystemStorage(os.path.abspath(''))  
    stream.download(output_path='{}/downloads/video'.format(os.path.abspath('')), filename = filename)
    file_path = "downloads/video/{}".format(filename)   
    with fs.open(file_path) as video:
        response = HttpResponse(video, content_type='video/mp4')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(out_filename)
    return response

def mailserver(request,receiver,full_name,subject,message):
    email_subject = '🚀 DownTube | Thanks for your Feedback'
    email_body = render_to_string('pages/feedback-conformation-mail.html',{
        'full_name' : full_name,
        'subject' : subject,
        'content' : message,
        'email' : receiver,
    })
    message = Mail(
        from_email=settings.EMAIL_SERVER_HANDLER,
        to_emails=[receiver],
        subject=email_subject,
        html_content=email_body,
        )
    try:    
        email = SendGridAPIClient(settings.SENDGRID_API_KEY)
        email.send(message)
        messages.info(request,'Thanks for your Feedback')
        return render(request,"pages/about-errors.html",{'success':'Request Accepted Successfully'})

    except Exception as error:
        messages.warning(request,'Something Went Wrong')
        return custom_error_view(request, exception=error)

def commentform(request):
    feedbackform = FeedbackForm(data=request.POST)
    if request.method == "POST":
        if feedbackform.is_valid():
            return mailserver(request,feedbackform.cleaned_data.get('email'),feedbackform.cleaned_data.get('full_name')
            ,feedbackform.cleaned_data.get('subject'),feedbackform.cleaned_data.get('comment_area'),)

def custom_page_not_found_view(request, exception):
    messages.warning(request,'Resources you are looking for currently unavailable.')
    return render(request, "pages/about-errors.html", {'error':'Error_404_Not_Found','exception' : exception})

def custom_error_view(request, exception=None):
    messages.warning(request,'Internal Error Occur, Try Again.')
    return render(request, "pages/about-errors.html", {'error':'Error_500_Internal_Error','exception' : exception})

def custom_permission_denied_view(request, exception=None):
    messages.warning(request,'Unauthorise Access detected from your end.')
    return render(request, "pages/about-errors.html", {'error':'Error_403_Permsission_Denied','exception' : exception})

def custom_bad_request_view(request, exception=None):
    return render(request, "pages/about-errors.html", {'error':'Error_400_Bad_Request','exception' : exception})