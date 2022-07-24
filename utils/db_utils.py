import os
import sys
import time
from datetime import timedelta
from datetime import datetime
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import AutoReconnect
from pymongo.errors import ConnectionFailure

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(DIR + '/../utils')

from read_config import CONFIG

MAX_RETRY_TIMES = 1


class DbClient:

    def __init__(
            self,
            logger,
            test_only=False,
            read_preference='primary'
    ):
        self.read_preference = read_preference
        self.MONGO_URI = CONFIG['MONGO']['URI']
        self.logger = logger
        self.ttl = timedelta(seconds=70)
        self.test_only = test_only
        self.__set_up_db_client()

    def find_keyword(self, keyword, source):
        def __find_keyword():
            return self.readon_keywords.find_one(
                {'keyword': keyword, 'source': source}
            )
        return self.__call_with_retry(__find_keyword)

    def find_keywords(self, query):
        def __find_keywords():
            return list(self.readon_keywords.find(query))
        return self.__call_with_retry(__find_keywords)

    def update_keyword(self, keyword, source, update_field):
        def __update_keyword():
            return self.readon_keywords.update_one(
                {'keyword': keyword, 'source': source},
                {'$set': update_field},
                upsert=True
            )

        return self.__call_with_retry(__update_keyword)

    def find_video(self, video_id, source):
        def __find_videos():
            return self.readon_videos.find_one(
                {'video_id': video_id, 'source': source}
            )

        return self.__call_with_retry(__find_videos)

    def find_videos(self, query):
        def __find_videos():
            return list(self.readon_videos.find(query))

        return self.__call_with_retry(__find_videos)

    def bulk_write_videos(self, update_list):
        def __bulk_write_videos():
            self.readon_videos.bulk_write(
                update_list,
                ordered=False,
                bypass_document_validation=True
            )
        return self.__call_with_retry(__bulk_write_videos)

    def insert_video(self, video):
        def __insert_video():
            return self.readon_videos.insert_one(video)

        return self.__call_with_retry(__insert_video)

    def update_video(self, video_id, source, update_field):
        def __update_video():
            return self.readon_videos.update_one(
                {'video_id': video_id, 'source': source},
                {'$set': update_field}
            )

        return self.__call_with_retry(__update_video)

    def find_author(self, author_id, source):
        def __find_author():
            return self.readon_authors.find_one(
                {'author_id': author_id, 'source': source}
            )

        return self.__call_with_retry(__find_author)

    def find_authors(self,  query):
        def __find_authors():
            return list(self.readon_authors.find(query))

        return self.__call_with_retry(__find_authors)

    def insert_author(self, author):
        def __insert_author():
            return self.readon_authors.insert_one(author)

        return self.__call_with_retry(__insert_author)

    def update_author(self, author_id, source, update_field):
        def __update_author():
            return self.readon_authors.update_one(
                {'author_id': author_id, 'source': source},
                {'$set': update_field}
            )

        return self.__call_with_retry(__update_author)

    def get_youtube_api_key(self):
        def __get_youtube_api_key():
            return self.youtube_api_keys.find_one(
                {'limit': {'$gt': 100}}
            )

        return self.__call_with_retry(__get_youtube_api_key)

    def insert_youtube_api_key(self, api_key):
        def __insert_youtube_api_key():
            return self.youtube_api_keys.insert_one(
                {'api_key': api_key, 'limit': 5000, 'updated_at': datetime.utcnow()}
            )

        return self.__call_with_retry(__insert_youtube_api_key)

    def update_youtube_api_key(self, api_key, update_file):
        def __get_youtube_api_key():
            return self.youtube_api_keys.update_one(
                {'api_key': api_key},
                {'$set': update_file}
            )

        return self.__call_with_retry(__get_youtube_api_key)

    def get_google_sheet_id(self, name, title):
        def __get_google_sheet_id():
            return self.readon_sheets.find_one(
                {'belong_to': name, 'title': title}
            )

        return self.__call_with_retry(__get_google_sheet_id)

    def upsert_kol(self, origin_url, update_field):
        def __upsert_kol():
            return self.readon_kols.update_one(
                {'origin_url': origin_url},
                {'$set': update_field},
                upsert=True
            )

        return self.__call_with_retry(__upsert_kol)

    def update_kol(self, origin_url, update_field):
        def __update_kol():
            return self.readon_kols.update_one(
                {'origin_url': origin_url},
                {'$set': update_field},
            )

        return self.__call_with_retry(__update_kol)

    def find_kols(self,  query):
        def __find_kols():
            return list(self.readon_kols.find(query))

        return self.__call_with_retry(__find_kols)

    def find_kol(self, author_id, source):
        def __find_kol():
            return self.readon_kols.find_one(
                {'author_id': author_id, 'source': source}
            )

        return self.__call_with_retry(__find_kol)

    def insert_sheet(self, sheet_info):
        def __insert_sheet():
            return self.readon_sheets.insert_one(sheet_info)

        return self.__call_with_retry(__insert_sheet)

    def insert_cooperation(self, cooperation):
        def __insert_cooperation():
            return self.cooperations.insert_one(cooperation)

        return self.__call_with_retry(__insert_cooperation)

    def find_cooperations(self,  query):
        def __find_cooperations():
            return list(self.cooperations.find(query))

        return self.__call_with_retry(__find_cooperations)

    def find_cooperation(self,  cooperation_id):
        def __find_cooperation():
            return self.cooperations.find_one({'cooperation_id': cooperation_id})

        return self.__call_with_retry(__find_cooperation)

    def update_cooperation(self,  cooperation_id, update_filed):
        def __update_cooperation():
            return self.cooperations.update_one(
                {'cooperation_id': cooperation_id},
                {'$set': update_filed}
            )

        return self.__call_with_retry(__update_cooperation)

    def get_latest_message(self, cooperation_id, belong_to):
        def __get_latest_message():
            messages = list(self.messages.find(
                {'cooperation_id': cooperation_id, 'belong_to': belong_to}))
            if not messages:
                return ''
            messages.sort(key=lambda x: x['created_at'], reverse=True)
            return messages[0]['content']

        return self.__call_with_retry(__get_latest_message)

    def get_messages(self, cooperation_id):
        def __get_messages():
            return list(self.messages.find({'cooperation_id': cooperation_id}))

        return self.__call_with_retry(__get_messages)

    def insert_message(self, message):
        def __insert_message():
            return self.messages.insert_one(message)

        return self.__call_with_retry(__insert_message)

    def __call_with_retry(self, callback, times=0):
        try:
            return callback()
        except (AutoReconnect, ConnectionFailure) as e:
            if times > MAX_RETRY_TIMES:
                raise
            else:
                self.__set_up_db_client()
                time.sleep(2)
                return self.__call_with_retry(callback, times=times + 1)

    def __set_up_db_client(self):
        mongo_client = MongoClient(self.MONGO_URI, server_api=ServerApi('1'))

        readon_db = mongo_client.readon

        if self.test_only:
            self.logger.info('Running in test mode.')
            test_db = mongo_client.test
            readon_db = test_db

        self.readon_keywords = readon_db.Keywords
        self.readon_videos = readon_db.Videos
        self.readon_authors = readon_db.Authors
        self.youtube_api_keys = readon_db.Youtube_api_keys
        self.readon_sheets = readon_db.Sheets
        self.readon_kols = readon_db.Kols
        self.cooperations = readon_db.Cooperations
        self.messages = readon_db.Messages


def main():
    test_db = DbClient(None)
    sheet_info = {
        'sheet_id': '1s0No8lGQmA4IH9l-1xaE67RV_YZUHPvspVHwofrzQ9g',
        'belong_to': 'kol_main',
        'title': 'kol_wanted_status'
    }
    test_db.insert_sheet(sheet_info)
    # test_db.insert_youtube_api_key('AIzaSyDBj1U8vzMxS-JWbwFfja-dsmiQ0Sjqtr8')


if __name__ == '__main__':
    main()
