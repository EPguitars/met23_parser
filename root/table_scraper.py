""" csv writer module """
import time

import pandas as pd

ctime = time.gmtime()
TABLE_NAME = f'23мет.ru - {ctime.tm_mday}.{ctime.tm_mon}.{ctime.tm_year}.csv'

def write_to_csv(data: list) -> None:
    """ pandas parsing and csv writer """
    result_table = None

    if len(data) == 0:
        pass
    else:
        for element in data:

            current_table = pd.read_html(element.data.text)[0]
            current_table.insert(0, "Основной раздел", element.main_category)
            current_table.insert(1, "Подраздел", element.name)
            current_table.insert(2, "Размер", element.size)
            if result_table is None:
                result_table = current_table

            else:
                result_table = pd.concat([result_table, current_table], axis=0)

        # replacing some columns
        try:
            columns_name = "Поставщик"
            column = result_table.pop(columns_name)
            result_table = pd.concat([result_table, column], axis=1)
            columns_name = "Поставщик.1"
            column = result_table.pop(columns_name)
            result_table = pd.concat([result_table, column], axis=1)
        except KeyError:
            pass

        try:
            old_table = pd.read_csv(TABLE_NAME, encoding="utf=8")        
            file = pd.concat([result_table, old_table], axis=0)
            file.to_csv(TABLE_NAME, index=False)

        except FileNotFoundError:
            result_table.to_csv(TABLE_NAME, encoding="utf=8", index=True)


