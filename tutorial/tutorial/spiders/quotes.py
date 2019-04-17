# -*- coding: utf-8 -*-
import scrapy
from tutorial.items import TutorialItem
from selenium import webdriver
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        # 配置不加载图片
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        # 配置无头浏览器
        chrome_options.add_argument('--headless')
        self.browser = webdriver.Chrome(options=chrome_options)
        super(QuotesSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        # 爬虫推出时候关闭浏览器
        self.browser.quit()

    def parse(self, response):
        for quote in response.css('div.quote'):
            text = quote.css('span.text::text').get()
            author = quote.css('span small::text').get()
            tags = ','.join(quote.css('div.tags a.tag::text').getall())

            tutorial_item = TutorialItem()
            for field in tutorial_item.fields:
                tutorial_item[field] = eval(field)
            yield tutorial_item

        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
