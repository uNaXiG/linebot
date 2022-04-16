import datetime
import csv
import pandas as pd
import os
import numpy as np
import requests

from bs4 import BeautifulSoup
from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)
from linebot.exceptions import LineBotApiError

app = Flask(__name__)

path = "E:/LineBot/Weather/"
TownNameFile = path + '/location_report_data.csv'
WeatherFile = path + datetime.datetime.now().strftime('%Y_%m_%d') + "_data" + '/{}_data.csv'.format(datetime.datetime.now().strftime('weather_report'))
MovieIdFile = "E:/LineBot/Movie/movie_id.csv"
movie_web = 'http://www.vscinemas.com.tw/vsweb/theater/detail.aspx?id='

uidFile = "E:/LineBot/UID_Data/user_id.txt"
uid_arr = []

# read user_id.txt file 
def PassFileToList():
    with open(uidFile, "r") as file:
        for i in file:
            uid_arr.append(i)

# check in "uid_arr" list have the user's id
def CheckUidInArr(uid):
    for i in range(len(uid_arr)):
        if uid_arr[i] == uid:
            return
    uid_arr.append(uid)


# write user_arr to user_id.txt file
def SaveUidFile():
    with open(uidFile, "w") as file:
        for i in range(len(uid_arr)):
            file.write(uid_arr[i])
            
#!----weather info function----
# final send weather text to line user message
def SendMsg(loc_town, tempMsg):
    with open(WeatherFile, newline='') as csvfile:
        csvData = csv.reader(csvfile, delimiter=',')
        arr = {}
        rtMsg = ''
        for row in csvData:
            if loc_town in row[0]:
                arr = row
                arr[13] = arr[13].replace('。', '\n')
                rtMsg = tempMsg + arr[13] + "\n預報時間為：\n" + arr[1] + " 至\n" + arr[2] + " 間\n"
                tipMsg = ''
                if int(arr[3]) <= 10:
                    tipMsg = '\n小提示 :\n該地區降雨率不高，是個好天氣！'
                elif int(arr[3]) <= 40:
                    tipMsg = '\n小提示 :\n該地區降雨率雖然不高\n不麻煩的話建議帶把傘吧 ～'
                else:
                    tipMsg = '\n小提示 :\n該地區降雨率高，出門請一定要帶把傘喔 ～'
                rtMsg += tipMsg
                return rtMsg
        
    return 'N/A'

# get input location name is Minimumest 
def GetMinName(arr):
    minName = arr[0]
    for n in arr:         
        if len(arr[n]) < len(minName):
            minName = arr[n]
    return minName

# 開啟並查找 location_report.csv 檔案
def BotMsg(s):    
    with open(TownNameFile, newline='') as csvfile:
        csvData = csv.reader(csvfile, delimiter=',')
        arr_Name = {}
        arr = {}
        arr_index = 0
        for row in csvData:
            if s in row[0]: 
                arr_Name[arr_index] = row[0]
                arr[arr_index] = row
                arr_index += 1
        location_name = ''        
        town = ''
        location = ''
        temp_msg = 'test'
        if len(arr) == 0:
            return '抱歉，查無資料QQ。\n不便之處，敬請見諒。' 
        elif len(arr) > 1:
            location_name = GetMinName(arr_Name)
            for n in arr:
            #print(arr[n][0])
                if arr[n][0] == location_name:
                    town = arr[n][1]
                    location = arr[n][3] 
        else:
            location_name = s
            town = arr[0][1]
            location = arr[0][3] 
        temp_msg = town + location + "附近的天氣是...\n" 
        return SendMsg(town, temp_msg)
  

#!----movie info function----

# get movie name and time data
def GetMovieData(movie_id):
    url = requests.get(movie_web + movie_id)
    soup = BeautifulSoup(url.text, "html.parser")
    movie_time = soup.select("article.hidden ", limit=1)
    movie_tip = soup.select("article.hidden span", limit=2)
    movie_date = soup.select("div.dateBanner a", limit = 1)
    date_temp = ""
    for i in movie_date:
        date_temp = str(i.text).replace(" ", "")

    tip_temp = ""
    for i in movie_tip:
        tip_temp += i.text

    msg = ""
    for i in movie_time:       
        msg = (str(i.text).replace(tip_temp, date_temp).replace("\n\n", "\n"))
    return msg

# check movie id is in the data file : /Movie/movie_id.csv
def CheckMovieId(movie_id):
    m_id_list = []
    with open(MovieIdFile, "r") as file :
        r = csv.reader(file, delimiter = ',')
        for row in r:
            if str(movie_id) == row[1]:                
                m_id_list.append(row[0])
                m_id_list.append(row[1])    
                return m_id_list[0] + " : " + GetMovieData(m_id_list[1]) + "若已過所有放映時刻，將會顯示隔天的資料喔～"
        else : return "請輸入正確的影城代號(ID)\n如欲查詢請輸入「代號」查詢"
        
# search movie id 
def SearchMovieId():
    m_id_str = ""
    with open(MovieIdFile, "r") as file :
        r = csv.reader(file, delimiter = ',')
        for row in r:
            m_id_str += row[0] + "==>" + row[1] + "\n"
    return m_id_str
        
        
line_bot_api = LineBotApi('KHNmxSWhk/SqBzgmrH/CQsFAKfn1Lo1ORJrizExW/++iiBs+fqBypk9keWYfxbZMV7Y+guJiOnN/iRGGkpwLhtuMg0GrIr/xFbOw99JlrNE79VjrK5vv5TEOiwrE0TVbg8OzK+aQeTvtxRPyhdEswgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('b74870847ae16a1d49c263b1db24b733')

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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # get user id when reply    
    print(event.source.user_id + " : " + str(event.message.text))
    user_id = event.source.user_id + "\n"
    CheckUidInArr(user_id)
    try:        
        s = str(event.message.text)
        if '你好' in s :
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text = '我是可以幫你查很多東西的機器人'))        
        else:
            
            try:                
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = CheckMovieId(int(s))))
            except :
                if "代號" in s:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = SearchMovieId()))
                    return
                if len(s) < 2 or len(s) > 5:
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text = '輸入有錯，再檢查一下吧～'))
                else:
                    if '台' in s:
                        s = s.replace('台', '臺')           
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text = BotMsg(s)))       
    except LineBotApiError as e:
    # error handle
        raise e
    
'''
line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text = 'text'))
line_bot_api.push_message(to, TextSendMessage(text = "搜尋 " + s + " 的天氣中..."))
'''

@app.route('/')
def homepage():
    return 'Hello, World!'

#line_bot_api = LineBotApi('8QLSwitsABbrHwpop6wedRbI5RW3kam6lThsY4i35O9WwddiP4zRaiB9W5NaOlM4os421PsFQvqRrNlZzFp+ltJQVpXRKs9xPhWmVti5TU0OfV4DeZYfZ0vDEIu0ppt8b/h4vV0VVqcF9MQrO34vxAdB04t89/1O/w1cDnyilFU=')
'''=================Main==================''' 
if __name__ == "__main__":    
    PassFileToList()
    app.run()
    SaveUidFile()
