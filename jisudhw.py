import os
from multiprocessing.pool import ThreadPool

import requests
from bs4 import BeautifulSoup
import ffmpy3

search_keyword = '迷雾第一季'
search_url = 'http://www.jisudhw.com/index.php'
search_params = {
    'm': 'vod-search'
}
search_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
    'Referer': 'http://www.jisudhw.com/',
    'Origin': 'http://www.jisudhw.com',
    'Host': 'www.jisudhw.com'
}

search_datas = {
    'wd': search_keyword,
    'submit': 'search'
}

video_dir = ''

req = requests.post(url=search_url, params=search_params, headers=search_headers, data=search_datas)
req.encoding = 'utf-8'
server = 'http://www.jisudhw.com'
search_html = BeautifulSoup(req.text, 'lxml')
search_spans = search_html.find_all('span', class_='xing_vb4')
for span in search_spans:
    url = server + span.a.get('href')
    name = span.a.string
    video_dir = name
    if name not in os.listdir('./'):
        os.mkdir(name)
    # print(name)
    # print(url)
    detail_url = url
    r = requests.get(url=detail_url)
    r.encoding = 'utf-8'
    detail_bf = BeautifulSoup(r.text, 'lxml')
    num = 1
    search_res = {}
    for each_url in detail_bf.find_all('input'):
        if 'mp4' in each_url.get('value'):
            url = each_url.get('value')
            if url not in search_res.keys():
                search_res[url] = num
                print('第%03d集:' % num)
                print(url)
                num += 1


def downVideo(url):
    num = search_res[url]
    name = os.path.join(video_dir, '第%03d集.mp4' % num)
    ffmpy3.FFmpeg(executable='ffmpeg.exe', inputs={url: None}, outputs={name: None}).run()


# 开8个线程池
pool = ThreadPool(8)
results = pool.map(downVideo, search_res.keys())
pool.close()
pool.join()
# print(search_res)
