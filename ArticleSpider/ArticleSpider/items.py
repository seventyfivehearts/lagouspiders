# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import datetime
import re

import redis
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join

from utils.common import extract_num
from ArticleSpider.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT

from w3lib.html import remove_tags
from ArticleSpider.models.es_types import ArticleType


from elasticsearch_dsl.connections import connections
es = connections.create_connection(ArticleType._doc_type.using)#连接es

redis_cli = redis.StrictRedis(host="localhost")




def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip() != "查看地图"]
    return "".join(addr_list)

class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash),

    )
    work_years = scrapy.Field(
        input_processor = MapCompose(remove_splash),
    )
    degree_need = scrapy.Field(
        input_processor = MapCompose(remove_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    tags = scrapy.Field(
        input_processor= Join(",")
    )
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags,handle_jobaddr),
    )
    company_url = scrapy.Field()
    company_name = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()


    def get_insert_sql(self):
        insert_sql = '''
            insert into lagou_job(title, url, url_object_id, salary, job_city, work_years, degree_need,
            job_type, publish_time, job_advantage, job_desc, job_addr, company_name, company_url,
            tags, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_desc=VALUES(job_desc)
        '''
        params = (
            self["title"], self["url"], self["url_object_id"], self["salary"], self["job_city"],
            self["work_years"], self["degree_need"], self["job_type"],
            self["publish_time"], self["job_advantage"], self["job_desc"],
            self["job_addr"], self["company_name"], self["company_url"],
            self["job_addr"], self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )
        return  insert_sql,params


    def save_to_es(self):
        job = ArticleType()
        job.url = self['url']
        job.url_object_id = self['url_object_id']
        job.title = self['title']
        job.salary = self['salary']
        job.job_city = self['job_city']
        job.work_years = self['work_years']
        job.degree_need = self['degree_need']
        job.job_type = self['job_type']
        if self['publish_time']:
            job.publish_time = self['publish_time']
        job.tags = self['tags']
        job.job_advantage = self['job_advantage']
        job.job_desc = self['job_desc']
        job.job_addr = self['job_addr']
        job.company_url = self['company_url']
        job.company_name = self['company_name']
        job.crawl_time = self['crawl_time']
        #job.crawl_update_time = self['crawl_update_time']

        job.suggest = gen_suggests(ArticleType._doc_type.index,((job.title,10),(job.tags,7)))

        job.save()
        redis_cli.incr("lagou_count")

        return



