__author__ = 'xubuju'
from scrapy.selector import Selector
import scrapy
from mm131.items import Mm131Item
from scrapy.loader import ItemLoader, Identity
import requests
from scrapy.http import Request
from urllib.parse import urljoin
import re

from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware
from mm131.middlewares.agentResource import UserAgents

import random

class RandomUserAgent(UserAgentMiddleware):
    def process_request(self, request, spider):
        ua=random.choice(UserAgents)
        request.headers.setdefault('User-Agent',ua)

class MeizituSpider(scrapy.Spider):
    name = "mm131"
    allowed_domains = ["mm131.com"]
    start_urls = (
        'http://www.mm131.com/',
    )

    def parse_item(self, response):
        print("parse_item ")
        l = ItemLoader(item=Mm131Item(), response=response)
        l.add_xpath('image_urls', "//div[@class='content-pic']/a/img/@src", Identity())
        l.add_value('url', response.url)
        l.add_xpath('text', "//div[@class='content']/h5/text()")

        return l.load_item()


    def parse(self, response):
        sel = Selector(response)
        print("----------------------------------response:url %s------------------------------ " % response.url)
        for title_next in sel.xpath("//div[@class='nav']/ul/li[position() > 1]/a/@href").extract():
            print("fist for:%s" % title_next)
            yield Request(title_next, callback=self.parse)

        nextPages = sel.xpath("//a[@class='page-en']/text()").extract()
        print("nextPage:%s" % nextPages)
        # list_6_106.html
        #http://www.mm131.com/xinggan/list_6_104.html
        #http://www.mm131.com/xinggan/
        if '末页' in nextPages:
            url = sel.xpath("//a[text()='末页']/@href").extract()
            url = ''.join(url)
            pages = (int)(url[url.rfind('_') + 1:url.rfind('.')])
            responseUrl = response.url
            urlHead = responseUrl[:response.url.rfind('/') + 1]
            print("urlHead:%s" % urlHead)

            for index in range(0, pages):
                tempUrl = responseUrl       #第0页 http://www.mm131.com/xinggan/
                if index != 0:
                    tempUrl = urlHead + url[:url.rfind('_')] + '_' + str(index + 1) + '.html' #非第0页 拼http://www.mm131.com/xinggan/list_6_104.html
                print("tempUrl:%s" % tempUrl)
                yield Request(tempUrl, callback=self.parse)

        #找一个页面上的所有相册
        for next_sel in sel.xpath("//dl[@class='list-left public-box']/dd/a[contains(@href, 'www.mm131.com')]/@href").extract():
            print("while for fist for:%s" % next_sel)
            yield Request(next_sel, callback=self.parse_item) #自己也要解析,不然下面会被当成重复而取不到数据

        #找总共多少页如: '共63页'
        pages = sel.xpath("//span[@class='page-ch'][1]/text()").extract()
        pages = ''.join(pages)
        print("xxxx first print pages %s" % pages)

        if pages == '':
            print("xxx   xxxxxxxxxxxxxxxxxxxxxxxxx")
            return

        #取 '共63页' 中的数字
        pages = re.sub("\D", "", pages)
        print("3 pages %s" % pages)
        if pages == '':
            print("xxxxxxxxxxxxxxxx   xxxxxxxxx")
            return

        print("xxxx two print pages %s" % pages)
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

'''
http://img1.mm131.com/pic/3273/6.jpg
        for title_next in sel.xpath("//div[@class='nav']/ul/li[position() > 1]/a/@href").extract():
            print("fist for:%s" % title_next)
            yield Request(title_next, callback=self.parse)

        select = sel.xpath("//dd/a[@class='page-en']/text()").extract()
        select = ''.join(select)
        print("select : %s" % select)
        if '下一页' in select:
            print("下一页 1")
            for pictrue in sel.xpath("//dd/a[@class='page-en']/@href").extract():
                print("xxxxx pictrue:%s" % pictrue)
                for next_sel in sel.xpath("//dl[@class='list-left public-box']/dd/a[contains(@href, 'www.mm131.com')]/@href").extract():
                    print("while for fist for:%s" % next_sel)
                    yield Request(next_sel, callback=self.parse)
                print("下一页")
                url = response.url + pictrue[-2]
                yield Request(url, callback=self.parse)



        pages = sel.xpath("//dd[@class='page-en']/@href").extract()
        if len(pages) > 2:
            pages = sel.xpath("//span[@class='page-ch'][1]/text()").extract()
            pages = ''.join(pages)
            print("xxxx first print pages %s" % pages)

            if pages == '':
                print("xxx   xxxxxxxxxxxxxxxxxxxxxxxxx")

            pages = re.findall("/d+", pages)
            pages = ''.join(pages)
            if pages == '':
                print("xxxxxxxxxxxxxxxx   xxxxxxxxx")

            print("xxxx two print pages %s" % pages)
            pages = (int)(pages)
            for index in range(0, pages):
                temp = str(index + 1) + '.jpg'
                yield Request(temp, callback=self.parse_item)


        pages = sel.xpath("//dd[@class='page-en']/@href").extract()
        if len(pages > 2):
            pages = sel.xpath("//span[@class='page-ch'][1]/text()").extract()
            pages = ''.join(pages)
            print("xxxx first print pages %s" % pages)

            if pages == '':
                print("xxx   xxxxxxxxxxxxxxxxxxxxxxxxx")
                continue
            pages = re.findall("/d+", pages)
            pages = ''.join(pages)
            if pages == '':
                print("xxxxxxxxxxxxxxxx   xxxxxxxxx")
                continue

            print("xxxx two print pages %s" % pages)
            pages = (int)(pages)
            for index in range(0, pages):
                temp = str(index + 1) + '.jpg'
                yield Request(temp, callback=self.parse_item)



        pages = sel.xpath("//dd[@class='page-en']/@href").extract()

        if len(pages > 2):
            page_link = response.url + pages[-2]

            yield parse_pages(page_link)
            print("second for:%s" % page_link)
            yield Request(page_link, callback=self.parse)
'''
'''
        for next_sel in sel.xpath("//dl[@class='list-left public-box']/dd/a[contains(@href, 'www.mm131.com')]/@href").extract():

            print("second for:%s" % next_sel)
            yield Request(next_sel, callback=self.parse_item)

        for pictrue in sel.xpath("//div[@class='content-pic']/a/img/@src").extract():
            temp = ''.join(pictrue)
            print(temp)
            if temp == '':
                print("xxxxxxxxxxxxxxxx  xxxxx              xxxxx")
                return
            yield self.parse_item(self, pictrue)

        pages = sel.xpath("//span[@class='page-ch'][1]/text()").extract()
        pages = ''.join(pages)
        print("xxxx first print pages %s" % pages)

        if pages == '':
            print("xxx   xxxxxxxxxxxxxxxxxxxxxxxxx")
            return
        pages = re.findall("/d+", pages)
        pages = ''.join(pages)
        if pages == '':
            print("xxxxxxxxxxxxxxxx   xxxxxxxxx")
            return

        print("xxxx two print pages %s" % pages)
        pages = (int)(pages)


        for index in range(0, pages):
            temp = str(index + 1) + '.jpg'

            self.parse_item(response, temp)




        next_sel = sel.xpath("//div[@class='navigation']/div[@id='wp_page_numbers']/ul/li/a/@href").extract()
        print(next_sel)
        for url in next_sel:
            print(url)
            link = 'http://www.meizitu.com' + url
            print('first for %s  response.url:%s' % (link, response.url))
            response.url = link
            yield request(link)

        selectors  = sel.xpath("//div[@class='pic']/a/@href").extract()
        for selector in selectors:
            print('second for link %s' % selector)
            yield self.parse_item(selector, response)

        if len(pages) > 2:
            page_link = pages[-2]
            page_link = page_link.replace('/a/', '')
            print('page_link %s%s ' % ('http://www.meizitu.com/a/%s', page_link))
            request = scrapy.Request('http://www.meizitu.com/a/%s' % page_link, callback=self.parse_item)
            yield request
        '''
