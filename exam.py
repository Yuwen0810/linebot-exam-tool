import numpy as np
import pandas as pd
import os
from sklearn.utils import shuffle

from json_tools import *


# os.chdir(r'D:/NTUCode/linebot_exam_tool/data')
exam_data = pd.read_excel('./excel_output.xlsx')

def get_question_ids(num_of_q, cls=None):
    if isinstance(cls, (tuple, list)) and len(cls) > 0:
        conditions = '|'.join(cls)
        question_db = exam_data[exam_data['easy_tag'].str.contains(conditions)]
    else:
        question_db = exam_data

    question_db = shuffle(question_db)[:num_of_q]

    q_ids = question_db['#'].to_numpy(dtype=np.int)
    questions = question_db['試題'].to_numpy()
    answers = question_db['答案'].to_numpy(dtype=np.int)
    cls = question_db['easy_tag'].to_numpy()

    return q_ids, questions, answers, cls


def add_exam_record(user_id, start_time, end_time, correct_id, error_id, score, num_of_q):
    record = json_read()

    if user_id not in record:
        record[user_id] = {}

    record[user_id][start_time] = {
        'exam_time': end_time - start_time,
        'correct_id': list(map(int, correct_id)),
        'error_id': list(map(int, error_id)),
        'score': score,
        'num_of_q': num_of_q
    }

    json_write(record)


if __name__ == '__main__':
    print(get_question_ids(40, ['元', '日','長_正確']))
    # print(exam_data[~exam_data['試題'].str.contains('\?|？|:|：')])


