__author__ = 'xubuju'
# -*- coding: utf-8 -*-

from scrapy.selector import Selector
import scrapy
from daiqiyang.items import DaiqiyangItem
from scrapy.loader import ItemLoader, Identity
import requests
from scrapy.http import Request
from urllib.parse import urljoin
import re
count = 0
class MeizituSpider(scrapy.Spider):
    name = "daiqiyang"
    allowed_domains = ["daiqiyang.com"]
    start_urls = (
        'http://www.daiqiyang.com/',
    )

    def parse_item(self, response):
        print("parse_item ")
        l = ItemLoader(item=DaiqiyangItem(), response=response)
        l.add_xpath('image_urls', "//div[@class='showimg']/a/img/@src", Identity())
        l.add_value('url', response.url)
        l.add_xpath('text', "//div[@class='crumbs']/h1/text()")

        return l.load_item()

    def parse_forth(self, response):
        sel = Selector(response)
        pages = sel.xpath("//div[@class='showsummary']/text()").extract()
        temp = ''.join(pages)
        if temp == '':
            return

        print("pages : %s" % pages)
        pages = ''.join(pages)
        pages = pages.split('张')[-2].strip()
        pages = pages[pages.rfind(u"：") + 1:]

        pages = int(pages)



        for index in range(0, pages):
            url = response.url
            url = ''.join(url)
            url = url[:url.rfind('.')] + '-' + str(index + 1) + '.html'
            print("index:%s url:%s" % (index, url))
            yield Request(url, callback=self.parse_item)

    def parse_third(self, response):
        sel = Selector(response)
                        #找一个页面上的所有相册
        for allPictruePages in sel.xpath("//div[@class='imageitem']/a/@href").extract():
            print("while for fist for:%s" % allPictruePages)
            yield Request(allPictruePages, callback=self.parse_forth) #自己也要解析,不然下面会被当成重复而取不到数据


    def parse_second(self, response):
        sel = Selector(response)
        allPages = sel.xpath("//div[@class='paging']/span/a/@href").extract()
        print("allPages: %s response ur:%s" % (allPages, response.url))
        temp = ''.join(allPages)
        print("allPages %s" % allPages)
        allPages = ''.join(allPages[-2])
        print("allPages %s" % allPages)
        allPages = allPages[allPages.rfind('/') + 1:].strip()
        print("allPages %s" % allPages)
        allPages = int(allPages)

        responseUrl = response.url
        for index in range(0, allPages): #第0页 http://www.daiqiyang.com/daxiong/
            tempUrl = responseUrl + str(index + 1) #http://www.daiqiyang.com/daxiong/3
            print("tempUrl:%s" % tempUrl)
            yield Request(tempUrl, callback=self.parse_third)

    def parse(self, response):
        sel = Selector(response)
        print("---------------------response:url:%s-------------------------" % response.url)
        if 'http://www.daiqiyang.com/' != str(response.url):
            print("----xxxxxxxxxx------response:url:%s-----xxxxxxxx-------" % response.url)
        for title_next in sel.xpath("//div[@class='nav']/a/@href").extract():
            print("fist for:%s" % title_next)
            yield Request(title_next, callback=self.parse_second)









