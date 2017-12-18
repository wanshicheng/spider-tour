import os
import requests


class Song:
    def __init__(self, sid, title, author, link, lrclink, hash_code):
        self.sid = sid
        self.title = title
        self.author = author
        self.link = link
        self.lrclink = lrclink
        self.hash_code = hash_code
        print(self.title + ' 就绪...')

    def download(self):
        response = requests.get(self.link)
        # 持久化
        file_path = '{0}/{1}/{2}.mp3'.format(os.getcwd(), 'song', self.title)
        with open(file_path, 'wb') as f:
            f.write(response.content)
