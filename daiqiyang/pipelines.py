# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import requests
from daiqiyang import settings
import os
import pymysql
from twisted.enterprise import adbapi
import codecs
import json

class DaiqiyangPipeline(object):
    def process_item(self, item, spider):
        print("item : %s  url:%s")
        if 'image_urls' in item:
            images = []
            dir_path = '%s/%s' % (settings.IMAGES_STORE, spider.name)

            request_data = {'allow_redirects': False,
             'auth': None,
             'cert': None,
             'data': {},
             'files': {},
             'headers': {
                        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "Accept-Encoding":"gzip, deflate",
                        "Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                        "Cache-Control":"max-age=0",
                        "Connection":"keep-alive",
                        "Host": "www.daiqiyang.com",
                        "Referer":"http://www.daiqiyang.com/gaoqing/20171007212512-2.html",
                        "Cookie":"UM_distinctid=15ef72d09641f8-0207596f43e4de8-4c322f7c-1fa400-15ef72d0965266; CNZZDATA4166195=cnzz_eid%3D167669602-1507380508-null%26ntime%3D1507450999; Hm_lvt_bfaf38a27108429d724db3384dfc9680=1507385478,1507437965; ASP.NET_SessionId=1cz21m0r1wa1xbmo1bb3biba; Hm_lpvt_bfaf38a27108429d724db3384dfc9680=1507455067",
                        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
                        },
             'method': 'get',
             'params': {},
             'proxies': {},
             'stream': True,
             'timeout': 30,
             'url': '',
             'verify': True}

            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            for image_url in item['image_urls']:
                request_data['url'] = image_url
                us = image_url.split('/')[3:]
                image_file_name = '_'.join(us)
                file_path = '%s/%s' % (dir_path, image_file_name)
                images.append(file_path)
                if os.path.exists(file_path):
                    continue

                with open(file_path, 'wb') as handle:
                    response = requests.request(**request_data)
                    for block in response.iter_content(1024):
                        if not block:
                            break

                        handle.write(block)

            item['images'] = images
        return item


class JsonWithEncodingPipeline(object):
    '''保存到文件中对应的class
       1、在settings.py文件中配置
       2、在自己实现的爬虫类中yield item,会自动执行'''
    def __init__(self):
        self.file = codecs.open('info1.txt', 'w', encoding='utf-8')#保存为json文件
    def process_item(self, item, spider):
        #line = json.dumps(dict(item)) + "\n"#转为json的
        self.file.write(str(item) + "\n")#写入文件中
        return item
    def spider_closed(self, spider):#爬虫结束时关闭文件
        self.file.close()