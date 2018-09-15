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
from django.http import HttpResponse
import random
from mongoengine import *
import json
import base64,re
from yqdata.Auths import *
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

class wallPost(APIView):  # xxxx/yqdata/wallpost

    @csrf_exempt
    def get(self, request, format=None):
        userid=int(request.GET['userId'])
        topicid=int(request.GET['topicId'])
        json_out={}
        data=[]

        try:
            res = Tran_Wall_Post.objects(hot_topic_id=topicid)
            
            for post in res :
                temp = {}
                poster = {}
                temp['url']=post.url
                temp['site_id']=post.site_id
                temp['site_name']=post.site_name
                temp['topic_id']=post.topic_id
                temp['hot_topic_id']=post.hot_topic_id
                temp['board']=post.board
                temp['data_type']=post.data_type
                temp['title']=post.title
                temp['content']=post.content
                temp['pt_time']=post.pt_time
                temp['st_time']=post.st_time
                temp['read_num']=post.read_num
                temp['comm_num']=post.comm_num
                temp['img_url']=post.img_url
                temp['repost_num']=post.repost_num
                temp['lan_type']=post.lan_type
                temp['is_read']=post.is_read
                temp['repost_pt_id']=post.repost_pt_id
                temp['transText']=post.transText

                poster['home_url']=post.poster.home_url
                poster['img_url']=post.poster.img_url
                poster['id']=post.poster.id
                poster['name']=post.poster.name
                poster['follows']=post.poster.follows
                poster['following']=post.poster.following
                poster['post_num']=post.poster.post_num
                poster['level']=post.poster.level
                poster['location']=post.poster.location
                poster['birthday']=post.poster.birthday

                temp['poster']=poster
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

class senHot(APIView):   #xxxx/yqdata/sen_hot

    @csrf_exempt
    def get(self, request, format=None):
        userid=int(request.GET['userId'])
        topicid=int(request.GET['topicId'])
        json_out={}
        data=[]
        try:

            hots = Hot_Value_Trace.objects(topic_id=topicid)
            for hot in hots :
                temp = {}
                temp['date']=hot.date
                temp['real_value']=hot.real_value
                temp['predict_value']=hot.predict_value

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

        

class senTopic(APIView):    # yqdata/sentopic
    @csrf_exempt
    def get(self, request, format=None):
        userid=int(request.GET['userId'])
        json_out={}
        data=[]
        try:
            res=Sen_Topic.objects(Q(user_id=userid))
            for topic in res:
                temp={}
                temp['topicId']=topic._id
                temp['topicName']=topic.topic_name

                # print topic._id

               	kws = Cloud_formain.objects(topic_id=topic._id)
                # print len(kws)
               	kws_list = []
               	for kw in kws :
               		# tem = {}
               		# tem['frequency'] = kw.frequency
               		# tem['word'] = kw.word
                    # print kw.word
               		# kws_list.append(tem)
                    kws_list.append(kw.word)
               	temp['topicKeywords']=kws_list


                # temp['topicKeywords']=topic.topic_kws
                temp['imgs']= []
                if topic._id == 140:
                    temp['imgs'] = [
                            'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1510578676040&di=760c68bd1639c956fd8629f73456c0f5&imgtype=0&src=http%3A%2F%2Fimg.cache.cdqss.com%2Fimages%2Fattachement%2Fjpg%2Fsite2%2F20121122%2F001f3c0d6d0d1217b32d0d.jpg',
                            'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1510578755586&di=2d2e7a063ce1ccf73c89386120c6d27f&imgtype=0&src=http%3A%2F%2Ffileimage.inewsweek.cn%2Ffck_upload%2F20131018%2F13820687366473.jpg',
                            'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1510578946798&di=c9dee230f119dc94cfa2a316be883c09&imgtype=0&src=http%3A%2F%2Fimg1.cache.netease.com%2Fcatchpic%2FE%2FE0%2FE0569E9411E683F94E8B0A4CB754D75F.jpg'
                        ]
                elif topic._id == 141 :
                    temp['imgs'] = [
                            'http://www.china.com.cn/node_7000058/attachement/jpg/site1000/20171110/ac9e178530e11b6f1b0d20.jpg',
                            'http://news.xinhuanet.com/politics/2017-11/09/1121932351_15102301509901n.jpg',
                            'http://news.xinhuanet.com/politics/2017-11/09/1121932351_15102310626871n.jpg'
                        ]
                elif topic._id == 142 :
                    temp['imgs'] = [
                            'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1510579727257&di=6bb8545205b595bde16552d08dd8e3d1&imgtype=0&src=http%3A%2F%2Fimg0.utuku.china.com%2F400x0%2Feconomy%2F20170711%2F2939668c-7a2b-4c47-b3ca-09aadf6f40f4.jpg',
                            'http://yynews.cnnb.com.cn/pic/0/11/38/22/1)382283_797336.jpg'
                        ]
                elif topic._id == 143 :
                    temp['imgs'] = [
                            'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1510593392291&di=b2fe1e430973d6eb9b74ff410d033edd&imgtype=0&src=http%3A%2F%2Fimages.china.cn%2Fattachement%2Fjpg%2Fsite1000%2F20160717%2Fd02788e9b6ae18f571f82a.jpg',
                            'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1510595070647&di=3b31e7410a728faf89b2304d81237a88&imgtype=0&src=http%3A%2F%2Fwww.people.com.cn%2Fmediafile%2Fpic%2F20151126%2F26%2F17008412103535275678.jpg',
                            'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1510595130637&di=6789fc40869036887b640eca881b3f32&imgtype=0&src=http%3A%2F%2Fpicture.youth.cn%2Fqtdb%2F201710%2FW020171031115555478807.jpg'
                        ]
                elif topic._id == 144 :
                    temp['imgs'] = [
                            'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1510590676054&di=03fac7601c4954e0e5c7644621e46ba3&imgtype=0&src=http%3A%2F%2Fstc.zjol.com.cn%2Fg1%2FM00054FCggSA1jgRayARvOXAABySP1u_MQ827.jpg%3Fwidth%3D601%26height%3D358',
                            'https://timgsa.baidu.com/timg?image&quality=80&size=b10000_10000&sec=1510581606&di=cf57b48b80d489f6b3d598f8a965ee60&src=http://img.jiaodong.net/pic/news2005/20050317guoji2.jpg',
                            'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1510592042751&di=e07996417e84660429c4808c06aac55a&imgtype=0&src=http%3A%2F%2Fimages.china.cn%2Fattachement%2Fjpg%2Fsite1000%2F20130503%2F7427ea210a4d12ed55a10f.jpg'
                        ]
                elif topic._id == 145 :
                    temp['imgs'] = [
                            'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1510592234712&di=a78cdcd1254f15b5d994d086e7aeb06c&imgtype=jpg&src=http%3A%2F%2Fimg0.imgtn.bdimg.com%2Fit%2Fu%3D3110906030%2C1039306458%26fm%3D214%26gp%3D0.jpg',
                            'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1510592357726&di=63506953402ebcbb69e96b39df40841b&imgtype=0&src=http%3A%2F%2Fphotocdn.sohu.com%2F20150812%2FImg418692432.jpg',
                            'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1510592679719&di=3aa12a76b3719173c2af238c1d7e6449&imgtype=0&src=http%3A%2F%2Fwww.mm111.net%2Fuploadfile%2F2011%2F0826%2F20110826022117600.jpg'
                        ]
                # res = Tran_Wall_Post.objects(hot_topic_id=topic._id)
                # for post_res in res :
                #     if len(post_res.img_url) > 5:
                #         temp['imgs'].append(post_res.img_url)
                #     else :
                #         pass
                # try:        
                #     temp['imgs'] = random.sample(temp['imgs'],5)
                # except:
                #     pass
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

# def SenmsgOut(APIView):    # yqdata/sentopic
#     @csrf_exempt
#     def get(self, request, format=None):
#         # userid=int(request.GET['userId'])
#         json_out={}
#         data=[]
#         tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))

#         # tokens = base64.b64decode(request.META.get('HTTP_AUTHORIZATION'))
#         time_stamp = tokens[-13:-3]

#         if abs(int(time_stamp)-int(time.time())) < 60:

#             tokens = re.sub(r'#.*#.*','',tokens)
#             # tokens = json_data['userid']
#             pld = Auth.decode_auth_token(tokens)

#             user_id = pld['data']['id']
#             login_time = pld['data']['login_time']

            



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

