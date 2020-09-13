# heroku: https://linebot-exam-tool.herokuapp.com/callback
# Yuwen PC: https://6f443bb66a69.ngrok.io/callback

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *


#======這裡是呼叫的檔案內容=====
from message import *
from new import *
from Function import *
from json_tools import *
from exam import *
from user_setting import *
#======這裡是呼叫的檔案內容=====

#======python的函數庫==========
import tempfile, os
import datetime
import time
import numpy as np
import pandas as pd
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi('qGyKoQLIHRCDZjwbdYysGUF05L5Wn5hXLA4KzGbfVQvQvmdjJI7suqLHCHAt+gq9Xeb0tv/bYJTSNrt8f+w0J3Qdzdb+dUryUojTHa3VuT6ZWIZuu8xoXc3pPP/SNrmbE1gC41/DHJMaZkaoeVebhAdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('c956674e81ca7bbec33bd70ebc49ca7c')


#======global parameters==========
exam_dict = {}
user_setting = {}
Q_CLS = ['日期', '價格', '廠商數', '人數', '%', '多選', '短正確', '短錯誤', '長正確', '長錯誤']
#======global parameters==========

def get_setting_message(user_id):
    reply_txt = ''
    for q_c in Q_CLS:
        reply_txt += f'【{q_c}】：  {"✓" if user_setting[user_id][q_c] else "✗"}\n'

    return reply_txt

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    user_id = event.source.user_id
    timestamp = event.timestamp
    # print('=============', event, '=============', sep='\n')
    # if '最新合作廠商' in msg:
    #     message = imagemap_message()
    #     line_bot_api.reply_message(event.reply_token, message)
    # elif '最新活動訊息' in msg:
    #     message = buttons_message()
    #     line_bot_api.reply_message(event.reply_token, message)
    # elif '註冊會員' in msg:
    #     message = Confirm_Template()
    #     line_bot_api.reply_message(event.reply_token, message)
    # elif '旋轉木馬' in msg:
    #     message = Carousel_Template()
    #     line_bot_api.reply_message(event.reply_token, message)
    # elif '圖片畫廊' in msg:
    #     message = test()
    #     line_bot_api.reply_message(event.reply_token, message)
    # elif '功能列表' in msg:
    #     message = function_list()
    #     line_bot_api.reply_message(event.reply_token, message)
    # else:
    #     print('User id:', event.source.user_id)
    #     print('Message:', event.message.text)
    #     print('Time:', event.timestamp)
    #     print('Type:', event.message.type)
    #     message = TextSendMessage(text=msg)
    #     line_bot_api.reply_message(event.reply_token, message)


    # 新增訊息 測試
    # if user_id not in user_record:
    #     user_record[user_id] = record_template
    # user_record[user_id]['message'].append(msg)
    # user_record[user_id]['timestamp'].append(timestamp)
    # print(user_record)
    # json_write(user_record)

    ##########################################
    # 考試 or 回答
    ##########################################
    try:
        if msg in ['考試', '測驗', '1', '2', '3', '4']:
            # 考試，重新出題
            if msg in ['考試', '測驗']:

                # 防止忘記結束設定
                if user_setting[user_id]['is_setting']:
                    user_setting[user_id]['is_setting'] = False
                    json_write(user_setting, './user_setting.json')

                num_of_q = user_setting[user_id]['num_of_q']
                q_cls = [c for c in Q_CLS if user_setting[user_id][c] == True]

                q_ids, questions, answers, cls = get_question_ids(num_of_q, cls=q_cls)

                exam_dict[user_id] = {
                    'start_time': timestamp,
                    'end_time': None,
                    'q_ids': q_ids,
                    'questions': questions,
                    'answers': answers,
                    'user_answers': np.zeros(num_of_q, np.int),
                    'cls': cls,
                    'is_exam': True,
                    'current': 0
                }

                # 建立 setting 中考試者的資料
                if user_id not in user_setting:
                    user_setting[user_id] = setting_temp
                    json_write(user_setting, './user_setting.json')


            elif user_id in exam_dict and exam_dict[user_id]['is_exam']:
                exam_dict[user_id]['user_answers'][exam_dict[user_id]['current']] = msg
                exam_dict[user_id]['current'] += 1

            # if 該用戶有參與考試
            if user_id in exam_dict and exam_dict[user_id]['is_exam']:
                # 還沒超過最大題數，繼續出題
                if exam_dict[user_id]['current'] < user_setting[user_id]['num_of_q']:
                    q_index = exam_dict[user_id]['current']

                    # 取得題目的訊息
                    q_id = exam_dict[user_id]['q_ids'][q_index]
                    question = exam_dict[user_id]['questions'][q_index].replace('(1)', '\n(1)').replace('(2)',
                                                                                                        '\n(2)').replace(
                        '(3)', '\n(3)').replace('(4)', '\n(4)').replace(' ', '')
                    cls = exam_dict[user_id]['cls'][q_index]

                    # 出題
                    title = "# " + str(q_id) + f"    (第{q_index + 1}題，共{user_setting[user_id]['num_of_q']}題)" + "\n"
                    title_cls = f"分類：{cls}\n\n"
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=title + title_cls + question))

                # 達到最大題數，開始結算
                else:
                    exam_dict[user_id]['end_time'] = timestamp

                    total_q = user_setting[user_id]['num_of_q']
                    correct_q = exam_dict[user_id]['answers'] == exam_dict[user_id]['user_answers']
                    correct_id = exam_dict[user_id]['q_ids'][correct_q]
                    correct_user_answer = exam_dict[user_id]['user_answers'][correct_q]
                    correct_answer = exam_dict[user_id]['answers'][correct_q]
                    correct_cls = exam_dict[user_id]['cls'][correct_q]

                    num_correct_q = np.sum(correct_q)
                    score = 100 * (np.sum(num_correct_q) / total_q)

                    error_q = exam_dict[user_id]['answers'] != exam_dict[user_id]['user_answers']
                    error_id = exam_dict[user_id]['q_ids'][error_q]
                    error_user_answer = exam_dict[user_id]['user_answers'][error_q]
                    error_answer = exam_dict[user_id]['answers'][error_q]
                    error_cls = exam_dict[user_id]['cls'][error_q]

                    reply_title = f'答對題數：{num_correct_q} / {total_q}  ' + \
                                  '分數：{:.1f} 分\n'.format(score)

                    # reply_correct = '\n答對題號：\n#         你的答案    正確答案    類別\n'
                    reply_correct = '\n答對題號：\n#    你的答案  正確答案    類別\n'
                    for id, u_ans, ans, c in zip(correct_id, correct_user_answer, correct_answer, correct_cls):
                        reply_correct += f'{id}       {u_ans}               {ans}         {c}\n'

                    reply_error = '\n答錯題號：\n#    你的答案  正確答案    類別\n'
                    for id, u_ans, ans, c in zip(error_id, error_user_answer, error_answer, error_cls):
                        reply_error += f'{id}       {u_ans}               {ans}         {c}\n'

                    cost_time = exam_dict[user_id]['end_time'] - exam_dict[user_id]['start_time']
                    reply_time = f'\n測驗時間： {cost_time / 1000} 秒'

                    line_bot_api.reply_message(event.reply_token, TextSendMessage(
                        text=reply_title + reply_correct + reply_error + reply_time))
                    exam_dict[user_id]['current'] = False

                    add_para = {
                        'user_id': user_id,
                        'start_time': exam_dict[user_id]['start_time'],
                        'end_time': exam_dict[user_id]['end_time'],
                        'correct_id': correct_id,
                        'error_id': error_id,
                        'score': score,
                        'num_of_q': user_setting[user_id]['num_of_q']
                    }
                    add_exam_record(**add_para)

        ##########################################
        # 設定題組、考試題數
        ##########################################
        elif msg == '設定':
            if user_id not in user_setting:
                user_setting[user_id] = setting_temp
                json_write(user_setting, './user_setting.json')

            user_setting[user_id]['is_setting'] = True
            reply_txt = f"考試題數：{user_setting[user_id]['num_of_q']}\n"
            reply_txt += get_setting_message(user_id)

            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_txt))

        # 設定題組
        elif (msg in Q_CLS or msg[:2] == '題數') and user_setting[user_id]['is_setting']:
            if msg[:2] == '題數':
                user_setting[user_id]['num_of_q'] = int(msg[2:].replace(' ', ''))
            else:
                user_setting[user_id][msg] = not user_setting[user_id][msg]

            reply_txt = f"考試題數：{user_setting[user_id]['num_of_q']}\n"
            reply_txt += get_setting_message(user_id)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_txt))

        elif msg == '重置':
            user_setting[user_id] = setting_temp
            json_write(user_setting, './user_setting.json')
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="重置完成～"))


        ##########################################
        # 考試 or 設定結束
        ##########################################
        elif msg == '結束':
            if user_id in exam_dict and exam_dict[user_id]['is_exam']:
                del exam_dict[user_id]
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="考試結束～"))

            if user_setting[user_id]['is_setting']:
                user_setting[user_id]['is_setting'] = False
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="設定結束～"))
                json_write(user_setting, './user_setting.json')


        ##########################################
        # 瀏覽紀錄
        ##########################################
        elif msg in ['紀錄', '歷史']:
            pass


        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))

    except Exception as e:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=e))

import os
if __name__ == "__main__":
    # os.chdir(r'D:/NTUCode/linebot_exam_tool/data')
    user_setting = json_read('./user_setting.json')
    # print(os.getcwd())
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
