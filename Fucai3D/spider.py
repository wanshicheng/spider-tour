import os

import re
import requests
import time
from fake_useragent import UserAgent
from requests import RequestException
from pyquery import PyQuery as pq

from setting import *

BASE_DIR = os.path.abspath(os.path.realpath('.'))


def get_page_index(url, options={}):
    ua = UserAgent()
    base_headers = {
        'User-Agent': ua.random,
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    headers = dict(base_headers, **options)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            html = str(response.content, 'utf-8')
            return html
        return None
    except RequestException:
        print('请求索引页出现错误')
        return None


def parse_page_index(html):
    result = ''
    doc = pq(html)
    trs = doc(r'#main > div.page_left.fl.clearself > div.page_box.clearself.mt10 > table > tbody > tr').items()
    i = 0
    for tr in trs:
        i = i + 1
        if i > 2:
            term = pq(tr)('td:nth-child(1)').text()
            num1 = pq(tr)('td:nth-child(2)').text()
            num2 = pq(tr)('td:nth-child(3)').text()
            num3 = pq(tr)('td:nth-child(4)').text()
            s = '{0},{1},{2},{3}\n'.format(term, num1, num2, num3)
            result = result + s
    return result


def get_page_count(html):
    doc = pq(html)
    result = doc(r'#main > div.page_left.fl.clearself > div.page_box.clearself.mt10 > div')
    count = re.match(r'.*?(\d+)页', result.text())
    return count.group(1)


def write_to_csv(result):
    file_time = time.strftime("%Y-%m-%d", time.localtime())
    file = '{0}/{1}.csv'.format(BASE_DIR, file_time)
    with open(file, 'a') as f:
        f.writelines(result)
        f.close()


def main():
    url = 'http://www.cwl.gov.cn/kjxx/fc3d/hmhz/index.shtml'
    base_url = 'http://www.cwl.gov.cn/kjxx/fc3d/hmhz/index_{0}.shtml'
    html = get_page_index(url)
    count = get_page_count(html)
    result = parse_page_index(html)
    write_to_csv(result)
    for i in range(int(count) -1):
        html = get_page_index(base_url.format(str(i+1)))
        result = parse_page_index(html)
        write_to_csv(result)


if __name__ == '__main__':
    main()

