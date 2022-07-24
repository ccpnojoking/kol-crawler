import re
import sys
import os
import random
import time
from bs4 import BeautifulSoup as bs
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(DIR + '/../utils')

from youtube_utils import YouTubeInfo

MAX_LOAD_COUNT = 10
MAX_RETRY_COUNT = 2


class CrawlYoutube:

    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    @staticmethod
    def time_sleep(min_seconds, max_seconds):
        time.sleep(random.randint(min_seconds, max_seconds))
        return

    @staticmethod
    def init_chromedriver():
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(
            options=options,
            executable_path='/Users/caibusi/Desktop/projects/kol-crawler/kol_youtube/chromedriver'
        )

    def load_webpage(self, driver, height):
        for retry in range(MAX_RETRY_COUNT):
            driver.execute_script('window.scrollTo(0, %s)' % (height - 10))
            self.time_sleep(1, 3)
            driver.execute_script('window.scrollTo(0, %s)' % (height + 10))
            self.time_sleep(1, 3)
            driver.execute_script('window.scrollTo(0, document.documentElement.scrollHeight)')
            self.time_sleep(1, 3)
            new_height = driver.execute_script("return action=document.documentElement.scrollHeight")
            if new_height > height:
                return new_height
            self.logger.info(f'height: {height}, retry count: {retry + 1}.')
        return height

    def get_video_id_from_search_list(self, keyword):
        driver = self.init_chromedriver()
        try:
            url = f'https://www.youtube.com/results?search_query={keyword}&sp=EgIIBQ%253D'
            driver.set_page_load_timeout(60)
            driver.get(url)
            driver.maximize_window()
            self.time_sleep(2, 4)
            height = self.load_webpage(driver, height=100)
            self.logger.info(f'key word: {keyword}, crawl search list job start, height: {height}.')
            for load_count in range(MAX_LOAD_COUNT):
                new_height = self.load_webpage(driver, height)
                if new_height == height:
                    break
                height = new_height
                self.logger.info(f'key word: {keyword}, height: {height}, load count: {load_count + 2}.')
            page = str(bs(driver.page_source, 'lxml'))
            a_tag = '<a aria-label=".*?" class="yt-simple-endpoint style-scope ytd-video-renderer" href="/watch\?v=(.*?)" id="video-title"'
            video_ids = re.findall(a_tag, page)
            video_ids = list(set(video_ids))
            self.logger.info(f'key word: {keyword}, videos count: {len(video_ids)}.')
            driver.quit()
            return video_ids
        except Exception as e:
            driver.quit()
            raise Exception(str(e))

    @staticmethod
    def extract_upload_at(video_info):
        upload_at = video_info['items'][0]['snippet']['publishedAt'].split('.')[0]
        upload_at = re.findall(r'\d*-\d*-\d*T\d*:\d*:\d*', upload_at)[0]
        return datetime.strptime(upload_at, '%Y-%m-%dT%H:%M:%S')

    @staticmethod
    def extract_emails(description):
        emails = re.findall(r"[a-zA-Z0-9.\-+_]+@[a-zA-Z0-9.\-+_]+\.[a-zA-Z]+", description)
        return list(set(emails))

    @staticmethod
    def handle_exception_in_statistics(video_info, statistic_name):
        try:
            return int(video_info['items'][0]['statistics'][statistic_name])
        except:
            return 0

    @staticmethod
    def get_playlist_info(uploads_id, youtube_data_api_key):
        status, uploads_info = YouTubeInfo.search_playlist_info(
            uploads_id,
            youtube_data_api_key,
            10,
            snippet=['resourceId(videoId)']
        )
        if not status:
            return False, uploads_info
        uploads_video_id = [i['snippet']['resourceId']['videoId'] for i in uploads_info['items']]
        return True, uploads_video_id

    def get_video_info_from_api(self, video_id, youtube_data_api_key):
        status, video_info = YouTubeInfo.search_video_info(
            video_id,
            youtube_data_api_key,
            snippet=['title', 'description', 'publishedAt', 'channelId'],
            statistics=[]
        )
        if not status:
            return False, video_info
        upload_at = self.extract_upload_at(video_info)
        author_id = video_info['items'][0]['snippet']['channelId']
        title = video_info['items'][0]['snippet']['title']
        description = video_info['items'][0]['snippet']['description']
        emails = self.extract_emails(description)
        views = self.handle_exception_in_statistics(video_info, 'viewCount')
        comments = self.handle_exception_in_statistics(video_info, 'commentCount')
        likes = self.handle_exception_in_statistics(video_info, 'likeCount')
        dislikes = self.handle_exception_in_statistics(video_info, 'dislikeCount')
        return True, {
            'video_id': video_id,
            'title': title,
            'description': description,
            'views': views,
            'comments': comments,
            'likes': likes,
            'dislikes': dislikes,
            'upload_at': upload_at,
            'author_id': author_id,
            'emails': emails
        }

    def get_author_info_from_api(self, author_id, youtube_data_api_key, emails):
        status, author_info = YouTubeInfo.search_channel_info(
            author_id,
            youtube_data_api_key,
            snippet=['title', 'description', 'country'],
            contentDetails=['relatedPlaylists(uploads)'],
            statistics=['subscriberCount']
        )
        if not status:
            return False, author_info
        name = author_info['items'][0]['snippet']['title']
        description = author_info['items'][0]['snippet']['description']
        email = re.findall(r"[a-zA-Z0-9.\-+_]+@[a-zA-Z0-9.\-+_]+\.[a-zA-Z]+", description)
        emails.extend(email)
        new_emails = self.extract_emails(description)
        emails.extend(new_emails)
        country_code = author_info['items'][0]['snippet'].get('country', 'unknown')
        uploads_id = author_info['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        subscribers = self.handle_exception_in_statistics(author_info, 'subscriberCount')
        return True, {
            'author_id': author_id,
            'name': name,
            'description': description,
            'country_code': country_code,
            'uploads_id': uploads_id,
            'subscribers': subscribers,
            'emails': list(set(emails))
        }



def main():
    job = CrawlYoutube()
    # job.get_video_id_from_search_list('hello')
    # video_info = job.get_video_info_from_api('qUU9H5Yt1n8', 'AIzaSyDHeKGmD2mkdtxwuljBDUScOP4vn4xTElk')
    # print(video_info)
    # channel_info = job.get_author_info_from_api('UC55ahPQ7m5iJdVWcOfmuE6g', 'AIzaSyDHeKGmD2mkdtxwuljBDUScOP4vn4xTElk', [])
    # print(channel_info)
    uploads = job.get_playlist_info('UU55ahPQ7m5iJdVWcOfmuE6g', 'AIzaSyDHeKGmD2mkdtxwuljBDUScOP4vn4xTElk')
    print(uploads)


if __name__ == '__main__':
    main()
