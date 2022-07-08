import os
import sys
import pandas as pd

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(DIR + '/../utils')

from utils.google_sheet_utils import GoogleSheetClient

DIR = os.path.dirname(os.path.abspath(__file__))
TASK_SHEET_ID = '1BqTXoLb60MucnUlNo_9gv-aqtA5AgBGnCiI9To-WxBY'


class CrawlTaskSheet:

    def __init__(self):
        super().__init__()
        self.sheet_client = GoogleSheetClient()

    def get_keywords(self):
        tasks = self.sheet_client.read_dataframe_from_googlesheet(TASK_SHEET_ID, 'keywords')
        if tasks is None:
            return []
        keywords = []
        for index, task in tasks.iterrows():
            keyword = {
                'keyword': task['keyword'],
                'belong_to': task['belong_to'],
                'order_by_method': task['order_by_method']
            }
            keywords.append(keyword)
        self.sheet_client.clear_googlesheet_values(TASK_SHEET_ID, 'keywords')
        init_sheet = pd.DataFrame(
            {'keyword': [], 'belong_to': [], 'order_by_method': []})
        self.sheet_client.write_to_googlesheet(init_sheet, TASK_SHEET_ID, 'keywords')
        return keywords


def main():
    job = CrawlTaskSheet()
    print(job.get_keywords())


if __name__ == '__main__':
    main()
