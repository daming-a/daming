import requests
from lxml import etree


# 主页面 多页数据 -- next_url 通过翻页获取多页数据
# 封装的 -- 请求网页request
def url_request(url):
    return requests.get(url).content


# 封装的 -- 获取响应体，并解析响应体内的目标数据，以及下一页的网址  content_list,next_url 以元组-解构的形式
def get_content_list(html):
    tree = etree.HTML(html)
    # 获取数据，并进行数据的结构化 item = {key:value} 的形式进行存储
    content_list = tree.xpath('')
    item = {}
    for i in content_list:
        item['key'] = i

    # 获取下一页next_url，进行深度爬取
    next_url = tree.xpath('')
    # 巧妙设计 -- 结合run()函数 使用到元组的解构
    return content_list, next_url


# 持久化存储 -- 本地文本 二进制文件 数据库 mongodb redis mysql
def save_content_list(content_list):
    pass


# 从主页获取详情页的detail_url
# 关于详情页的 -- 递归调用 -- 目的搜集详情页的数据，通过if判断，可以终止递归，最终返回详情页的数据
def detail_url_content(detail_url, content_list):
    # 递归 获取详情页的全部数据，并返回
    html = url_request(detail_url)
    tree = etree.HTML(html)
    # 获取到详情页数据，并返回    --   结合递归  使用列表的content_list += [...] 扩充列表内容
    content_list += tree.xpath('')
    # 获取到详情页的下一页next_url，递归调用自己，目的--获取更多本详情页的数据
    next_url = tree.xpath('')
    # 通过判断，结束递归，返回数据
    if next_url:
        return detail_url_content(next_url, content_list)
    # 获得扩充后的 所有的数据列表，并返回
    return content_list


def run(start_url):
    # 先定义一个初始url开启循环  通过循环体内解构出来的next_url 进行重新赋值 继续循环 直到没有next_url产生 数据搜集完毕 循环结束 程序终止
    next_url = start_url
    while next_url:

        # request 请求 获取到响应体
        html = url_request(next_url)

        # 提取数据，并解析出下一页的网址  --  content,next_url
        # next_url被重新赋值，当提取不到next_url时，循环结束 -- 程序终止
        content_list, next_url = get_content_list(html)

        # 保存数据
        save_content_list(content_list)


if __name__ == '__main__':
    start_url = ''
    run(start_url)
