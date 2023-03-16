import os
import sys
from datetime import datetime, timedelta

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(DIR + '/../utils/')

from logger_utils import Logger
from db_utils import DbClient
from email_utils import EmailClient
from google_sheet_utils import GoogleSheetClient

SUPPORT_LANGUAGE = {}


class SendJob:

    def __init__(self, is_test=False):
        super().__init__()
        self.logger = Logger('send job', os.path.join(DIR, 'logs/send_job.log'))
        self.db_client = DbClient(self.logger, test_only=is_test)
        self.email_client = EmailClient()
        self.sheet_client = GoogleSheetClient()

    @staticmethod
    def loop_call(simple: list):
        index = 0
        while index <= len(simple):
            if index == len(simple):
                index = 0
            index += 1
            yield simple[index - 1]

    def get_message(self, sender_email, receiver_emails, belong_to, country_code, index):
        sheet_id = self.db_client.get_google_sheet_id(belong_to, 'email')
        messages = self.sheet_client.read_dataframe_from_googlesheet(sheet_id, str(index))
        subject = messages[SUPPORT_LANGUAGE.get(country_code, 'en')][0]
        content = messages[SUPPORT_LANGUAGE.get(country_code, 'en')][1]
        message = self.email_client.get_html_message(sender_email, receiver_emails, subject, content)
        return message

    def get_kols(self, belong_to):
        query = {'is_replied': {'$ne': True}, 'is_sent': {'$ne': False}, 'belong_to': belong_to}
        kols = self.db_client.find_kols(query)
        need_kols = []
        for kol in kols:
            if kol.get('sent_count', 0) >= 4:
                self.db_client.update_kol(kol['origin_url'], {'is_sent': False})
                continue
            last_sent_at = kol.get('last_sent_at', datetime.utcnow() - timedelta(days=3))
            if (datetime.utcnow() - last_sent_at).days < 2:
                continue
            need_kols.append(kol)
        return need_kols

    def run(self, belong_to):
        emails = self.db_client.find_emails({'belong_to': belong_to})
        email_loops = self.loop_call(emails)
        kols = self.get_kols(belong_to)
        if not kols:
            return
        for kol in kols:
            kol_emails = kol['emails']
            if not kol_emails:
                continue
            email = next(email_loops)
            sent_count = kol.get('sent_count', 0)
            message = self.get_message(email, kol_emails, belong_to, kol.get('country_code', 'unknown'), sent_count)
            is_sent = False
            try:
                response = self.email_client.send(email['email'], email['password'], kol_emails, message)
                is_sent = True
            except Exception as e:
                response = str(e)
            self.db_client.insert_event(
                {'sender': email, 'kol': kol, 'response': response, 'created_at': datetime.utcnow()}
            )
            if not is_sent:
                continue
            self.db_client.update_kol(
                kol['origin_url'],
                {'is_sent': False, 'sent_count': sent_count + 1, 'last_sent_at': datetime.utcnow()}
            )


def main():
    job = SendJob(True)
    job.run('ccp')


if __name__ == '__main__':
    main()
