from ytmusicapi import YTMusic

def YouTubeMusicSearch(keyword: str) -> str:
    ytmusic = YTMusic()
    search_results = ytmusic.search(keyword)
    audio_result = search_results[1]
    video_id = None
    if search_results[0].get('category') == 'Top result' and search_results[0].get('resultType') == 'video' :
        video_id = search_results[0]['videoId']
    return audio_result['videoId'], video_id