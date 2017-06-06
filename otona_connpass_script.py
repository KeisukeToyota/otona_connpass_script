from connpass import *
from dateutil import parser
import bs4
from tweepy import *
from datetime import datetime
import time
from urllib import request
import os
from PIL import Image
from io import BytesIO
import signal

signal.signal(signal.SIGPIPE, signal.SIG_DFL)
signal.signal(signal.SIGINT, signal.SIG_DFL)


def connpass_infomation(series_id):
    connpass = Connpass()
    results = []
    events = connpass.search(series_id=[series_id])['events']

    for event in events:
        event_id = event['event_id']
        start_time = parser.parse(event['started_at'])
        end_time = parser.parse(event['ended_at'])
        start_time = str(start_time.year) + '年' + str(start_time.month) + '月' + str(
            start_time.day) + '日' + ' ' + str(start_time.hour) + '時' + str(start_time.minute) + '0分'
        end_time = str(end_time.year) + '年' + str(end_time.month) + '月' + str(end_time.day) + \
            '日' + ' ' + str(end_time.hour) + '時' + str(end_time.minute) + '0分'
        if(datetime.now() < datetime.strptime(start_time, '%Y年%m月%d日　%H時%M分')):
            title = event['title']
            place = event['place']
            url = event['event_url']
            soup = bs4.BeautifulSoup(event['description'], 'html.parser')
            all_tag = [tag.string for tag in soup.find_all()]
            teacher = ''
            if('講師' in all_tag):
                teacher = all_tag[all_tag.index('講師') + 1]
            elif('サポーター' in all_tag):
                teacher = all_tag[all_tag.index('サポーター') + 1]
            if teacher:
                text = 'タイトル：%s\n場所：%s\n講師：%s\n開始時間：%s\n終了時間：%s\nURL：%s' % (
                    title, place, teacher, start_time, end_time, url)
                results.append([text, event_id])

    return results


def otona_img_getter(event_id):
    try:
        url = 'https://otona.connpass.com/event/' + str(event_id)
        response = request.urlopen(url)
        html = response.read().decode("utf-8")
        soup = bs4.BeautifulSoup(html, 'html.parser')
        img_bg = str(soup.find(class_='thumbnail')).split(' ')
        img = ''
        for i in img_bg:
            if('url' in i):
                img = i[28:-3]
        return img
    except:
        return 0


def tweet(text, event_id):
    consumer_key = '****************************'
    consumer_secret = '****************************'
    access_token = '****************************'
    access_token_secret = '****************************'
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    filename = 'output.png'
    img_getter = otona_img_getter(event_id)
    if img_getter:
        img = request.urlopen(img_getter).read()
        image = Image.open(BytesIO(img))
        image.save(filename, "PNG")
        API(auth).update_with_media(filename, status=text)
        os.remove(filename)
    else:
        API(auth).update_status(status=text)


def main():
    connpass_infos = connpass_infomation(2547)

    for text, event_id in connpass_infos:
        tweet(text, event_id)
        time.sleep(10)

if __name__ == '__main__':
    main()
