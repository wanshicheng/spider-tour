import requests
import re
import json

url = 'http://tingapi.ting.baidu.com/v1/restserver/ting?method=baidu.ting.song.play&format=jsonp&callback=jQuery17205388351642742888_1513579711445&songid=551132272&_=1513579712696'
response = requests.get(url)
item_str = re.match(r'jQuery.*?\((.*)\)', response.text)
print(item_str.group(1))
