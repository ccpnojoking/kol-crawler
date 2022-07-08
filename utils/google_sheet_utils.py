import os
import time
import gspread
import gspread_dataframe as gd
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
GOOGLE_SHEET_BASE_URL = "https://docs.google.com/spreadsheets/d/"


class GoogleSheetClient:
    def __init__(self, creadential_path='config/creadential_google_sheet.json') -> None:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            os.path.join(DIR, creadential_path), SCOPES)
        self.gc = gspread.authorize(credentials)

    def open_worksheet(self, url, parm):
        if isinstance(parm, int):
            return self.gc.open_by_url(url).get_worksheet(parm)
        elif isinstance(parm, str):
            return self.gc.open_by_url(url).worksheet(parm)

    def get_titles(self, spread_sheet_id):
        url = GOOGLE_SHEET_BASE_URL + spread_sheet_id
        spread_sheet = self.gc.open_by_url(url)
        work_sheets = spread_sheet.worksheets()
        return [sheet.title for sheet in work_sheets]

    def write_to_googlesheet(self, df_to_write, spread_sheet_id, sub_sheet):
        url = GOOGLE_SHEET_BASE_URL + spread_sheet_id
        wks = self.open_worksheet(url, sub_sheet)
        gd.set_with_dataframe(wks, df_to_write)

    def clear_googlesheet_values(self, spread_sheet_id, sub_sheet):
        url = GOOGLE_SHEET_BASE_URL + spread_sheet_id
        wks = self.open_worksheet(url, sub_sheet)
        wks.clear()

    def read_list_from_googlesheet(self, spread_sheet_id, sub_sheet):
        url = GOOGLE_SHEET_BASE_URL + spread_sheet_id
        wks = self.open_worksheet(url, sub_sheet)
        return wks.get_all_values()

    def read_dataframe_from_googlesheet(self, spread_sheet_id, sub_sheet):
        url = GOOGLE_SHEET_BASE_URL + spread_sheet_id
        wks = self.open_worksheet(url, sub_sheet)
        values = wks.get_all_values()
        title = values.pop(0)
        return pd.DataFrame(values, columns=title)

    def read_list_spread_sheet_values(self, spread_sheet_id):
        url = GOOGLE_SHEET_BASE_URL + spread_sheet_id
        spread_sheet = self.gc.open_by_url(url)
        spread_sheet_values = []
        for wks in spread_sheet.worksheets():
            wsk_values = wks.get_all_values()
            wsk_values.pop(0)
            spread_sheet_values.extend(wsk_values)
        return spread_sheet_values

    def read_dataframe_spread_sheet_values(self, spread_sheet_id):
        url = GOOGLE_SHEET_BASE_URL + spread_sheet_id
        spread_sheet = self.gc.open_by_url(url)
        spread_sheet_values = []
        title = []
        for wks in spread_sheet.worksheets():
            wsk_values = wks.get_all_values()
            title = wsk_values.pop(0)
            spread_sheet_values.extend(wsk_values)
        return pd.DataFrame(spread_sheet_values, columns=title)

    def append_to_googlesheet(self, add_documents_name: list, add_documents: list, spread_sheet_id, sub_sheet):
        df_read = self.read_dataframe_from_googlesheet(spread_sheet_id, sub_sheet)
        index = len(df_read)
        for documents in add_documents:
            df_read.loc[index, add_documents_name] = documents
            index += 1
        df_write = df_read.fillna('')
        self.write_to_googlesheet(df_write, spread_sheet_id, sub_sheet)

    def set_cells_background_color(
            self, spread_sheet_id, sub_sheet, affected_rows: list, affected_cols: list, background_color: dict):
        url = GOOGLE_SHEET_BASE_URL + spread_sheet_id
        wks = self.open_worksheet(url, sub_sheet)
        sheet_id = wks.id
        values = []
        for col in range(affected_cols[0], affected_cols[1]):
            values.append({"userEnteredFormat": {
                "backgroundColor": background_color}})
        batch_update_spreadsheet_request_body = {
            "requests": [
                {
                    "updateCells": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": affected_rows[0],
                            "endRowIndex": affected_rows[1],
                            "startColumnIndex": affected_cols[0],
                            "endColumnIndex": affected_cols[1]
                        },
                        "rows": [
                            {
                                "values": values
                            }
                        ],
                        "fields": "userEnteredFormat.backgroundColor"
                    }
                }
            ]
        }
        spread_sheet = self.gc.open_by_url(url)
        spread_sheet.batch_update(batch_update_spreadsheet_request_body)
        time.sleep(2)


def test_job():
    job = GoogleSheetClient()
    titles = job.get_titles('1BqTXoLb60MucnUlNo_9gv-aqtA5AgBGnCiI9To-WxBY')
    print(titles)


if __name__ == '__main__':
    test_job()
