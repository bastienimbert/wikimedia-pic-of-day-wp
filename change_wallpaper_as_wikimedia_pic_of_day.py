# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 16:48:54 2024

@author: Bastien Imbert
"""
import os
import time
import tqdm
import ctypes
import platform
import urllib.request
import feedparser as fp
from html.parser import HTMLParser

READING_TIME = 10 # In seconds
FILE_NAME_MAX_CHAR = 20
SUPPORTED_OS = ['Windows'] # Possible outputs are 'Linux', 'Darwin', 'Java', 'Windows'
rss_url = 'https://commons.wikimedia.org/w/api.php?action=featuredfeed&feed=potd&feedformat=rss&language=en'
last_block = 0
dst_folder = os.path.expanduser('~')+r"\Pictures\Backgrounds\\"

class MyHTMLParser(HTMLParser):
    picture_desc=''
    picture_src=''
    def handle_starttag(self, tag, attrs):
        if tag=="img":
            for attr in attrs:
                if attr[0] == 'src':
                    self.picture_src = attr[1]
    
    def handle_data(self, data):
        if len(data)>=2 and data!="Picture of the day":
            self.picture_desc += data

def tqdm_caller(current_block, block_size, total_size):
    global last_block
    global progress_bar
    if (last_block==0):
        progress_bar = tqdm.tqdm(total=(total_size//1024), unit="ko", postfix='ko')
    else:
        progress_bar.update(((current_block-last_block)*block_size//1024))
    last_block=current_block
supported_os_str = ''
for os_value in SUPPORTED_OS:
    supported_os_str+=['',', '][len(supported_os_str)>0]+f"{os_value}"
print(f"Unsupported OS Platform\nList of supported Platform OS: {supported_os_str}")
if not (platform.system() in SUPPORTED_OS):
    error = OSError()
    supported_os_str = ''
    for os_value in SUPPORTED_OS:
        supported_os_str+=['',', '][len(supported_os_str)]+f"{os_value}"
    error.add_note(f"Unsupported OS Platform\nList of supported Platform OS: {supported_os_str}")
    raise error

### Getting rss data
rss_feed = fp.parse(rss_url)
parser = MyHTMLParser()

### Keeping only rss data of interest
parser.feed(rss_feed.entries[-1].summary)
parser.close()
print('Found the picture of the day :')
print(parser.picture_desc)
print()

### The rss gives a link to the 300px thumbnail of the picture such as:
### https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Rain_Clouds_Tsarap_Phuktal_Zanskar_Jun24_R16_07793.jpg/300px-Rain_Clouds_Tsarap_Phuktal_Zanskar_Jun24_R16_07793.jpg
### We want to get the full picture for our wallpaper such as:
### https://upload.wikimedia.org/wikipedia/commons/7/7b/Rain_Clouds_Tsarap_Phuktal_Zanskar_Jun24_R16_07793.jpg
better_quality_link=parser.picture_src
idx_thumb = better_quality_link.rfind('thumb/')
better_quality_link = better_quality_link[:idx_thumb]+better_quality_link[idx_thumb+len('thumb/'):]
idx_300px = better_quality_link.rfind('/300px')
better_quality_link = better_quality_link[:idx_300px]
print('Found the url for the best version')
print(better_quality_link)
print()

### Retrieving the resource located at the URL 
### and storing it in the file name a.png 
file_name = parser.picture_desc[:min(len(parser.picture_desc), FILE_NAME_MAX_CHAR)]+".png"

print('Downloading picture')
urllib.request.urlretrieve(better_quality_link, dst_folder+file_name, reporthook=tqdm_caller)
progress_bar.close()
print()
print('File downloaded')

ctypes.windll.user32.SystemParametersInfoW(20, 0, dst_folder+file_name , 0)
print('Background changed!')

print()
print('Now viewing '+parser.picture_desc)
closing_timer = tqdm.tqdm(total=READING_TIME, desc="Closing window in")
for i in range(READING_TIME):
    time.sleep(1)
    closing_timer.update()
closing_timer.close()