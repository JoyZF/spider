import codecs
import json
from _md5 import md5
from multiprocessing import Pool
from urllib.parse import urlencode

import re

import os
import requests
from requests import RequestException
from bs4 import BeautifulSoup

def get_page_index(offset,keyword):
    data = {
        'offset':offset,
        'format':'json',
        'keyword':keyword,
        'autoload':'true',
        'count':20,
        'cur_tab':3,
        'from':'gallery'
    }
    url = 'https://www.toutiao.com/search_content/?'+urlencode(data)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求出错")
        return None

def parse_page_index(html):
   data = json.loads(html)
   if data and 'data' in data.keys():
       for item  in data.get('data'):
           yield item.get('article_url')

def get_page_detail(html):
    try:
        response = requests.get(html)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求出错")
        return None

def parse_page_datail(html):
    try:
        soup = BeautifulSoup(html)
        title = soup.select('title')
        # print(title)
        image_pattern = re.compile(r'gallery: JSON.parse\("(.*?)"\),', re.S)
        result = re.search(image_pattern,html)
        print(result)
        if result:
            data_str = codecs.getdecoder('unicode_escape')(result.group(1))[0]
            json_data = json.loads(data_str)
            if json_data and 'sub_images' in json_data.keys():
                sub_images = json_data.get('sub_images')
                images = [item.get('url') for item in sub_images]
                for image in images:
                    download_image(image)
                return {
                    'title': title,
                    'images': images,
                }
        else:
            print('没有搜索到符合条件的gallery数据', end='\n\n')
    except Exception:
        return None

def download_image(url):
    print('正在下载图片', url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_image(response.content)
    except RequestException:
        print('请求图片错误', url)
        pass

def save_image(content):
    dir_name = 'pic'
    file_path = '{0}/{1}.{2}'.format(dir_name, md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()

def main(offset):
    html = get_page_index(20, '军事')
    for url in parse_page_index(html):
        detail_html = get_page_detail(url)
        if detail_html:
            result = parse_page_datail(detail_html)


if __name__ == "__main__":
    groups = [x * 20 for x in range(0, 100)]
    pool = Pool()
    pool.map(main, groups)



