# -*- coding: utf-8 -*-
import scrapy
import os
import pickle
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ArticleSpider.settings import BASE_DIR
import time
from PIL import ImageGrab
from mouse import move,click
from ArticleSpider.items import LagouJobItemLoader, LagouJobItem
from utils.common import get_md5
from datetime import datetime


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=('zhaopin/.*')),follow=True),
        Rule(LinkExtractor(allow=('gongsi/j\d+.html')), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )



    def start_requests(self):
        #去使用selenium模拟登陆后拿到cookie交给request使用
        #1.模拟登陆
        #2.从文件中读取cookie
        cookies =[]
        if os.path.exists(BASE_DIR+"/cookies/lagou.cookie"):
            cookies = pickle.load(open(BASE_DIR+"/cookies/lagou.cookie","rb"))

        if not cookies:
            from selenium import webdriver
            browser = webdriver.Chrome()
            browser.get('https://passport.lagou.com/login/login.html')
            # try:
            #     browser.maximize_window()
            # except:
            #     pass
            #login_success = False
            browser.find_element_by_css_selector('.form_body .input.input_white').send_keys('13894937529')
            browser.find_element_by_xpath('//input[@placeholder="请输入密码"]').send_keys('dlb12345')
            browser.find_element_by_xpath("//div[@class='input_item btn_group clearfix sense_login_password']//input[@class='btn btn_green btn_active btn_block btn_lg']").click()
            time.sleep(10)
            cookies = browser.get_cookies()
            # 写入cookie到文件中
            pickle.dump(cookies, open(BASE_DIR + "/cookies/lagou.cookie", "wb"))

            #
            #     if geetest_copyright:
            #         canvas = browser.find_element_by_xpath(
            #             "//canvas[@class='geetest_canvas_slice geetest_absolute']")
            #         time.sleep(2)
            #         location = canvas.location
            #         size = canvas.size
            #         top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location[
            #             'x'] + size['width']
            #         box = (left, top + 118, right, bottom + 118)
            #         im = ImageGrab.grab(bbox=box)
            #         im.save(BASE_DIR+"/images/12.png")
            #         return im
            #


        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']

        for url in self.start_urls:
            yield scrapy.Request(url,dont_filter=True,cookies=cookie_dict)





    def parse_job(self, response):
        #解析拉勾网的职位
        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_css("title", ".job-name::attr(title)")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("salary", ".job_request .salary::text")
        item_loader.add_xpath("job_city", "//*[@class='job_request']/p/span[2]/text()")
        item_loader.add_xpath("work_years", "//*[@class='job_request']/p/span[3]/text()")
        item_loader.add_xpath("degree_need", "//*[@class='job_request']/p/span[4]/text()")
        item_loader.add_xpath("job_type", "//*[@class='job_request']/p/span[5]/text()")

        item_loader.add_css("tags", '.position-label li::text')
        item_loader.add_css("publish_time", ".publish_time::text")
        item_loader.add_css("job_advantage", ".job-advantage p::text")
        item_loader.add_css("job_desc", ".job_bt div")
        item_loader.add_xpath("job_addr", "//div[@class='work_addr']")
        item_loader.add_css("company_name", "#job_company dt a img::attr(alt)")
        item_loader.add_css("company_url", "#job_company dt a::attr(href)")
        item_loader.add_value("crawl_time", datetime.now())

        job_item = item_loader.load_item()
        return job_item

