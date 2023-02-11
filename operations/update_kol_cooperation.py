import os
import sys
import time
import hashlib
import locale
import numpy as np
import pandas as pd
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(DIR + '/../utils')

from db_utils import DbClient
from logger_utils import Logger
from google_sheet_utils import GoogleSheetClient


class UpdateKolCooperation:

    def __init__(self, is_test=False):
        super().__init__()
        self.logger = Logger('update kol cooperation', os.path.join(DIR, 'logs/update_kol_cooperation.log'))
        self.db_client = DbClient(self.logger, test_only=is_test)
        self.sheet_client = GoogleSheetClient()

    @staticmethod
    def get_show_authors_sheet(authors):
        show_authors = {
            'Name': [],
            'Author ID': [],
            'Origin Url': [],
            'Source': [],
            'Belong To': [],
            'Country Code': [],
            'Subscribers': [],
            'Avg Views': [],
            'Median Views': [],
            'Avg Comments': [],
            'Median Comments': [],
            'Keyword': [],
            'Selected': [],
            'Emails': [],
            'Other Contacts': []
        }
        for author in authors:
            show_authors['Name'].append(author['name'])
            show_authors['Author ID'].append(author['author_id'])
            show_authors['Origin Url'].append(author['origin_url'])
            show_authors['Source'].append(author['source'])
            show_authors['Belong To'].append(author['belong_to'])
            show_authors['Country Code'].append(author['country_code'])
            show_authors['Subscribers'].append(author['subscribers'])
            views_list = author['views_list']
            comments_list = author['comments_list']
            show_authors['Avg Views'].append(int(np.mean(views_list)))
            show_authors['Median Views'].append(int(np.median(views_list)))
            show_authors['Avg Comments'].append(int(np.mean(comments_list)))
            show_authors['Median Comments'].append(int(np.median(comments_list)))
            show_authors['Keyword'].append(author.get('keyword', 'None'))
            show_authors['Selected'].append('')
            show_authors['Emails'].append(','.join(author['emails']))
            show_authors['Other Contacts'].append('')
        return pd.DataFrame(show_authors)

    @staticmethod
    def get_show_kol_sent_status_sheet(kols):
        show_kols = {
            'Author ID': [],
            'Source': [],
            'Origin Url': [],
            'Belong To': [],
            'Emails': [],
            'Sent Status': [],
            'Sent Count': [],
            'Last Sent Datetime': [],
            'Replied': []
        }
        for kol in kols:
            show_kols['Author ID'].append(kol['author_id'])
            show_kols['Source'].append(kol['source'])
            show_kols['Origin Url'].append(kol['origin_url'])
            show_kols['Belong To'].append(kol['belong_to'])
            show_kols['Emails'].append(','.join(kol['emails']))
            show_kols['Sent Status'].append(1 if kol.get('is_sent') else 0)
            show_kols['Sent Count'].append(kol.get('sent_count', ''))
            show_kols['Last Sent Datetime'].append(kol.get('last_sent_at', ''))
            show_kols['Replied'].append('')
        return pd.DataFrame(show_kols)

    @staticmethod
    def get_show_kol_wanted_status_sheet(kols):
        show_kols = {
            'Author ID': [],
            'Source': [],
            'Origin Url': [],
            'Belong To': [],
            'Wanted': []
        }
        for kol in kols:
            show_kols['Author ID'].append(kol['author_id'])
            show_kols['Source'].append(kol['source'])
            show_kols['Origin Url'].append(kol['origin_url'])
            show_kols['Belong To'].append(kol['belong_to'])
            show_kols['Wanted'].append('')
        return pd.DataFrame(show_kols)

    def get_messages(self, cooperation_id):
        messages = self.db_client.get_messages(cooperation_id)
        if not messages:
            return ''
        messages.sort(key=lambda x: x['created_at'])
        messages_history = ''
        for message in messages:
            messages_history += f"{message['belong_to']}({str(message['created_at'])}):\n{message['content']}" \
                                f"\n{'-'*20}\n"
        return messages_history

    def insert_message(self, content, belong_to, cooperation_id):
        if not content:
            return False
        created_at = datetime.utcnow()
        hash_str = '-'.join([content, str(created_at)])
        message_id = hashlib.md5(hash_str.encode('utf-8')).hexdigest().upper()
        message = {
            'message_id': message_id,
            'content': content,
            'belong_to': belong_to,
            'cooperation_id': cooperation_id,
            'created_at': created_at
        }
        self.db_client.insert_message(message)
        self.logger.info(message)
        return True

    def get_show_kol_cooperated_status_sheet(self, cooperations):
        show_kols = {
            'Cooperation ID': [],
            'Author ID': [],
            'Source': [],
            'Origin Url': [],
            'Belong To': [],
            'Country Code': [],
            'Subscribers': [],
            'Avg Views': [],
            'Median Views': [],
            'Avg Comments': [],
            'Median Comments': [],
            'Default Price': [],
            'KOL Price': [],
            'Operator Price': [],
            'Operator Message': [],
            'Boss Price': [],
            'Boss Message': [],
            'Operator Confirmed': [],
            'Boss Confirmed': [],
            'Messages': [],
        }
        for cooperation in cooperations:
            cooperation_id = cooperation['cooperation_id']
            author_id = cooperation['author_id']
            source = cooperation['source']
            author = self.db_client.find_author(author_id, source)
            if not author:
                self.logger.error(f'Not found author[Id: {author_id}, Source: {source}]')
                continue
            show_kols['Cooperation ID'].append(cooperation_id)
            show_kols['Author ID'].append(author_id)
            show_kols['Source'].append(source)
            show_kols['Origin Url'].append(author['origin_url'])
            show_kols['Belong To'].append(cooperation['belong_to'])
            show_kols['Country Code'].append(author['country_code'])
            show_kols['Subscribers'].append(author['subscribers'])
            views_list = author['views_list']
            comments_list = author['comments_list']
            avg_views = int(np.mean(views_list))
            show_kols['Avg Views'].append(avg_views)
            median_views = int(np.median(views_list))
            show_kols['Median Views'].append(median_views)
            show_kols['Avg Comments'].append(int(np.mean(comments_list)))
            show_kols['Median Comments'].append(int(np.median(comments_list)))
            show_kols['Default Price'].append(int(min(median_views, avg_views) * 0.0015))
            show_kols['KOL Price'].append(cooperation.get('kol_price', ''))
            show_kols['Operator Price'].append(cooperation.get('operator_price', ''))
            show_kols['Operator Message'].append('')
            show_kols['Boss Price'].append(cooperation.get('boss_price', ''))
            show_kols['Boss Message'].append('')
            is_confirmed_by_operator = ''
            if cooperation.get('is_confirmed_by_operator') is True:
                is_confirmed_by_operator = '1'
            if cooperation.get('is_confirmed_by_operator') is False:
                is_confirmed_by_operator = '0'
            is_confirmed_by_boss = ''
            if cooperation.get('is_confirmed_by_boss') is True:
                is_confirmed_by_boss = '1'
            if cooperation.get('is_confirmed_by_boss') is False:
                is_confirmed_by_boss = '0'
            show_kols['Operator Confirmed'].append(is_confirmed_by_operator)
            show_kols['Boss Confirmed'].append(is_confirmed_by_boss)
            show_kols['Messages'].append(self.get_messages(cooperation['cooperation_id']))
        return pd.DataFrame(show_kols)

    def update_origin_authors_sheet(self, belong_to):
        """
        1. 展示 origin authors
        涉及：authors(db) [is_shown]
        展示数据 authors(sheet) 分主表格 和 各个运营负责的副表格
        :return:
        """
        query = {'is_shown': {'$exists': True}}
        if belong_to != 'kol_main':
            query['belong_to'] = belong_to
        authors = self.db_client.find_authors(query)
        show_authors_sheet = self.get_show_authors_sheet(authors)
        show_authors_sheet.sort_values(
            ['Belong To', 'Subscribers', 'Median Views'], ascending=[True, False, False], inplace=True)
        sheet_info = self.db_client.get_google_sheet_id(belong_to, 'origin_authors')
        sheet_id = sheet_info['sheet_id']
        self.sheet_client.clear_googlesheet_values(sheet_id, 'origin_authors')
        self.sheet_client.write_to_googlesheet(show_authors_sheet, sheet_id, 'origin_authors')

    def update_authors_sheet(self, belong_to):
        """
        1. 展示 authors
        涉及：authors(db) [is_shown]
        展示数据 authors(sheet) 分主表格 和 各个运营负责的副表格
        :return:
        """
        query = {'is_shown': False}
        if belong_to != 'kol_main':
            query['belong_to'] = belong_to
        authors = self.db_client.find_authors(query)
        show_authors_sheet = self.get_show_authors_sheet(authors)
        show_authors_sheet.sort_values(
            ['Belong To', 'Subscribers', 'Median Views'], ascending=[True, False, False], inplace=True)
        sheet_info = self.db_client.get_google_sheet_id(belong_to, 'authors')
        sheet_id = sheet_info['sheet_id']
        self.sheet_client.clear_googlesheet_values(sheet_id, 'authors')
        self.sheet_client.write_to_googlesheet(show_authors_sheet, sheet_id, 'authors')

    def update_kols(self, belong_to):
        """
        2. 筛选 kols
        涉及：authors(db) [is_shown][is_selected], kols(db)
        操作 authors(sheet) 对【选中】标记 选中/未选中，选中 补充联系方式；
        读取表格数据，对标记过的数据 更新数据库数据；
        选中：更新 authors(db)[is_shown: True], 添加 kols(db)
        未选中：更新 authors(db)[is_shown: True]
        :param belong_to:
        :return:
        """
        sheet_info = self.db_client.get_google_sheet_id(belong_to, 'authors')
        sheet_id = sheet_info['sheet_id']
        authors_sheet = self.sheet_client.read_dataframe_from_googlesheet(sheet_id, 'authors')
        for index, author in authors_sheet.iterrows():
            is_selected = author['Selected']
            author_id = author['Author ID']
            source = author['Source']
            other_contacts = author['Other Contacts']
            emails = author['Emails']
            if is_selected == '':
                continue
            author_in_db = self.db_client.find_author(author_id, source)
            if not author_in_db:
                self.logger.error(f'Not found author[Id: {author_id}, Source: {source}]')
                continue
            self.db_client.update_author(author_id, source, {'is_shown': True})
            if is_selected == '0':
                continue
            emails_in_db = author_in_db['emails']
            kol = {
                'author_id': author_id,
                'source': author_in_db['source'],
                'origin_url': author_in_db['origin_url'],
                'created_at': datetime.utcnow(),
                'emails': emails_in_db,
                'other_contacts': other_contacts,
                'belong_to': belong_to
            }
            if emails != ','.join(emails_in_db):
                kol['emails'] = emails.split(',')
            self.db_client.upsert_kol(author_in_db['origin_url'], kol)

    def update_kol_sent_status_sheet(self, belong_to):
        """
        3. kols 发送邮件状态
        涉及：kols(db)[is_sent][sent_count][last_sent_at][is_replied]
        读取 kols 邮件状态，运营标记 已回复邮件，或者其他渠道完成回复的；
        已回复：更新 kols(db)[is_replied: True]
        :return:
        """
        query = {'is_replied': {'$nin': [True, False]}}
        if belong_to != 'kol_main':
            query['belong_to'] = belong_to
        kol_sent_status = self.db_client.find_kols(query)
        show_kol_sent_status_sheet = self.get_show_kol_sent_status_sheet(kol_sent_status)
        show_kol_sent_status_sheet.sort_values(
            ['Belong To', 'Sent Status', 'Sent Count', 'Last Sent Datetime'],
            ascending=[True, False, True, False],
            inplace=True
        )
        sheet_info = self.db_client.get_google_sheet_id(belong_to, 'kol_sent_status')
        sheet_id = sheet_info['sheet_id']
        self.sheet_client.clear_googlesheet_values(sheet_id, 'kol_sent_status')
        self.sheet_client.write_to_googlesheet(show_kol_sent_status_sheet, sheet_id, 'kol_sent_status')

    def update_kol_sent_status(self, belong_to):
        sheet_info = self.db_client.get_google_sheet_id(belong_to, 'kol_sent_status')
        sheet_id = sheet_info['sheet_id']
        kol_sent_status_sheet = self.sheet_client.read_dataframe_from_googlesheet(sheet_id, 'kol_sent_status')
        for index, kol in kol_sent_status_sheet.iterrows():
            is_replied = kol['Replied']
            kol_emails = kol['Emails']
            if is_replied == '' and not kol_emails:
                continue
            author_id = kol['Author ID']
            source = kol['Source']
            kol_in_db = self.db_client.find_kol(author_id, source)
            if not kol_in_db:
                self.logger.error(f'Not found kol [Id: {author_id}, Source: {source}]')
                continue
            emails = kol_in_db['emails']
            update_filed = {}
            if kol_emails != ','.join(emails):
                kol_emails = kol_emails.split(',')
                update_filed['emails'] = kol_emails
            if is_replied == '1':
                update_filed['is_replied'] = True
            if is_replied == '0':
                update_filed['is_replied'] = False
            if not update_filed:
                continue
            self.db_client.update_kol(kol_in_db['origin_url'], update_filed)

    def update_kol_wanted_status_sheet(self, belong_to):
        """
        4. kols 合作意愿
        涉及: kols(db)[is_wanted]
        读取 kols 已回复状态，运营标记 合作意愿
        同意合作：更新 kols[is_wanted: True]
        不同意合作: 更新 kols[is_wanted: False]
        未表明态度: 不做处理
        :return:
        """
        query = {'is_replied': True, 'is_wanted': {'$exists': False}}
        if belong_to != 'kol_main':
            query['belong_to'] = belong_to
        kol_wanted_status = self.db_client.find_kols(query)
        show_kol_wanted_status_sheet = self.get_show_kol_wanted_status_sheet(kol_wanted_status)
        sheet_info = self.db_client.get_google_sheet_id(belong_to, 'kol_wanted_status')
        sheet_id = sheet_info['sheet_id']
        self.sheet_client.clear_googlesheet_values(sheet_id, 'kol_wanted_status')
        self.sheet_client.write_to_googlesheet(show_kol_wanted_status_sheet, sheet_id, 'kol_wanted_status')

    def update_kol_wanted_status(self, belong_to):
        sheet_info = self.db_client.get_google_sheet_id(belong_to, 'kol_wanted_status')
        sheet_id = sheet_info['sheet_id']
        kol_wanted_status_sheet = self.sheet_client.read_dataframe_from_googlesheet(sheet_id, 'kol_wanted_status')
        for index, kol in kol_wanted_status_sheet.iterrows():
            is_wanted = kol['Wanted']
            if is_wanted == '':
                continue
            is_wanted = True if is_wanted else False
            author_id = kol['Author ID']
            source = kol['Source']
            kol_in_db = self.db_client.find_kol(author_id, source)
            if not kol_in_db:
                self.logger.error(f'Not found kol [Id: {author_id}, Source: {source}]')
                continue
            self.db_client.update_kol(kol_in_db['origin_url'], {'is_wanted': is_wanted})
            if not is_wanted:
                continue
            created_at = datetime.utcnow()
            belong_to = kol_in_db['belong_to']
            hash_str = '-'.join([author_id, source, belong_to, str(created_at)])
            cooperation_id = hashlib.md5(hash_str.encode('utf-8')).hexdigest().upper()
            cooperation = {
                'cooperation_id': cooperation_id,
                'author_id': author_id,
                'source': source,
                'belong_to': belong_to,
                'created_at': created_at
            }
            self.db_client.insert_cooperation(cooperation)

    def update_kol_cooperated_status_sheet(self, belong_to):
        """
        5. cooperations 洽谈价格
        涉及: cooperations(db)[default_price][kol_price][operator_price][boss_price][operator_message][boss_message]
        展示 kols 填kol报价，填运营报价，boss报价，运营留言，boss留言
        :return:
        """
        query = {'is_cooperated': {'$exists': False}}
        if belong_to not in ['boss_mike', 'kol_main']:
            query['belong_to'] = belong_to
        cooperations = self.db_client.find_cooperations(query)
        show_kol_cooperated_status_sheet = self.get_show_kol_cooperated_status_sheet(cooperations)
        sheet_info = self.db_client.get_google_sheet_id(belong_to, 'kol_cooperated_status')
        sheet_id = sheet_info['sheet_id']
        self.sheet_client.clear_googlesheet_values(sheet_id, 'kol_cooperated_status')
        self.sheet_client.write_to_googlesheet(show_kol_cooperated_status_sheet, sheet_id, 'kol_cooperated_status')

    def update_operator_kol_cooperated_status(self, belong_to):
        sheet_info = self.db_client.get_google_sheet_id(belong_to, 'kol_cooperated_status')
        sheet_id = sheet_info['sheet_id']
        cooperation_status_sheet = self.sheet_client.read_dataframe_from_googlesheet(
            sheet_id, 'kol_cooperated_status')
        if cooperation_status_sheet.empty:
            self.logger.info('the sheet is empty.')
            return
        for index, cooperation in cooperation_status_sheet.iterrows():
            kol_price = self.extract_price(cooperation['KOL Price'])
            operator_price = self.extract_price(cooperation['Operator Price'])
            cooperation_id = cooperation['Cooperation ID']
            cooperation_in_db = self.db_client.find_cooperation(cooperation_id)
            if not cooperation_in_db:
                self.logger.error(f'Not found cooperation [Id: {cooperation_id}]')
                continue
            operator_message = cooperation['Operator Message']
            self.insert_message(operator_message, cooperation['Belong To'], cooperation['Cooperation ID'])
            cooperation_status = {}
            if kol_price:
                cooperation_status['kol_price'] = kol_price
            if operator_price:
                cooperation_status['operator_price'] = operator_price
            is_confirmed_by_operator = self.get_confirmed_status(cooperation['Operator Confirmed'])
            if is_confirmed_by_operator is not None:
                cooperation_status['is_confirmed_by_operator'] = is_confirmed_by_operator
                if cooperation_in_db.get('is_confirmed_by_boss') == is_confirmed_by_operator:
                    cooperation_status['is_cooperated'] = is_confirmed_by_operator
            if not cooperation_status:
                continue
            cooperation_status['updated_at'] = datetime.utcnow()
            self.db_client.update_cooperation(cooperation_id, cooperation_status)
            self.logger.info(cooperation_status)

    def update_boss_kol_cooperated_status(self):
        sheet_info = self.db_client.get_google_sheet_id('boss_mike', 'kol_cooperated_status')
        sheet_id = sheet_info['sheet_id']
        cooperation_status_sheet = self.sheet_client.read_dataframe_from_googlesheet(
            sheet_id, 'kol_cooperated_status')
        for index, cooperation in cooperation_status_sheet.iterrows():
            boss_price = self.extract_price(cooperation['Boss Price'])
            cooperation_id = cooperation['Cooperation ID']
            cooperation_in_db = self.db_client.find_cooperation(cooperation_id)
            if not cooperation_in_db:
                self.logger.error(f'Not found cooperation [Id: {cooperation_id}]')
                continue
            boss_message = cooperation['Boss Message']
            self.insert_message(boss_message, 'boss_mike', cooperation['Cooperation ID'])
            cooperation_status = {}
            if boss_price:
                cooperation_status['boss_price'] = boss_price
            is_confirmed_by_boss = self.get_confirmed_status(cooperation['Boss Confirmed'])
            if is_confirmed_by_boss is not None:
                cooperation_status['is_confirmed_by_boss'] = is_confirmed_by_boss
            if not cooperation_status:
                continue
            cooperation_status['updated_at'] = datetime.utcnow()
            self.db_client.update_cooperation(cooperation_id, cooperation_status)
            self.logger.info(cooperation_status)

    @staticmethod
    def get_confirmed_status(status):
        if status == '0':
            return False
        if status == '1':
            return True
        return None

    @staticmethod
    def extract_price(price):
        if not price:
            return None
        return locale.atoi(price)


def main():
    update_status_job = UpdateKolCooperation()

    operators = ['elon', 'kevin', 'blue', 'jinglong', 'yunsoon']
    show_sheets = ['elon', 'kevin', 'blue', 'jinglong', 'yunsoon', 'kol_main']

    # 展示所有作者
    for belong_to in show_sheets:
        update_status_job.update_origin_authors_sheet(belong_to)
        time.sleep(60)

    # Selected 标记 0，1 或者 不标记；authors 选中 -> kols
    for operator in operators:
        update_status_job.update_kols(operator)
        time.sleep(60)
    for belong_to in show_sheets:
        update_status_job.update_authors_sheet(belong_to)
        time.sleep(60)

    # Emails 填充 邮箱 多个邮箱逗号相连；Replied 回复标记 True
    for operator in operators:
        update_status_job.update_kol_sent_status(operator)
        time.sleep(60)
    for belong_to in show_sheets:
        update_status_job.update_kol_sent_status_sheet(belong_to)
        time.sleep(60)

    # Wanted 标记 0，1 或者不标记
    for operator in operators:
        update_status_job.update_kol_wanted_status(operator)
        time.sleep(60)
    for belong_to in show_sheets:
        update_status_job.update_kol_wanted_status_sheet(belong_to)
        time.sleep(60)

    # Operator 标记 KOL Price，Operator Price，Operator Message，Operator Confirmed
    # Boss 标记 Boss Price，Boss Message，Boss Confirmed
    update_status_job.update_boss_kol_cooperated_status()
    for belong_to in operators:
        update_status_job.update_operator_kol_cooperated_status(belong_to)
        time.sleep(60)
    for belong_to in ['kol_main', 'elon', 'kevin', 'blue', 'boss_mike']:
        update_status_job.update_kol_cooperated_status_sheet(belong_to)
        time.sleep(60)


if __name__ == '__main__':
    main()
