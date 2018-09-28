__author__ = 'xubuju'
# -*- coding: utf-8 -*-
from scrapy.selector import Selector
import scrapy
from www7160.items import Www7160Item
from scrapy.loader import ItemLoader, Identity
import requests
from scrapy.http import Request
from urllib.parse import urljoin
import re



class youwuSpider(scrapy.Spider):
    name = "www7160"
    allowed_domains = ["7160.com"]
    start_urls = (
        'http://www.7160.com/qingchunmeinv/',
        'http://www.7160.com/xingganmeinv/',
        'http://www.7160.com/meinvmingxing/',
        'http://www.7160.com/xingganmote/',
        'http://www.7160.com/lianglichemo/',
        'http://www.7160.com/xiaohua/',
        'http://www.7160.com/rihanmeinv/',
        'http://www.7160.com/zhenrenxiu/',
    )

    def parse_item(self, response):
        print("parse_item ")
        l = ItemLoader(item=Www7160Item(), response=response)
        l.add_xpath('image_urls', "//div[@class='picsbox picsboxcenter']/p/a/img/@src", Identity())
        l.add_value('url', response.url)
        l.add_xpath('text', "//div[@id='photos']/h1/text()")

        return l.load_item()


    def parse_third(self, response):
        sel = Selector(response)
         #找总共多少页如: '共63页'
        pages = sel.xpath("//div[@class='itempage']/a[1]/text()").extract()
        pages = ''.join(pages)
        print("xxxx first print pages %s" % pages)

        #取 '共63页' 中的数字
        pages = re.sub("\D", "", pages)
        print(" pages %s" % pages)

        pages = (int)(pages)
        temp = str(response.url) # http://www.7160.com/meinv/49564/
        for index in range(0, pages): #http://www.7160.com/meinv/49564/index_2.html
            url = temp
            if index != 0:
                print("index:%s url:%s" % (index, url))
                url = url[:url.rfind('/')] + '/index_' + str(index + 1) + '.html'

           # url = 'http://img1.mm131.com/pic/' + midStr + '/' + endStr
            print(url)
            yield Request(url, callback=self.parse_item)


    def parse_second(self, response):
        sel = Selector(response)
        # list_6_106.html
        #http://www.youwu.cc/guonei/list_1.html

        #找一个页面上的所有相册
        for next_sel in sel.xpath("//ul[@class='new-img']/ul/li/a/@href").extract():
            url = 'http://www.7160.com' + ''.join(next_sel)
            print("while for fist for:%s" % next_sel)
            yield Request(url, callback=self.parse_third) #自己也要解析,不然下面会被当成重复而取不到数据


    def parse(self, response):
        sel = Selector(response)
        print("----------------------------------response:url %s------------------------------ " % response.url)

        nextPages = sel.xpath("//div[@class='page']/a/text()").extract()
        print("nextPage:%s" % nextPages)
        # list_6_106.html
        #list_5_272.html
        if '末页' in nextPages:
            url = sel.xpath("//a[text()='末页']/@href").extract()
            url = ''.join(url)
            pages = (int)(url[url.rfind('_') + 1:url.rfind('.')])
            pagesHead = url[:url.rfind('_') + 1]
            responseUrl = response.url
            #urlHead = responseUrl[:response.url.rfind('/') + 1]
            print("urlHead:%s" % responseUrl)


            for index in range(0, pages):       #http://www.youwu.cc/guonei/list_2.html
                tempUrl = responseUrl + pagesHead + str(index + 1) + '.html' #非第0页 拼http://www.mm131.com/xinggan/list_6_104.html
                print("tempUrl:%s" % tempUrl)
                if index == 0:
                    tempUrl = responseUrl
                yield Request(tempUrl , callback=self.parse_second)

