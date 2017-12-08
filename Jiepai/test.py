import re

import os

string = 'gallery: JSON.parse("{\"count\":8,\"sub_images\":[{\"url\":\"http:\\/\\/p3.pstatp.com\\/origin' \
      '\\/4af40001830a66d2b866\",' \
      '\"width\":800,\"url_list\":[{\"url\":\"http:\\/\\/p3.pstatp.com\\/origin\\/4af40001830a66d2b866\"},'

images_pattern = re.compile(r'gallery.*?parse\("(.*)', re.S)
result = re.search(images_pattern, string)

print(result.group(1).replace('\"', '@@'))

print(os.getcwd() + '/image')