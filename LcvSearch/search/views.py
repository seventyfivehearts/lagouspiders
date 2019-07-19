from django.shortcuts import render
from django.views.generic.base import View
from search.models import ArticleType
from django.http import HttpResponse
from elasticsearch import Elasticsearch
import json
import redis
from datetime import datetime

client = Elasticsearch(hosts=["127.0.0.1"])
redis_cli = redis.StrictRedis()
# Create your views here.

class IndexView(View):
    #首页
    def get(self, request):

        top1 = []
        #redis_cli.zincrby("search_keywords_set", 1, key_words)  # key_words存在，分数加1
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)

        for search in topn_search:
            top1.append(search.decode("utf8"))

        return render(request, "index.html", {"topn_search":top1})

class SearchSuggest(View):
    def get(self,request):
        key_words = request.GET.get('s','')
        re_datas = []
        if key_words:
            s= ArticleType.search()
            s = s.suggest('my_suggest',key_words,completion={
                "field":"suggest","fuzzy":{
                    "fuzziness":2
                },
                "size":10
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source["title"])
        return HttpResponse(json.dumps(re_datas),content_type="application/json")

class SearchView(View):
    def get(self,request):
        key_words = request.GET.get("q", "")
        s_type = request.GET.get("s_type", "article")
        top = []
        redis_cli.zincrby("search_keywords_set",1,key_words)#key_words存在，分数加1
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set","+inf","-inf",start=0, num=5)
        #topn_search = top_search.decode(encoding='utf-8')
        for search in topn_search:
            top.append(search.decode("utf8"))
        #print(topn_search[0])
        #print(topn_search)

        #print(type(top))
        page = request.GET.get("p","1")
        try:
            page = int(page)
        except:
            page = 1
        lagou_count = int(redis_cli.get("lagou_count"))
        #print(type(lagou_count))
        start_time = datetime.now()
        response = client.search(
            index = "lagou",
            body={
                "query":{
                    "multi_match":{
                        "query":key_words,
                        "fields":["tags","title","job_desc"]
                    }
                },
                "from":(page-1)*10,
                "size":10,
                "highlight": {
                    "pre_tags": ['<span class="keyWord">'],
                    "post_tags": ['</span >'],
                    "fields": {

                        "title": {},
                        "job_desc":{},
                    }
                }
            }
        )
        end_time = datetime.now()
        last_seconds = (end_time-start_time).total_seconds()
        total_nums = response["hits"]["total"]

        if (page%10) > 0:
            page_nums = int(total_nums/10)+1
        else:
            page_nums = int(total_nums/10)
        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            if "title" in hit["highlight"]:
                hit_dict["title"] = "".join(hit["highlight"]["title"])
            else:
                hit_dict["title"] = hit["_source"]["title"]

            if "job_desc" in hit["highlight"]:
                hit_dict["job_desc"] = "".join(hit["highlight"]["job_desc"])[:500]
            else:
                hit_dict["job_desc"] = hit["_source"]["job_desc"][:500]

            hit_dict["crawl_time"] = hit["_source"]["crawl_time"]
            hit_dict['url'] =  hit["_source"]["url"]
            hit_dict['score'] = hit["_score"]

            hit_list.append(hit_dict)

        return render(request,"result.html",{"all_hits":hit_list,
                                             "key_words":key_words,
                                             "page":page,
                                             "total_nums":total_nums,
                                             "page_nums":page_nums,
                                             "last_seconds":last_seconds,
                                             "lagou_count":lagou_count,
                                             "topn_search":top
                                             })

