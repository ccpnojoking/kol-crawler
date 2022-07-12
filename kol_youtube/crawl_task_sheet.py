import os
import sys
import pandas as pd

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(DIR + '/../utils')

from utils.google_sheet_utils import GoogleSheetClient

DIR = os.path.dirname(os.path.abspath(__file__))


class CrawlTaskSheet:

    def __init__(self):
        super().__init__()
        self.sheet_client = GoogleSheetClient()

    def get_keywords(self, sheet_id):
        tasks = self.sheet_client.read_dataframe_from_googlesheet(sheet_id, 'keywords')
        if tasks is None:
            return []
        keywords = []
        for index, task in tasks.iterrows():
            keyword = {
                'keyword': task['Key Word'],
                'belong_to': task['Belong To'],
                'order_by_method': task['Order By Method']
            }
            keywords.append(keyword)
        self.sheet_client.clear_googlesheet_values(sheet_id, 'keywords')
        init_sheet = pd.DataFrame(
            {'Key Word': [], 'Belong To': [], 'Order By Method': []})
        self.sheet_client.write_to_googlesheet(init_sheet, sheet_id, 'keywords')
        return keywords


def main():
    job = CrawlTaskSheet()
    print(job.get_keywords('1BqTXoLb60MucnUlNo_9gv-aqtA5AgBGnCiI9To-WxBY'))


if __name__ == '__main__':
    main()
