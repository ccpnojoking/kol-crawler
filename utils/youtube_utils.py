import os
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(DIR + '/../utils')

# from redis_utils import RedisUtils
from http_utils import HttpUtils


class YouTubeInfo:

    @staticmethod
    def search_video_info(video_id, api_key, **kwargs):
        items = []
        part = []
        for key, value in kwargs.items():
            item = key
            if value:
                item = '{}({})'.format(key, ','.join(value))
            items.append(item)
            part.append(key)
        video_info_url = 'https://www.googleapis.com/youtube/v3/videos' \
                         '?' \
                         'id={}' \
                         '&' \
                         'key={}' \
                         '&' \
                         'fields=items({})' \
                         '&' \
                         'part={}'.format(video_id, api_key, ','.join(items), ','.join(part))
        status, response = HttpUtils.request_get(video_info_url)
        if not status:
            return False, None
        video_info = response.json()
        if not video_info.get('error'):
            return True, video_info
        return False, video_info['error']['message']

    @staticmethod
    def search_channel_info(channel_id, api_key, **kwargs):
        items = []
        part = []
        for key, value in kwargs.items():
            item = key
            if value:
                item = '{}({})'.format(key, ','.join(value))
            items.append(item)
            part.append(key)
        channel_info_url = 'https://www.googleapis.com/youtube/v3/channels' \
                           '?' \
                           'id={}' \
                           '&' \
                           'key={}' \
                           '&' \
                           'fields=items({})' \
                           '&' \
                           'part={}'.format(channel_id, api_key, ','.join(items), ','.join(part))
        status, response = HttpUtils.request_get(channel_info_url)
        if not status:
            return False, None
        channel_info = response.json()
        if not channel_info.get('error'):
            return True, channel_info
        return False, channel_info['error']['message']

    @staticmethod
    def search_playlist_info(uploads_id, api_key, max_results, **kwargs):
        items = []
        part = []
        for key, value in kwargs.items():
            item = key
            if value:
                item = '{}({})'.format(key, ','.join(value))
            items.append(item)
            part.append(key)
        uploads_info_url = 'https://www.googleapis.com/youtube/v3/playlistItems' \
                           '?' \
                           'playlistId={}' \
                           '&' \
                           'key={}' \
                           '&' \
                           'fields=items({})' \
                           '&' \
                           'part={}' \
                           '&' \
                           'maxResults={}'.format(uploads_id, api_key, ','.join(items), ','.join(part), max_results)
        status, response = HttpUtils.request_get(uploads_info_url)
        if not status:
            return False, None
        uploads_info = response.json()
        if not uploads_info.get('error'):
            return True, uploads_info
        return False, uploads_info['error']['message']


# class YouTubeUtils(YouTubeInfo):
#
#     def __init__(self) -> None:
#         self.redis_client = RedisUtils.get_buzzbreak_event_redis_client()
#
#     def increment(self, api_key):
#         is_existed = self.redis_client.exists(f'youtube_api_key:{api_key}:count')
#         if not is_existed:
#             self.redis_client.set(f'youtube_api_key:{api_key}:count', 0, ex=24 * 60 * 60)
#         self.redis_client.incr(f'youtube_api_key:{api_key}:count')
#
#     def rate_limited(self, api_key):
#         calls_count = int(self.redis_client.get(f'youtube_api_key:{api_key}:count') or 0)
#         return calls_count > 5000
#
#     def invalid_key(self, api_key):
#         self.redis_client.set(f'youtube_api_key:{api_key}:count', 10000, ex=24 * 60 * 60)


def main():
    youtube_info = YouTubeInfo()
    res = youtube_info.search_video_info(
        'RzGwfyGOFaM',
        'AIzaSyDBj1U8vzMxS-JWbwFfja-dsmiQ0Sjqtr8',
        snippet=['channelId', 'title', 'description', 'channelTitle', 'thumbnails'],
        contentDetails=['duration'],
        statistics=['viewCount']
    )
    print(res)
    # res = youtube_info.search_channels_info(
    #     'UCm141bdC7ywK_F3TgGbYMUA',
    #     'AIzaSyDHeKGmD2mkdtxwuljBDUScOP4vn4xTElk',
    #     snippet=['title', 'description'],
    #     contentDetails=['relatedPlaylists'],
    #     statistics=['viewCount', 'commentCount', 'subscriberCount', 'videoCount']
    # )
    # print(res)
    # res = youtube_info.search_playlist_info(
    #     'UUm141bdC7ywK_F3TgGbYMUA',
    #     'AIzaSyDHeKGmD2mkdtxwuljBDUScOP4vn4xTElk',
    #     10,
    #     snippet=['publishedAt', 'title', 'description', 'thumbnails'],
    #     contentDetails=[]
    # )
    # print(res)


if __name__ == '__main__':
    main()
