import json
import os
from hashlib import md5
from multiprocessing import Pool
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup
import re
from redis import Redis

# 使用pymongo 连接mongodb数据库
import pymongo

# mongodb的链接地址
MONGO_URL = 'localhost'
# mongodb - 创建一个数据库名称
MONGO_DB = 'toutiao'
# mongodb - 创建一个表名
MONGO_TABLE = 'toutiao'


# 声名 一个mongodb 数据库
client = pymongo.MongoClient(MONGO_URL,connect = False)
db = client[MONGO_DB]


def url_request(offset, keyword):
    data = {
        'keys': offset,
        'keys2': keyword
    }
    url = 'http://www.xxx.com?' + urlencode(data)
    # try - except  if判断  确保程序能够不中断的正常进行
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except Exception as e:
        print('there is something wrong')
        return None


# 构造生成器  def - for-in - yield
def parse(jso_n):
    # 返回的响应是 json格式  loads 反序列化 str->dict  |  dumps 序列化 dict->str
    data = json.loads(jso_n)
    # 加判断 保证json数据中 含有某个属性  data.keys() -- 对应所有的键名  使用get方法 - 没有则返回None
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('article_url')


def url_detail_request(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        print('there is something wrong')
        return None


def parse_detail(html, url):
    # 创建一个BeautifulSoup对象  并根据属性找出title值
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    # 使用正则 -- 针对xpath等选择器  无法处理的 - <script>内的内容<\script>  没有tag可以选择
    images_pattern = re.compile(r'var gallery= (.*?);', re.S)  # 匹配到第一个json数据{...}; re.S表示匹配任意
    result = re.search(images_pattern, html)
    if result:
        data = json.loads(result.group(1))
        # 判断存在
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            # 构建需要返回的信息
            return {
                'title': title,
                'url': url,
                'images': images
            }


def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('存储到mongodb成功',result)
        return True
    return False
def save_redis(item):
    connect = Redis(
        host='127.0.0.1',
        port=6379
    )
    connect.lpush(item)


def save_images(image_url):
    data = url_detail_request(image_url)
    file_name = '{0}/{1}.{2}'.format(os.getcwd(), md5(data).hexdigest(), 'jpg')
    if not os.path.exists(file_name):
        with open(file_name, 'wb') as w:
            w.write(data)


# 主要逻辑
def main():
    # 形参 与 实参 合理的结合使用   -- 目的  在主要逻辑中尽可能少的参数、赋值等  只负责主要的逻辑  具体操作可以放到不同功能的函数体内
    html = url_request(offset, keyword)
    # 函数生成器
    for url2 in parse(html):
        # 详情页
        html = url_detail_request(url2)
        if html:
            result = parse_detail(html, url2)
            if result:
                # 保存到数据库
                save_redis(result)


if __name__ == '__main__':
    # 可变参数 -- 函数体外  固定参数 -- 函数体内
    # 实参  放在函数体外，可控可调节  函数体内部 用形参
    offset = 0
    keyword = '街拍'

    # 循环遍历 使用map方法 调用进程池  总结为：每个任务是独立的 可以分别完成的  如果是根据上一页找下一页的翻页处理 则不适用
    # 不过可以通过url 的共同点 和 差异处  互相转换
    groups = [i * 20 for i in range(1, 20)]
    pool = Pool()
    pool.map(main, groups)

