__author__ = 'xubuju'
# -*- coding: utf-8 -*-
from scrapy.selector import Selector
import scrapy
from youwu.items import YouwuItem
from scrapy.loader import ItemLoader, Identity
import requests
from scrapy.http import Request
from urllib.parse import urljoin
import re


class youwuSpider(scrapy.Spider):
    name = "youwu"
    allowed_domains = ["youwu.cc"]
    start_urls = (
        'http://www.youwu.cc/guonei/',
        'http://www.youwu.cc/gangtai/',
    )

    def parse_item(self, response):
        print("parse_item ")
        l = ItemLoader(item=YouwuItem(), response=response)
        l.add_xpath('image_urls', "//img[@id='bigimg']/@src", Identity())
        l.add_value('url', response.url)
        l.add_xpath('text', "//div[@id='photos']/h1/text()")

        return l.load_item()


    def parse_third(self, response):
        sel = Selector(response)
         #找总共多少页如: '共63页'
        pages = sel.xpath("//div[@class='pages']/ul/li[1]/a/text()").extract()
        pages = ''.join(pages)
        print("xxxx first print pages %s" % pages)

        #取 '共63页' 中的数字
        pages = re.sub("\D", "", pages)
        print(" pages %s" % pages)

        pages = (int)(pages)
        temp = str(response.url) # http://www.mm131.com/xinggan/3277.html
        for index in range(0, pages):
            url = temp
            if index != 0:
                print("index:%s url:%s" % (index, url))
                url = url[:url.rfind('.')] + '_' + str(index + 1) + '.html'

           # url = 'http://img1.mm131.com/pic/' + midStr + '/' + endStr
            print(url)
            yield Request(url, callback=self.parse_item)


    def parse_second(self, response):
        sel = Selector(response)
        # list_6_106.html
        #http://www.youwu.cc/guonei/list_1.html

        #找一个页面上的所有相册
        for next_sel in sel.xpath("//div[@class='img']/a/@href").extract():
            url = 'http://www.youwu.cc' + ''.join(next_sel)
            print("while for fist for:%s" % next_sel)
            yield Request(url, callback=self.parse_third) #自己也要解析,不然下面会被当成重复而取不到数据


    def parse(self, response):
        sel = Selector(response)
        print("----------------------------------response:url %s------------------------------ " % response.url)

        nextPages = sel.xpath("//div[@id='pageNum']/span/a/text()").extract()
        print("nextPage:%s" % nextPages)
        # list_6_106.html
        #<a href="list_53.html">末页</a>
        if '末页' in nextPages:
            url = sel.xpath("//a[text()='末页']/@href").extract()
            url = ''.join(url)
            pages = (int)(url[url.rfind('_') + 1:url.rfind('.')])
            responseUrl = response.url
            #urlHead = responseUrl[:response.url.rfind('/') + 1]
            print("urlHead:%s" % responseUrl)

            for index in range(0, pages):       #http://www.youwu.cc/guonei/list_2.html
                tempUrl = responseUrl + 'list_' + str(index + 1) + '.html' #非第0页 拼http://www.mm131.com/xinggan/list_6_104.html
                print("tempUrl:%s" % tempUrl)
                yield Request(tempUrl, callback=self.parse_second)

