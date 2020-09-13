import json
import os
import numpy as np


setting_temp = {
    'num_of_q': 3,
    '日期': False,
    '價格': False,
    '廠商數': False,
    '人數': False,
    '%': False,
    '多選': False,
    '短正確': False,
    '短錯誤': False,
    '長錯誤': False,
    '長正確': False,
}


def json_read(file_path:str='./user_record.json') -> dict:
    print("reading .................")
    # print(os.getcwd())
    try:
        with open(file_path, 'r') as f:
            json_content = json.loads(f.read())
        return json_content

    except Exception as e:
        print('Error:', e)
        return None

def json_write(data:dict, file_path:str='./user_record.json'):
    print("writting .................")
    try:
        with open(file_path, 'w') as f:
            print(json.dumps(data, indent=4), file=f)
        return True

    except Exception as e:
        print('Error:',e)
        with open(file_path, 'w') as f:
            print(json.dumps({}, indent=4), file=f)
        return False

if __name__ == '__main__':
    content = json_read()



