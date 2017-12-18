import requests
from pyquery import PyQuery as pq
from requests import RequestException
import json
import re
import song
from multiprocessing import Pool
import redis


def get_song_list_by_singer(singer, start=0):
    base_url = 'http://music.baidu.com/search/song?s=1&key={0}&jump=0&start={1}&size=20&third_type=0'
    url = base_url.format(singer, str(start))
    try:
        response = requests.get(url)
        if response.status_code == 200:
            html = str(response.content, 'utf-8')
            return html
        return None
    except RequestException:
        print('页面请求错误！')
        return None


def parse_song_list(html):
    doc = pq(html)
    lis = doc('#result_container > div:nth-child(1) > div.search-song-list.song-list.song-list-hook > ul > li')
    # 默认的没法用
    # #result_container > div:nth-child(1) > div.page-navigator-hook.page-navigator.\7b.pageNavigator\3a \7b.\27 total\27 \3a 352\2c.\27 size\27 \3a 20\2c.\27 start\27 \3a 40\2c.\27 show_total\27 \3a 0\2c.\27 focus_neighbor\27 \3a 0.\7d.\7d > div > div > a:nth-child(12)
    count = doc('#result_container > div:nth-child(1) > div.page-navigator-hook.page-navigator > div > div > a:nth-last-of-type(2)')
    song_ids = []
    for li in lis.items():
        song_item_json = li.attr('data-songitem')
        song_item = json.loads(song_item_json)
        song_ids.append(song_item['songItem']['sid'])
    return song_ids, int(count.html())


def get_song_info(id):
    # 发现 api 的网址：http://music.baidu.com/song/5915242
    # 在 Chrome 开发者模式中需要 Disable Cache，才能查看到该 API
    base_api_url = 'http://tingapi.ting.baidu.com/v1/restserver/ting?method=baidu.ting.song.play&format=jsonp&callback=jQuery17205388351642742888_1513579711445&songid={0}&_=1513579712696'
    api_url = base_api_url.format(id)
    try:
        response = requests.get(api_url)
        # 有些歌曲的歌名中有"（）"
        item_str = re.match(r'jQuery.*?\((.*)\)', response.text)
        item = json.loads(item_str.group(1))
        sid = item['songinfo']['song_id']
        author = item['songinfo']['author']
        title = item['songinfo']['title']
        lrclink = item['songinfo']['lrclink']
        link = item['bitrate']['file_link']
        hash_code = item['bitrate']['hash']
        song_obj = song.Song(sid, title, author, link, lrclink, hash_code)
        return song_obj
    except:
        error_info = '获取歌曲错误：{0}'
        print(error_info.format(id))
        return None

if __name__ == '__main__':
    singer = '周杰轮'
    html = get_song_list_by_singer(singer)
    song_ids, count = parse_song_list(html)
    p = Pool()
    # 下载歌手所有的歌曲
    # for i in range(count - 1):
    #     html = get_song_list_by_singer(singer, (i + 1) * 20)
    #     ids, c = parse_song_list(html)
    #     song_ids = song_ids + ids
    for id in song_ids:
        song_obj = get_song_info(id)
        d = song_obj.download()
        p.apply_async(d)
