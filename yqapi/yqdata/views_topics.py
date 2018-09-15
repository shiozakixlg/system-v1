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
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
import base64,re
from yqdata.Auths import *
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


class Topic_statistics(APIView):   # http://127.0.0.1:8081/yqdata/topic_statistics/ 
    @csrf_exempt
    def get(self, request, format=None):
        userid=int(request.GET['userId'])
        json_out={}
        data=[]
        try:
            res=Topic.objects(Q(user_id=userid))
            for topic in res:
                temp={}
                temp['topicId']=topic._id
                temp['topicName']=topic.topic_name
                temp['topicKeywords']=topic.topic_kws
                temp['imgs']=''
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

class Topic_analysis(APIView):  # http://127.0.0.1:8081/yqdata/topic_analysis/
    @csrf_exempt
    def get(self, request, format=None):
        # userid=int(request.GET['userId'])
        topicid=int(request.GET['topicId'])
        # json_out={}
        # data={}
        json_out={}
        data={}
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        # print '111'
        # tokens = base64.b64decode(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]
        # if abs(int(time_stamp)-int(time.time())) < 60:
        if abs(int(time_stamp)-int(time.time())) < 60:
            # print '11111'
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
                topic=Topic.objects(Q(user_id=user_id)&Q(_id=topicid))[0]
                data['topicId']=topic._id
                res_evos=Topic_evolution.objects(Q(topic_id=str(topicid)))
                # print '11'
                
                # data_list=[]
                # for item in res_evos:
                #     temp={}
                #     temp['id']=str(item._id)
                #     temp['time']=item.time
                #     temp['number']=item.number
                #     temp['topic_id']=item.topic_id
                #     temp['topic']=item.topic[0]
                #     data_list.append(temp)
                data_list=[]
                for item in res_evos:
                    temp={}
                    # aopatemp['id']=str(item._id)
                    temp['time']=item.time
                    temp['number']=item.number
                    temp['topic_id']=item.topic_id
                    temp['word']=item.word
                    data_list.append(temp)
                data['topic_info']=data_list
                data['topicName']=topic.topic_name
                # data['imgs']=[]
                topic_kwslist=[]
                res=Cloud_formain.objects(Q(topic_id=str(topicid))&Q(WORD_TYPE='1m')).order_by('-frequency')[:30].only('word','frequency')

                for item in res:
                    temp={}
                    temp['word']=item.word
                    temp['weight']=item.frequency
                    topic_kwslist.append(temp)
                data['topic_kws']=topic_kwslist
                postdata=[]
                click_num=0
                img_num=0
                img_data=[]
                for data_type in datatype_list:
                    res=Post.objects(Q(topic_id=topicid)&Q(data_type=data_type.data_type)&Q(pt_time__gte=date_find_min)&Q(pt_time__lte=date_find_max)).only('pt_time','site_id','data_type','comm_num')

                    click_num=click_num+res.sum('comm_num')

                    img_res=res(Q(img_url__ne='')&Q(img_url__ne=' ')).only('img_url')
                    if (img_num<5)&(len(img_res)!=0):
                        for item in img_res:
                            img_data.append(item.img_url)
                            img_num=img_num+1
                            if img_num>=5:
                                break



                    for post in res:
                        temp={}
                        temp['postTime']=post.pt_time
                        temp['site_id']=post.site_id
                        temp['dataType']=post.data_type
                        temp['site_name']=sitedict[int(post.site_id)]
                        # temp['site_name']=Site.objects(Q(_id=post.site_id)).only('site_name').first().site_name
                        temp['dataTypeName']=datatypedict[int(post.data_type)]
                        postdata.append(temp)
                if topicid==38:
                    img_data = [
                                "http://szb.gdzjdaily.com.cn/zjwb/page/14/2015-12-01/11/77961448955861504.jpg",
								"http://s8.sinaimg.cn/middle/3e2115f9ha300854afc87&690"
                                ]
                elif topicid==42:
                    img_data = [
                                "http://n.sinaimg.cn/translate/144/w604h340/20180507/0_J2-hacuuvu4487767.jpg",
								"http://n.sinaimg.cn/translate/795/w1434h961/20180505/8P2A-hacuuvt7444425.jpg"
                            ]
                elif topicid==44:
                    img_data = [
                            "http://img.tukuchina.cn/images/front/v/68/dd/235563985405.jpg",
							"http://img.zxxk.com/2015-6/ZXXKCOM201506161120112850082.jpg"
                    ]
                elif topicid==50:
                    img_data = [
                            'http://images.china.cn/news/attachement/jpg/site3/20141013/2616107349730704805.jpg',
                            'http://edu.dahe.cn/zxt/W020080922397012038423.jpg'

                    ]
                elif topicid==45:
                	img_data = [
                			'http://5b0988e595225.cdn.sohucs.com/images/20180508/110fa79b66f74e029d646eb80145b522.png',
                			'http://img3.utuku.china.com/650x0/mili/20180505/6e150a8d-b43c-4fae-b3c3-1b1a82fd1c44.jpg'
                	]
                elif topicid==46:
                	img_data = [
                			'http://p1.img.cctvpic.com/photoworkspace/contentimg/2018/05/08/2018050817521614887.jpg',
                			'http://n.sinaimg.cn/news/crawl/135/w534h401/20180508/bB9e-hacuuvu7683834.jpg'
                	]
                elif topicid==47:
                	img_data = [
                			'https://wpimg.wallstcn.com/c477f0fa-19c0-4ce2-ba7c-96c994d84a36',
                			'http://i2.sinaimg.cn/dy/c/2014-02-13/1392275060_qpAl2X.jpg'
                	]
                elif topicid==48:
                	img_data = [
                		'http://img1.gtimg.com/edu/pics/hv1/83/202/1869/121583318.jpg'
                	]
                elif topicid==49:
                	img_data = [

                	]
                else :
                    pass
                data['imgs']=img_data
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

