import os
import sys
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(DIR)
sys.path.append(DIR + '/../utils')

from crawl_task_sheet import CrawlTaskSheet
from crawl_youtube import CrawlYoutube
from db_utils import DbClient
from logger_utils import Logger


class KOLHub:

    def __init__(self, is_teat=False):
        super().__init__()
        self.logger = Logger('kol hub', os.path.join(DIR, 'logs/kol_hub.log'))
        self.db_client = DbClient(self.logger, test_only=is_teat)

    def insert_keyword(self, keyword_info, belong_to):
        """
        keywords
        default(insert):
        1. keyword;
        2. source;
        3. is_crawled(init);
        4. updated_at;
        5. belong_to;
        6. repeated_count;
        7. order_by_method(相关性);
        :return:
        """
        keyword = {
            'keyword': keyword_info['keyword'],
            'source': 'youtube',
            'is_crawled': 'init',
            'updated_at': datetime.utcnow(),
            'belong_to': keyword_info['belong_to'] if keyword_info['belong_to'] else belong_to,
            'order_by_method': keyword_info['order_by_method']
        }
        keyword_in_db = self.db_client.find_keyword(
            keyword['keyword'], keyword['source']
        )
        keyword['repeated_count'] = keyword_in_db['repeated_count'] + 1 if keyword_in_db else 1
        self.db_client.update_keyword(
            keyword['keyword'], keyword['source'], keyword
        )
        self.logger.info(keyword)
        return True

    def insert_video(self, video_id, keyword, belong_to, repeated_count):
        """
        videos
        default(insert):
        1. video_id;
        2. source;
        3. is_crawled(init);
        4. created_at;
        5. keyword;
        6. belong_to;
        7. origin_url;
        8. keyword_repeated_count;
        :return:
        """
        video = {
            'video_id': video_id,
            'source': 'youtube',
            'is_crawled': 'init',
            'created_at': datetime.utcnow(),
            'keyword': keyword,
            'belong_to': belong_to,
            'origin_url': f'https://www.youtube.com/watch?v={video_id}',
            'keyword_repeated_count': repeated_count
        }
        video_in_db = self.db_client.find_video(video['video_id'], 'youtube')
        if video_in_db:
            return False
        self.db_client.insert_video(video)
        self.logger.info(video)
        return True

    def insert_author(self, author_id, belong_to, emails, keyword, video_details):
        """
        default(insert):
        1. author_id;
        2. source;
        3. is_crawled(init);
        4. created_at;
        5. belong_to;
        6. origin_url;
        :return:
        """
        author_in_db = self.db_client.find_author(author_id, 'youtube')
        if author_in_db:
            return False
        author = {
            'author_id': author_id,
            'keyword': keyword,
            'source': 'youtube',
            'is_crawled': 'init',
            'created_at': datetime.utcnow(),
            'belong_to': belong_to,
            'origin_url': f'https://www.youtube.com/channel/{author_id}',
            'emails': emails,
            'video_details': video_details
        }
        self.db_client.insert_author(author)
        self.logger.info(author)
        return True

    def update_youtube_api_key(self, youtube_api_key, status, response):
        if not response:
            return False
        if not status:
            self.db_client.update_youtube_api_key(
                youtube_api_key['api_key'], {'limit': 0, 'error': response}
            )
            return False
        limit = youtube_api_key['limit'] - 1
        self.db_client.update_youtube_api_key(
            youtube_api_key['api_key'], {'limit': limit}
        )
        return True

    def get_keyword_task(self, belong_to):
        sheet_info = self.db_client.get_google_sheet_id(belong_to, 'keywords')
        sheet_id = sheet_info['sheet_id']
        crawler = CrawlTaskSheet()
        keywords = crawler.get_keywords(sheet_id)
        self.logger.info(f'keyword count: {len(keywords)}')
        for keyword in keywords:
            self.insert_keyword(keyword, belong_to)

    def get_video_task_from_keyword(self):
        """
        keywords(update)
        crawled(success):
        1. is_crawled(success);
        2. updated_at;

        crawled(failed):
        1. is_crawled(failed);
        2. updated_at;
        :return:
        """
        crawler = CrawlYoutube(self.logger)
        keywords = self.db_client.find_keywords(
            {'source': 'youtube', 'is_crawled': 'init'}
        )
        for keyword in keywords:
            video_ids = []
            try:
                video_ids = crawler.get_video_id_from_search_list(keyword['keyword'])
                is_crawled = 'success'
            except Exception as e:
                self.logger.error(f'crawl keyword: {keyword["keyword"]} failed, information: {str(e)}')
                is_crawled = 'failed'
            self.db_client.update_keyword(
                keyword['keyword'],
                'youtube',
                {'is_crawled': is_crawled, 'updated_at': datetime.utcnow()}
            )
            if not video_ids:
                continue
            insert_result = [
                self.insert_video(video_id, keyword['keyword'], keyword['belong_to'], keyword['repeated_count'])
                for video_id in video_ids
            ]
            self.logger.info(
                f'keyword: {keyword["keyword"]}, repeated_count: {keyword["repeated_count"]}, '
                f'insert videos count: {sum(insert_result)}')

    def get_author_task_from_video(self):
        """
        videos(update)
        crawled(success):
        1. title;
        2. description;
        3. likes;
        4. dislikes;
        5. views;
        6. comments;
        7. uploaded_at;
        8. is_crawled(success);
        9. updated_at;
        10. author_id;

        crawled(failed):
        1. is_crawled(failed);
        2. updated_at;
        :return:
        """
        crawler = CrawlYoutube(self.logger)
        videos = self.db_client.find_videos(
            {'source': 'youtube', 'is_crawled': 'init'}
        )
        for video in videos:
            youtube_api_key = self.db_client.get_youtube_api_key()
            if not youtube_api_key:
                continue
            video_info = {}
            try:
                status, video_info = crawler.get_video_info_from_api(video['video_id'], youtube_api_key['api_key'])
                is_useful = self.update_youtube_api_key(youtube_api_key, status, video_info)
                if not is_useful:
                    continue
                crawl_result = video_info
                crawl_result['is_crawled'] = 'success'
            except Exception as e:
                self.logger.error(f'crawl video: {video["video_id"]} failed, information: {str(e)}')
                crawl_result = {'is_crawled': 'failed'}
            crawl_result['updated_at'] = datetime.utcnow()
            self.db_client.update_video(video['video_id'], 'youtube', crawl_result)
            if not video_info:
                continue
            video_details = {
                'origin_url': video['origin_url'],
                'views': video_info['views'],
                'likes': video_info['likes'],
                'dislikes': video_info['dislikes'],
                'comments': video_info['comments'],
                'upload_at': video_info['upload_at']
            }
            self.insert_author(
                video_info['author_id'], video['belong_to'], video_info['emails'], video['keyword'], video_details)

    # 抓取作者详细信息
    def get_author_details(self, author):
        crawler = CrawlYoutube(self.logger)
        youtube_api_key = self.db_client.get_youtube_api_key()
        if not youtube_api_key:
            return False, None
        try:
            status, author_info = crawler.get_author_info_from_api(
                author['author_id'], youtube_api_key['api_key'], author['emails'])
            is_useful = self.update_youtube_api_key(youtube_api_key, status, author_info)
            if not is_useful:
                return False, None
        except Exception as e:
            self.logger.error(f'crawl author: {author["author_id"]} failed, information: {str(e)}')
            self.db_client.update_author(
                author['author_id'],
                'youtube',
                {'is_crawled': 'failed', 'updated_at': datetime.utcnow()}
            )
            return False, None
        return True, author_info

    # 抓取最近发布的10个作品
    def get_upload_videos(self, author_id, uploads_id):
        crawler = CrawlYoutube(self.logger)
        youtube_api_key = self.db_client.get_youtube_api_key()
        if not youtube_api_key:
            return False, None
        try:
            status, upload_videos = crawler.get_playlist_info(uploads_id, youtube_api_key['api_key'])
            is_useful = self.update_youtube_api_key(youtube_api_key, status, upload_videos)
            if not is_useful:
                return False, None
        except Exception as e:
            self.logger.error(f'crawl uploads: {uploads_id} failed, information: {str(e)}')
            self.db_client.update_author(
                author_id,
                'youtube',
                {'is_crawled': 'failed', 'updated_at': datetime.utcnow()}
            )
            return False, None
        return True, upload_videos

    # 抓取每个视频的元数据
    def get_uploads_detail(self, author_id, uploads):
        crawler = CrawlYoutube(self.logger)
        try:
            videos = []
            for video in uploads:
                youtube_api_key = self.db_client.get_youtube_api_key()
                if not youtube_api_key:
                    continue
                status, video_info = crawler.get_video_info_from_api(video, youtube_api_key['api_key'])
                is_useful = self.update_youtube_api_key(youtube_api_key, status, video_info)
                if not is_useful:
                    continue
                videos.append(video_info)
            views_list = [video['views'] for video in videos]
            comments_list = [video['comments'] for video in videos]
        except Exception as e:
            self.logger.error(f'crawl uploads: {uploads} failed, information: {str(e)}')
            self.db_client.update_author(
                author_id,
                'youtube',
                {'is_crawled': 'failed', 'updated_at': datetime.utcnow()}
            )
            return False, None
        return True, {'views_list': views_list, 'comments_list': comments_list}

    def update_author_details(self):
        """
        authors(update)
        crawled(success):
        1. name;
        2. description;
        3. country_code;
        4. emails;
        5. subscribers;

        6. views_list;
        7. comments_list;
        8. videos_count;
        9. is_crawled(success);
        10 updated_at;

        crawled(failed):
        1. is_crawled(failed);
        2. updated_at;

        :return:
        """
        authors = self.db_client.find_authors({'is_crawled': 'init', 'source': 'youtube'})
        for author in authors:
            status, author_details = self.get_author_details(author)
            if not status:
                continue
            status, upload_videos = self.get_upload_videos(author_details['author_id'], author_details['uploads_id'])
            if not status:
                continue
            status, uploads_detail = self.get_uploads_detail(author_details['author_id'], upload_videos)
            if not status:
                continue
            author_details['views_list'] = uploads_detail['views_list']
            author_details['comments_list'] = uploads_detail['comments_list']
            author_details['videos_count'] = len(upload_videos)
            author_details['is_crawled'] = 'success'
            author_details['updated_at'] = datetime.utcnow()
            author_details['is_shown'] = False
            self.db_client.update_author(author_details['author_id'], 'youtube', author_details)
            self.logger.info(author_details)

    def reset_youtube_api_limit(self):
        youtube_api_keys = self.db_client.find_youtube_api_key()
        for api_key in youtube_api_keys:
            self.db_client.update_youtube_api_key(
                api_key['api_key'], {'limit': 5000}
            )

    def run(self, belong_to):
        self.get_keyword_task(belong_to)
        self.get_video_task_from_keyword()
        self.get_author_task_from_video()
        self.update_author_details()


def main():
    kol_job = KOLHub()
    operators = ['elon', 'kevin', 'blue', 'jinglong', 'yunsoon']
    for operator in operators:
        kol_job.run(operator)
    kol_job.reset_youtube_api_limit()


if __name__ == '__main__':
    main()
