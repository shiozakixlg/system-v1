# -*-coding:utf-8 -*-

#https://github.com/django-json-api/django-rest-framework-json-api/blob/develop/rest_framework_json_api/views.py
#http://django-rest-framework-json-api.readthedocs.io/en/stable/getting-started.html#running-the-example-app
# http://getblimp.github.io/django-rest-framework-jwt/

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from yqdata.models import *
from datetime import date, timedelta
import datetime
import pandas as pd
from rest_framework.views import APIView
import traceback
import random
import base64,re
from yqdata.Auths import *
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
import random
from mongoengine import *
import json
from mongoengine.queryset.visitor import Q
from serializers import PostSerializer
import logging
logger = logging.getLogger('django')

connect('yuqing', alias='default', host='118.190.133.203', port=27016,username='yuqing',password='yuqing@2017')
datatype_objs = Datatype_name.objects.only("data_type", 'datatype_name')
DTLIST = [(i.data_type, i.datatype_name) for i in datatype_objs]

datatype_objs = Datatype_name.objects.only("data_type", 'datatype_name')
DTDICT = {i.data_type: i.datatype_name for i in datatype_objs}

topic_objs = Topic.objects.only("_id",'topic_name')
TOPICLIST= [(i._id, i.topic_name) for i in topic_objs]

datatype_objs = Datatype_name.objects.only("data_type", 'datatype_name')
datatypedict={}
for item in datatype_objs:
    datatypedict[item.data_type]=item.datatype_name

site_objs = Site.objects.only("_id", 'site_name')
sitedict={}
for item in site_objs:
    sitedict[item._id]=item.site_name

def decode_base64(auth_token):
    missing_padding = 4 - len(auth_token)%4
    if missing_padding:
            auth_token+=b'='*missing_padding
    tokens = base64.decodestring(auth_token)
    return tokens
    
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


class hotTopic(APIView):   # http://127.0.0.1:8081/yqdata/hottopic
    @csrf_exempt
    def get(self, request, format=None):
        # userid=int(request.GET['userId'])
        json_out={}
        data=[]
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))

        # tokens = base64.b64decode(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']
            try:
                # res=Hot_Topic.objects(Q(user_id=userid)&Q(_id__lte=137))
                res=Hot_Topic.objects(Q(_id__lte=140))
                for topic in res:
                    temp={}
                    temp['topicId']=topic._id
                    temp['topicName']=topic.topic_name
                    temp['topicKeywords']=topic.topic_kws
                    temp['imgs']= []
                    if topic._id == 130:
                        temp['imgs'] = [
                        "http://www.moe.edu.cn/jyb_xwfb/xw_fbh/moe_2069/xwfbh_2017n/xwfb_070621/201706/W020170621386205134556.jpg",
                            "http://www.moe.gov.cn/jyb_xwfb/s6052/moe_838/201805/W020180503693998846906.jpg"
                                            ]
                    elif topic._id == 131 :
                        temp['imgs'] = [
                                    "https://gss0.baidu.com/-vo3dSag_xI4khGko9WTAnF6hhy/zhidao/wh%3D600%2C800/sign=62b13c2e0d46f21fc9615655c6144758/cefc1e178a82b901ffebb1e6748da9773812efa5.jpg",
                                        "http://www.81.cn/hkht/attachement/jpg/site351/20150921/18037331c3e11769f42e0e.jpg"
                                            ]
                    elif topic._id == 132:
                        temp['imgs'] = [
                        "http://img.caixin.com/2017-05-28/1495931830739657_480_320.jpg",
                            "http://img.caixin.com/2017-05-28/1495931818880517.jpg"
                                            ]   
                    elif topic._id == 133 :
                        temp['imgs'] = [
                        "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1525780379793&di=a3a5919e75d989bd440cbaf220285986&imgtype=0&src=http%3A%2F%2Fn.sinaimg.cn%2Fnews%2F20170111%2Fd009-fxzkssy1982912.jpg",
                        "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1525780367057&di=4fa93c0e58282e8b922ab9164582251d&imgtype=0&src=http%3A%2F%2Fi2.sinaimg.cn%2Fdy%2Fzl%2Fzatan%2F2015-12-17%2FU12776P1T940D5128F24202DT20151217094145.jpg"

                                            ]
                    elif topic._id == 134 :
                        temp['imgs'] = [
                        "http://img1.cache.netease.com/catchpic/8/86/866900747709FBDAD41BC788DC166E85.jpg",
                            "http://www.cs090.com/uploads/userup/333977/2015/1451104091-62H352.jpg"
                                            ]
                    elif topic._id == 135 :
                        temp['imgs'] = [
                        "https://goss3.vcg.com/creative/vcg/800/version23/VCG21a809942a0.jpg",
                            "http://www.gsstc.gov.cn/pic/2014_04/%7B194C4BEF-CA53-41CB-17F9-247BE28F05BE%7D.JPG"
                                            ]
                    elif topic._id == 137 :
                        temp['imgs'] = [
                        "http://www.17ok.com/files_root/upload_file/media/images/201310/20131014112307322.jpg",
                            "http://jjckb.xinhuanet.com/images/2014-12/20/xin_111211201146295262568.jpg"
                        ]
                    elif topic._id == 138 :
                        temp['imgs'] = [
                                "http://image.sinajs.cn/newchart/hk_stock/min_660/hsi.gif",
                                    "http://www.cash.com.hk/en/img/banner.jpg"
                        ]
                    elif topic._id == 139 :
                        temp['imgs'] = [
                                "http://campusrd.zhaopin.com/CompanyLogo/20141018/492BFE08208B4E1E9590F1CCE0784F8A.jpg",
                                "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1525780345536&di=d559538bb39e2c9db59177e851842025&imgtype=0&src=http%3A%2F%2Fcdns.soufunimg.com%2Fimgs%2Fhouse%2F2015_08%2F10%2Fhefei%2F1439169810477_000.jpg"

                        ]
                    elif topic._id == 136 :
                        temp['imgs'] = [
                                "http://finance.ce.cn/rolling/201305/13/W020130615723679354246.jpg",
                                    "http://www.0938f.com/userfiles/image/20150924/24100931069729c1de2991.jpg"
                        ]
                    else :
                        pass
                    # res =  Post_News.objects(hot_topic_id=topic._id)
                    # for post_res in res :
                    #     if len(post_res.img_url) > 5:
                    #         temp['imgs'].append(post_res.img_url)
                    #     else :
                    #         pass
                    # try:        
                    #     temp['imgs'] = random.sample(temp['imgs'],5)
                    # except:
                    #     temp['imgs'] = temp['imgs']
                    temp['summary']=topic.summary
                    data.append(temp)
                json_out['code']=0
                json_out['success']=True
                json_out['data']=data
            except:
                traceback.print_exc()
                json_out['code']=1
                json_out['success']=False
                json_out['data']={}

            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else:
            json_out['code'] = 1
            json_out['data'] = '认证失败'
            json_out['success'] = False
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

class Hot_Topic_analysis(APIView):  # http://127.0.0.1:8081/yqdata/hot_topic_analysis/
    @csrf_exempt
    def get(self, request, format=None):
        # userid=int(request.GET['userId'])
        topicid=int(request.GET['topicId'])
        json_out={}
        data={}
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))

        # tokens = base64.b64decode(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']
            try:
                year_now=date.today().year
                month_now=date.today().month
                day_now=date.today().day
                datatype_list = Datatype_name.objects
                month_find=0
                year_find=0
                date_find_min=None
                date_find_max=None
                if month_now<3:
                    month_find=month_now-2+12
                    year_find=year_now-1
                else:
                    month_find=month_now-2
                    year_find=year_now
                date_find_min=datetime.datetime.combine(date(year_find, month_find, 1), datetime.time.min)
                date_find_max=datetime.datetime.combine(date(year_now, month_now, day_now), datetime.time.max)
                topics=Hot_Topic.objects(_id=topicid)
                topics_name = []
                topic_relat_list = []
                topic_relations = Topic_Relation.objects(Q(_id=topicid))
                # print len(topic_relations)
                for topic_relat in topic_relations:
                    index = topic_relat._id - 130
                    for ind,val in enumerate(topic_relat.topic_relat) :
                        # print '222'
                        if index == ind :
                            continue
                        triple_group = {}
                        triple_group['source'] = index
                        triple_group['target'] = ind
                        triple_group['weight'] = val
                        # triple_group = [index,ind,val]
                        topic_relat_list.append(triple_group)


                

                all_topics = Hot_Topic.objects(Q(_id__gte=130)&Q(_id__lte=139))
                print len(all_topics)
                for topic in all_topics:
                    topic_obj = {}
                    topic_obj['id'] = topic._id
                    topic_obj['topic_name'] = topic.topic_name
                    topic_obj['topic_kws'] = topic.topic_kws
                    topic_obj['user_id'] = topic.user_id
                    topic_obj['user_name'] = topic.user_name
                    topic_obj['summary'] = topic.summary
                    topics_name.append(topic_obj)
                for topic in topics:
                    data['topicId']=topic._id
                    data['topic_index']=topic._id-130

                    res_evos=Topic_evolution.objects(Q(topic_id=str(topicid)))
                    print '11'
                    # count = 0
                    data_list=[]
                    for item in res_evos:
                        # count += 1
                        # if count == 500 :
                        #   break
                        # else :
                        #   pass
                        temp={}
                        # temp['id']=str(item._id)
                        temp['time']=item.time
                        temp['number']=item.number
                        temp['topic_id']=item.topic_id
                        temp['word']=item.word
                        # temp['topic']=item.topic[0]
                        data_list.append(temp)
                    data['topic_info']=data_list

                    img_list = []

                    data['topicName']=topic.topic_name
                    data['topic_kws']={}
                    data['all_topic']=topics_name
                    data['topic_relation']=topic_relat_list
                    for kw in topic.topic_kws:
                        data['topic_kws'][kw] = random.randint(1,100)
                    # data['topic_kws']=topic.topic_kws
                    # 
                    click_num=0
                    postdata=[]
                    for data_type in datatype_list:
                    	print '11111111'
                        res1=Post_News.objects(Q(hot_topic_id=topicid)&Q(data_type=data_type.data_type)).only('pt_time','site_id','data_type','comm_num','img_url','title','content')
                        # res1=Post_News.objects(Q(hot_topic_id=topicid)).only('pt_time','site_id','data_type','comm_num')
                        # click_num=res1.sum('comm_num')
                        print len(res1)
                        # click_num=click_num+res1.sum('comm_num')
                        for post in res1:
                            temp={}
                            temp['postTime']=post.pt_time
                            temp['site_id']=post.site_id
                            temp['title']=post.title
                            if len(post.img_url) > 5:
                                img_list.append(post.img_url)
                            else :
                                pass
                            temp['content']=post.content[:100]
                            temp['dataType']=post.data_type
                            temp['site_name']=sitedict[int(post.site_id)]
                            temp['dataTypeName']=datatypedict[int(post.data_type)]
                            postdata.append(temp)

                    # summa = 0

                    
                    # for post in res1[:200]:

                    #   # if summa > 100 :
                    #   #   continue
                    #   # else:
                    #   #   pass
                    #   # summa +=1

                    #     temp={}
                    #     temp['postTime']=post.pt_time
                    #     temp['site_id']=post.site_id
                    #     temp['title']=post.title
                    #     if len(post.img_url) > 5:
                    #         img_list.append(post.img_url)
                    #     else :
                    #         pass
                    #     temp['content']=post.content
                    #     temp['dataType']=post.data_type
                    #     temp['site_name']=sitedict[int(post.site_id)]
                    #     temp['dataTypeName']=datatypedict[int(post.data_type)]
                    #     postdata.append(temp)
                    try:
                        data['img_url'] = random.sample(img_list,5)
                    except:
                        data['img_url'] = img_list

                    data['clickNums']=click_num
                    data['postData']=postdata
                json_out['code']=0
                json_out['success']=True
                json_out['data']=data
            except:
                traceback.print_exc()
                json_out['code']=1
                json_out['success']=False
                json_out['data']={}

            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else:
            json_out['code'] = 1
            json_out['data'] = '认证失败'
            json_out['success'] = False
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

def is_leap_year(year):
    if (year%4)==0:
        if (year%100)==0:
            if (year%400)==0:
                return 1
            else:
                return -1
        else:
            return 1
    else:
        return -1

class courseTest(APIView):   # http://127.0.0.1:8081/yqdata/coursetest
    @csrf_exempt
    def get(self, request, format=None):
        # userid=int(request.GET['userId'])
        json_out={}
        data=[]
        # tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))

        # # tokens = base64.b64decode(request.META.get('HTTP_AUTHORIZATION'))
        # time_stamp = tokens[-13:-3]

        if 1:

            # tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            # pld = Auth.decode_auth_token(tokens)
            user_id = 1
            # user_id = pld['data']['id']
            # login_time = pld['data']['login_time']
            try:
                # res=Hot_Topic.objects(Q(user_id=userid)&Q(_id__lte=137))
                res=Hot_Topic.objects(Q(_id__lte=140))
                for topic in res:
                    temp={}
                    temp['topicId']=topic._id
                    temp['topicName']=topic.topic_name
                    temp['topicKeywords']=topic.topic_kws
                    temp['imgs']= []

                    res =  Post_News.objects(hot_topic_id=topic._id)
                    for post_res in res :
                        if len(post_res.img_url) > 5:
                            temp['imgs'].append(post_res.img_url)
                        else :
                            pass
                    try:        
                        temp['imgs'] = random.sample(temp['imgs'],5)
                    except:
                        temp['imgs'] = temp['imgs']
                    temp['summary']=topic.summary
                    data.append(temp)
                json_out['code']=0
                json_out['success']=True
                json_out['data']=data
            except:
                traceback.print_exc()
                json_out['code']=1
                json_out['success']=False
                json_out['data']={}

            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else:
            json_out['code'] = 1
            json_out['data'] = '认证失败'
            json_out['success'] = False
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
