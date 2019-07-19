from django.db import models

# Create your models here.
from datetime import datetime
from elasticsearch_dsl import DocType,Date,Nested,Boolean,analyzer,Completion,Keyword,Text,Integer
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
connections.create_connection(hosts=['localhost'])

# class ArticleType(DocType):
#     #伯乐在线文章类型
#     title = Text(analyzer="ik_max_word")
#     create_date = Date()
#     url = Keyword()
#     url_object_id = Keyword()
#     front_image_url = Keyword()
#     front_image_path = Keyword()
#     praise_nums = Integer()
#     comment_nums = Integer()
#     fav_nums = Integer()
#     tags = Text(analyzer="ik_max_word")
#     content = Text(analyzer="ik_max_word")
#
#     class Meta:
#         index = "jobbole"
#         doc_type = "article"

class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnalyzer("ik_max_word",filter = ["lowercase"])#设置大小写转化

class ArticleType(DocType):
    #拉钩文章类型
    suggest = Completion(analyzer=ik_analyzer)
    url = Keyword()
    url_object_id = Keyword()
    title = Text(analyzer="ik_max_word")
    salary = Text(analyzer="ik_max_word")
    job_city = Text(analyzer="ik_max_word")
    work_years = Text(analyzer="ik_max_word")
    degree_need = Text(analyzer="ik_max_word")
    job_type = Text(analyzer="ik_max_word")
    publish_time =Text(analyzer="ik_max_word")
    tags = Text(analyzer="ik_max_word")
    job_advantage = Text(analyzer="ik_max_word")
    job_desc = Text(analyzer="ik_max_word")
    job_addr = Text(analyzer="ik_max_word")
    company_url = Keyword()
    company_name = Text(analyzer="ik_max_word")
    crawl_time = Date()
    #crawl_update_time = Date()

    class Meta:
        index = "lagou"
        doc_type = "job"

if __name__ == "__main__":
    ArticleType.init()








