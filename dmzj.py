import os
import re
import time
from contextlib import closing

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

if __name__ == '__main__':
    # 创建保存的目录
    save_dir = 'data/妖神记'
    if save_dir not in os.listdir('./'):
        os.mkdir(save_dir)

    target = 'https://www.dmzj.com/info/yaoshenji.html'

    # 获取动漫章节链接和章节名
    req = requests.get(target)
    bs = BeautifulSoup(req.text, 'lxml')
    list_con_li = bs.find('ul', class_="list_con_li")
    cartoon_list = list_con_li.find_all('a')
    chapter_names = []
    chapter_urls = []
    for cartoon in cartoon_list:
        href = cartoon.get('href')
        name = cartoon.text
        chapter_names.insert(0, name)
        chapter_urls.insert(0, href)

    # 下载漫画
    for i, url in enumerate(tqdm(chapter_urls)):
        download_header = {
            'Referer': url
        }
        name = chapter_names[i]
        # 去掉.
        while '.' in name:
            name = name.replace('.', '')
        chapter_save_dir = os.path.join(save_dir, name)
        if name not in os.listdir(save_dir):
            os.mkdir(chapter_save_dir)
            r = requests.get(url=url)
            html = BeautifulSoup(r.text, 'lxml')
            script_info = html.script
            # 正则表达式匹配
            pics = re.findall('\d{13,14}', str(script_info))
            for j, pic in enumerate(pics):
                if len(pic) == 13:
                    pics[j] = pic + '0'
            pics = sorted(pics, key=lambda x: int(x))
            chapterpic_hou = re.findall('\|(\d{5})\|', str(script_info))[0]
            chapterpic_qian = re.findall('\|(\d{4})\|', str(script_info))[0]
            for idx, pic in enumerate(pics):
                if pic[-1] == '0':
                    url = 'https://images.dmzj.com/img/chapterpic/' + chapterpic_qian + '/' + chapterpic_hou + '/' + pic[
                                                                                                                     :-1] + '.jpg'
                else:
                    url = 'https://images.dmzj.com/img/chapterpic/' + chapterpic_qian + '/' + chapterpic_hou + '/' + pic + '.jpg'
                pic_name = '%03d.jpg' % (idx + 1)
                pic_save_path = os.path.join(chapter_save_dir, pic_name)
                with closing(requests.get(url, headers=download_header, stream=True)) as response:
                    chunk_size = 1024
                    content_size = int(response.headers['content-length'])
                    if response.status_code == 200:
                        with open(pic_save_path, "wb") as file:
                            for data in response.iter_content(chunk_size=chunk_size):
                                file.write(data)
                    else:
                        print('链接异常')
            time.sleep(10)
