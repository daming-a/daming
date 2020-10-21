# -*- coding: utf-8 -*-
'''
requests模块的应用:

    相对完整的模板 -- 可以作为复习的参考

    发现新的技巧， 随时添加

    还需要验证的有：
        生产者消费者模型  队列的概念  进程、线程、协程

    一些问题：
        高并发？分布式？new|init设计模式-单例？工厂？ 闭包-生成器？ python性能？内存管理？

    以下为：
        数据库的创建、 爬虫类 - 发起请求-获取响应并解析网页-深度爬取-保存数据库或本地

'''
import requests
from fake_useragent import UserAgent
import pymysql
from redis import Redis
import random
import time
from lxml import etree
import os


# MySQL数据库
class Mysql:
    def __init__(self, title, caption):
        self.title = title
        self.caption = caption
        self.connect = pymysql.connect(
            db='test_db',
            host='127.0.0.1',
            port=3306,
            user='root',
            password='z123',
            charset='utf8'
        )
        self.cursor = self.connect.cursor()

    def save_mysql(self):
        sql = f'insert into test_table values ("{self.title}","{self.caption}")'

        try:
            self.cursor.execute(sql)
            self.connect.connect()
        except Exception as e:
            self.connect.rollback()
            print('数据插入失败', e)


# redis数据库
class Red_is:
    def __init__(self):
        self.connect = Redis(
            host='127.0.0.1',
            port=6379
        )

    # lpush -- list类型  -- llen lrange append get del set sadd rename
    def save_redis(self, item):
        self.connect.lpush('test_list', item)


# 爬虫类
class Crawl_Spider:

    # 初始化 参数self
    def __init__(self):
        self.url = 'http://www.baidu.com'
        self.headers = {
            'User-Agent': UserAgent().random
        }
        self.proxies = [
            {}, {}, {}, {}
        ]
        # 还可以有 ： get--params = {} , post--data = {}

    # url请求
    def url_request(self, url):
        # 随机休眠 - 防止爬取速度过快，IP被封  -- 最好构建proxies， IP代理池
        time.sleep(random.randint(1, 2))
        # 获取session对象 -- 可携带cookies
        session = requests.Session()
        response = session.request('get', url=url, headers=self.headers, proxies=random.choice(self.proxies))

        # 只返回响应体 -- text文本 | content二进制  可在其他函数中转换，使数据存储格式更灵活
        return response

    # 生成器函数  -- 模仿scrapy 使用生成器函数， 更加节约内存
    def parse(self, response):
        tree = etree.HTML(response.content)
        for li in tree.xpath('//...'):
            item = {}
            item['title'] = li.xpath('./')
            item['caption'] = li.xpath('./')
            yield item

    # 适用于 生产者 | 消息队列 | 消费者
    # 所有的存储I/O, 以及网络请求等 -- 都可以使用进程(占用大)、 线程(GIL锁)、 协程(生成器) -- 提高效率
    # 连接数据库
    def connect_redis(self, item):
        connect = Red_is()
        connect.save_redis(item)

    def connect_mysql(self, item):
        # 具体根据mysql的存储格式, 定制item
        for value in item:
            connect = Mysql(value['title'], value['caption'])
            connect.save_mysql()

    # 二进制文件的下载  -- url -> 本地文件
    def down_load(self, url):
        # 获取文件数据
        data = self.url_request(url).content

        # 如果文件不存在， 则创建
        file_name = r'D:\Data'
        if os.path.exists(file_name) == False:
            os.mkdir(file_name)

        # 保存数据
        with open(file_name, 'wb') as w:
            w.write(data)

    # 主要逻辑
    def main(self):
        # 循环式赋值 -- 下一页
        next_p = self.url
        while next_p:
            # 发起请求
            response = self.url_request(next_p)
            # 解析响应 -- item, next_p
            item, next_p = self.parse(response)
            # 存储数据库 -- redis, mysql
            self.connect_redis(item)
            self.connect_mysql(item)


if __name__ == '__main__':
    # 实例化一个对象 -- 对象.方法
    spider = Crawl_Spider()
    spider.main()
