# -*-coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from django.shortcuts import render
from bson.objectid import ObjectId
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import date, timedelta
import datetime
import pandas as pd
import time
from rest_framework.views import APIView
import traceback
import random
import re
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
import base64,re
from django.http import HttpResponse
import random
from mongoengine import *
import json
from mongoengine.queryset.visitor import Q
from serializers import PostSerializer
from elasticsearch import Elasticsearch
import traceback
from models import *
# from elasticsearch_dsl import Search
connect('yuqing', alias='default', host='10.31.243.108', port=27016, username='yuqing', password='yuqing@2017')
# client = Elasticsearch('114.215.47.173:9200')
# client = Elasticsearch(hosts=["127.0.0.1"])
# s = Search(using=client,index="bbc_index",doc_type="bbc")
# s.query("match",title="¹ú¼Ò")
# print type(s)
# print s
# response = s.execute(ignore_cache=True)
# print type(response)
# print response
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

class Esearch(APIView):   # http://127.0.0.1:8081/yqdata/esearch
    @csrf_exempt
    def get(self, request, format=None):
        querystring=str(request.GET['keyword'])
        pageth=int(request.GET['page'])
        # querystring = querystring.decode('gbk')
        json_out={}
        data=[]
        try:
            client = Elasticsearch('114.215.47.173:9200')
            response = client.search(  # Ô­ÉúµÄelasticsearch½Ó¿ÚµÄsearch()·½·¨£¬¾ÍÊÇËÑË÷£¬¿ÉÒÔÖ§³ÖÔ­ÉúelasticsearchÓï¾ä²éÑ¯
                    index="cpost_index",  # ÉèÖÃË÷ÒýÃû³Æ
                    doc_type="course_post",  # ÉèÖÃ±íÃû³Æ
                    body={  # ÊéÐ´elasticsearchÓï¾ä
                        "query": {
                            "multi_match": {  # multi_match²éÑ¯
                            "query": querystring,  # ²éÑ¯¹Ø¼ü´Ê
                            "fields": ["title", "content"]  # ²éÑ¯×Ö¶Î
                        }
                    },
                    "from": (pageth-1)*10,
                    "size": 10,
                    "highlight":{  
                        "pre_tags": ['<span class="keyWord">'],  
                        "post_tags": ['</span>'], 
                        "fields": {  
                            "title": {}, 
                            "content": {}  
                        }
                    }
                }
            )
            total_nums = response["hits"]["total"]
            hit_list = []
            for hit in response["hits"]["hits"]:
                hit_dict = {}
                if "title" in hit["highlight"]:  # 
                    hit_dict["title"] = "".join(hit["highlight"]["title"]).strip()  # 
                else:
                    hit_dict["title"] = hit["_source"]["title"].strip()  # 

                if "content" in hit["highlight"]:  # 
                    hit_dict["content"] = "".join(hit["highlight"]["content"]).strip()  # 
                else:
                    hit_dict["content"] = hit["_source"]["content"].strip()[:400]  # 
                temp = hit["_source"]["content"].replace('\n','').replace(' ','').replace(u'图片版权','').replace(u'Imagecaption','').strip()
                # temp = re.sub(u"[^\u4e00-\u9fa5]+","".decode("utf8"),temp)
                if hit["_source"]["board"] != u'CNN中文网':
                    try:
                        temp = temp[:temp.index('/**/')]
                    except:
                        pass
                else:
                    try:
                        temp = temp[:temp.index('document')]
                    except:
                        pass
                # hit_dict["content"] = temp
                hit_dict["url"] = hit["_source"]["url"]
                hit_dict["board"] = hit["_source"]["board"]
                # hit_dict["title"] = hit["_source"]["title"]
                hit_dict["pt_time"] = hit["_source"]["pt_time"]
                hit_dict["st_time"] = hit["_source"]["st_time"]
                hit_dict["data_type"] = hit["_source"]["data_type"]
                hit_dict['score'] = hit["_score"]
                hit_list.append(hit_dict)
            json_out['sums'] = total_nums
            json_out['code']=0
            json_out['success']=True
            json_out['data']=hit_list

        except:
            traceback.print_exc()
            json_out['code']=1
            json_out['success']=False
            json_out['data']={}

        return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")



class Esort(APIView):   # http://127.0.0.1:8081/yqdata/esort
    @csrf_exempt
    def get(self, request, format=None):
        cate=int(request.GET['category'])
        pageth=int(request.GET['page'])
        querystring=str(request.GET['keyword'])
        # querystring = querystring.decode('gbk')
        json_out={}
        data=[]
        try:
            client = Elasticsearch('114.215.47.173:9200')
            response = client.search(  # Ô­ÉúµÄelasticsearch½Ó¿ÚµÄsearch()·½·¨£¬¾ÍÊÇËÑË÷£¬¿ÉÒÔÖ§³ÖÔ­ÉúelasticsearchÓï¾ä²éÑ¯
                    index="cpost_index",  # ÉèÖÃË÷ÒýÃû³Æ
                    doc_type="course_post",  # ÉèÖÃ±íÃû³Æ
                    body={  # ÊéÐ´elasticsearchÓï¾ä
                      "query": {
                          "bool":{
                              "must": [{"match": {"title":querystring}},{"match": {"content":querystring}}],
                              "filter": [{"term": {"data_type": cate}}]
                          }
                          
                    },
                    "from": (pageth-1)*10,
                    "size": 10,
                    "highlight":{  
                        "pre_tags": ['<span class="keyWord">'],  
                        "post_tags": ['</span>'], 
                        "fields": {  
                            "title": {}, 
                            "content": {}  
                        }
                    }
                }
            )
            total_nums = response["hits"]["total"]
            hit_list = []
            for hit in response["hits"]["hits"]:
                hit_dict = {}
                if "title" in hit["highlight"]:  # 
                    hit_dict["title"] = "".join(hit["highlight"]["title"]).strip()  #
                else:
                    hit_dict["title"] = hit["_source"]["title"].strip()  # 

                if "content" in hit["highlight"]:  # 
                    hit_dict["content"] = "".join(hit["highlight"]["content"]).strip()  # 
                else:
                    hit_dict["content"] = hit["_source"]["content"].strip()[:400]  # 
                temp = hit["_source"]["content"].replace('\n','').replace(' ','').replace(u'图片版权','').replace(u'Imagecaption','').strip()
                # temp = re.sub(u"[^\u4e00-\u9fa5]+","".decode("utf8"),temp)
                if hit["_source"]["board"] != u'CNN中文网':
                    try:
                        temp = temp[:temp.index('/**/')]
                    except:
                        pass
                else:
                    try:
                        temp = temp[:temp.index('document')]
                    except:
                        pass
                # hit_dict["content"] = 
                hit_dict["url"] = hit["_source"]["url"]
                hit_dict["board"] = hit["_source"]["board"]
                # hit_dict["title"] = hit["_source"]["title"]
                hit_dict["pt_time"] = hit["_source"]["pt_time"]
                hit_dict["st_time"] = hit["_source"]["st_time"]
                hit_dict["data_type"] = hit["_source"]["data_type"]
                hit_dict['score'] = hit["_score"]
                # if hit_dict["data_type"] == cate:
                hit_list.append(hit_dict)
                # else:
                #     pass
            json_out['sums'] = total_nums
            json_out['code']=0
            json_out['success']=True
            json_out['data']=hit_list
        except:
            traceback.print_exc()
            json_out['code']=1
            json_out['success']=False
            json_out['data']={}

        return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

class Record_In(APIView):   # /yqdata/recordin
    @csrf_exempt
    def get(self, request, format=None):
        keyword = request.GET['keyword']
        url = str(request.GET['url'])
        json_out = {}
        # print url
        print url
        # print type(url)
        if keyword == '' :
        	json_out['code']=1
        	json_out['success']=False
        	json_out['data']='查询为空'
        	return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        try:
            if url == '-1' :
                print '11111'
                record = Log_Kws.objects(key_word=keyword)
                if len(record) == 0:

                    obj_id = ObjectId()
                    
                    col = Log_Kws(
                                _id=obj_id,
                                key_word=keyword,
                                times=1)
                    col.save()


                else:
                    record_update = record.first()
                    record_update.times += 1
                    record_update.save()


            else:

                record = Log_Url.objects(Q(key_word=keyword)&Q(url=url))
                if len(record) == 0:
                    obj_id = ObjectId()
                    col = Log_Url(
                            _id=obj_id,
                            key_word=keyword,
                            url=url,
                            times=1)
                    col.save()
                else:
                    record_update = record.first()
                    record_update.times += 1
                    record_update.save()
            obj_id2 = ObjectId()
            col2 = Log_Timing(
                        _id=obj_id2,
                        key_word=keyword,
                        url=url,
                        timing=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                    )
            col2.save()

            json_out['code']=0
            json_out['success']=True
            json_out['data']='添加成功'
        except:
            traceback.print_exc()
            json_out['code']=1
            json_out['success']=True
            json_out['data']='添加失败'
        return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")



class Record_Out(APIView):  # /yqdata/Record_Out
    @csrf_exempt
    def get(self, request, format=None):
        
        json_out = {}
        data = []
        try:
            keywords = Log_Kws.objects()
            for item in keywords:
                temp = {}
                temp['name'] = item.key_word
                temp['value'] = item.times
                temp['children'] = []
                leaves = Log_Url.objects(key_word=item.key_word)
                for each in leaves:
                    temp_url = {}
                    temp_url['name'] = each.url
                    temp_url['value'] = each.times
                    temp['children'].append(temp_url)
                data.append(temp)

            json_out['code']=0
            json_out['success']=True
            json_out['data']=data
        except:
            json_out['code']=1
            json_out['success']=True
            json_out['data']='返回失败'

        return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")



