import json
from json import JSONDecodeError
from multiprocessing.pool import Pool
from urllib.parse import urlencode
from hashlib import md5

import re

import os
import pymongo
import requests
from bs4 import BeautifulSoup
from requests import RequestException
from config import *

# connenct=False 是在多进程的时候消除 MongoDB 的警告
client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]


def get_page_index(offset, keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': 20,
        'cur_tab': 1,
        # 这个里面的才都是图集
        'from': 'gallery',
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求索引页出现错误')
        return None


def parse_page_index(html):
    try:
        data = json.loads(html)
        if data and 'data' in data.keys():
            for item in data.get('data'):
                # 有些'data'没有'article_url'，也是一种反爬手段？
                if item.get('article_url'):
                    yield item.get('article_url')
    except JSONDecodeError:
        pass


def get_page_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求详情页出错：', url)
        return None


def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('Successfully Saved to Mongo', result)
        return True
    return False


def parse_page_detail(html, url):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    print(title)
    images_pattern = re.compile(r'gallery.*?parse\("(.*?)"\),', re.S)
    result = re.search(images_pattern, html)
    if result:
        # 为了反爬，目标网站对json的格式进行了重新定义
        result_str = result.group(1).replace('\\\"', '\"').replace('\\\\/', '/')
        data = json.loads(result_str)
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            for image in images: download_image(image)
            return {
                'title': title,
                'url': url,
                'images': images,

            }


def download_image(url):
    print('Downloading', url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_image(response.content)
            return response.text
        return None
    except RequestException:
        print('请求图片页出错：', url)
        return None


def save_image(content):
    # md5 防止文件名重复
    file_path = '{0}/{1}.{2}'.format(os.getcwd() + '/image', md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()


def main(offset):
    html = get_page_index(offset, KEYWORD)
    urls = parse_page_index(html)
    for url in urls:
        html = get_page_detail(url)
        result = parse_page_detail(html, url)
        if result: save_to_mongo(result)


if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(GROUP_START, GROUP_END + 1)])
    pool.map(main, groups)
    pool.close()
    pool.join()