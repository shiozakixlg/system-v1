# -*-coding:utf-8 -*-

#https://github.com/django-json-api/django-rest-framework-json-api/blob/develop/rest_framework_json_api/views.py
#http://django-rest-framework-json-api.readthedocs.io/en/stable/getting-started.html#running-the-example-app
# http://getblimp.github.io/django-rest-framework-jwt/

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from yqdata.models import *
from datetime import datetime, timedelta, date
import pandas as pd
from rest_framework.views import APIView
import traceback
import datetime
import random
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
import base64,re
from yqdata.Auths import *
from django.http import HttpResponse
import random
from bson.objectid import ObjectId
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


class Hot_Value_Evolution(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        json_out={}
        data=[]
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        topic_id = int(request.GET['s_id']) - 4
        event_id = int(request.GET['ev_id']) 


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

                objs = Event_Hot_Value.objects(Q(topic_id=topic_id)&Q(event_id=event_id))
                for obj in objs:
                    tmp = {}
                    date = obj.date
                    famous_num = obj.famous_num
                    post_num = obj.post_num
                    hot_value = obj.hot_value

                    str_date =  date.strftime('%Y/%m/%d')

                    tmp['time'] = str_date
                    tmp['da_v'] = famous_num
                    tmp['tiezi'] = post_num
                    tmp['redu'] = hot_value

                    data.append(tmp)

                json_out['data'] = data
                json_out['success'] = True
                json_out['code'] = 0
            except:
                traceback.print_exc()
                json_out['code']=1
                json_out['success']=False
                json_out['data']={}

            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

class Hot_Topic_Evolution(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        json_out={}
        data=[]
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        topic_id = int(request.GET['s_id']) - 4
        event_id = int(request.GET['ev_id']) 
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

                objs = Event_Topic_Evo.objects(Q(topic_id=topic_id)&Q(event_id=event_id))
                for obj in objs:
                    tmp = {}
                    date = obj.date
                    topic = obj.topic_kw
                    num = obj.kw_volumn
                    types = obj.type_id

                    str_date =  date.strftime('%Y/%m/%d')

                    tmp['time'] = str_date
                    tmp['topic'] = topic
                    tmp['num'] = num
                    tmp['type'] = types

                    data.append(tmp)

                json_out['data'] = data
                json_out['success'] = True
                json_out['code'] = 0
            except:
                traceback.print_exc()
                json_out['code']=1
                json_out['success']=False
                json_out['data']={}
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

class Event_Detail(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        json_out={}
        data=[]
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        topic_id = int(request.GET['s_id']) 
        event_id = int(request.GET['ev_id'])
        if topic_id == 0:
            topic_id = 2
        else:
            topic_id -= 4

        # event_id = response.GET['ev_id']
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
                str_time = '2017-01-01'

                if topic_id == 0 and event_id == 0:
                    start_time = '2018-03-01'
                    end_time = '2018-04-16'
                elif topic_id == 0 and event_id == 1:
                    start_time = '2018-04-16'
                    end_time = '2018-07-06'
                elif topic_id == 0 and event_id == 2:
                    start_time = '2018-07-06'
                    end_time = '2018-12-24'
                elif topic_id == 1 and event_id == 0:
                    start_time = '2018-07-15'
                    end_time = '2018-08-16'
                elif topic_id == 1 and event_id == 1:
                    start_time = '2018-08-16'
                    end_time = '2018-12-24'

                start_time = datetime.datetime.strptime(start_time,'%Y-%m-%d')
                end_time = datetime.datetime.strptime(end_time,'%Y-%m-%d')


                format_time = datetime.datetime.strptime(str_time,'%Y-%m-%d')
                objs = Known_Post.objects(Q(topic_id=topic_id)&Q(pt_time__gte=start_time)&Q(pt_time__lte=end_time))
                for obj in objs:
                    tmp = {}
                    
                    post_url = obj.url
                    site_name = obj.site_name
                    video_url = ''
                    title = obj.title
                    try:
                    	poster = obj.poster.name
                    except:
                    	poster = ''
                    
                    good_num = obj.read_num
                    try:
                    	poster_url = obj.poster.home_url
                    except:
                    	poster_url = ''
                    repost_num = obj.repost_num
                    content = obj.content
                    comm_num = obj.comm_num
                    pt_time = obj.pt_time
                    try:
                    	user_id = obj.poster.id
                    except:
                    	user_id = ''
                    try:

                    	img_url = obj.poster.img_url
                    except:
                    	img_url = ''
                    _id = obj._id   

                    str_date =  pt_time.strftime('%Y-%m-%d %H:%M:%S')

                    data_type = obj.data_type
                    if data_type == 0:
                        site_name = '新闻站点'
                    elif data_type == 1:
                        site_name = '论坛'
                    elif data_type == 2:
                        if site_name == 'Twitter':
                            site_name = '推特'
                        else:
                            site_name = '新浪微博'
                    elif data_type == 3:
                        site_name = '百度贴吧'
                    elif data_type == 5:
                        site_name = '全网搜索'


                    tmp['post_url'] = post_url
                    tmp['site_name'] = site_name
                    tmp['video_url'] = video_url
                    tmp['title'] = title
                    tmp['poster'] = poster
                    tmp['good_num'] = good_num
                    tmp['poster_url'] = poster_url
                    tmp['repost_num'] = repost_num
                    tmp['content'] = content
                    tmp['comm_num'] = comm_num
                    tmp['pt_time'] = str_date
                    tmp['user_id'] = user_id
                    tmp['img_url'] = img_url
                    tmp['id'] = str(_id)

                    data.append(tmp)

                json_out['data'] = data
                json_out['success'] = True
                json_out['code'] = 0
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

class Community_Detection(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        json_out={}
        data={}
        data['group1'] = []
        data['group2'] = []
        data['group3'] = []

        
        # data['group11'] = []
        # data['group21'] = []
        # data['group31'] = []
        data['user'] = []
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        topic_id = int(request.GET['s_id']) - 4
        event_id = int(request.GET['ev_id']) 
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
            
            dt00 = []
            dt01 = []
            dt02 = []
            dt10 = []
            dt11 = []
            u3 = []

            try:
                n = 1
                objs = Known_Poster.objects()
                for obj in objs:
                    tmp = {}
                    user_id = obj._id
                    user_name = obj.name
                    home_url = obj.home_url
                    Follows = obj.follows
                    Following = obj.following
                    post_num = obj.post_num
                    location = obj.location
                    intro = obj.abstract
                    board = "新浪微博"
                    user_type = obj.level
                    img_url = obj.img_url

                    tmp['user_id'] = user_id
                    tmp['user_name'] = user_name
                    tmp['home_url'] = home_url
                    tmp['Follows'] = Follows
                    tmp['Following'] = Following
                    tmp['post_nums'] = post_num
                    tmp['location'] = location
                    tmp['intro'] = intro
                    tmp['board'] = board
                    tmp['user_type'] = user_type
                    tmp['user_img'] = img_url
                    if obj.level != "3":
                        if n <= 800:
                            if n % 3 == 0:
                                dt00.append(tmp)
                            elif n % 3 == 1:
                                dt01.append(tmp)
                            elif n % 3 == 2:
                                dt02.append(tmp)                
                        elif n > 800:
                            if n % 2 == 0:
                                dt10.append(tmp)
                            elif n % 2 == 1:
                                dt11.append(tmp)                          

                    if obj.level == "2":
                        data['user'].append(tmp)
                    if obj.level == "3":
                        u3.append(tmp)

                    n += 1

                if topic_id == 0 :
                    if event_id == 0:
                        r = 1
                        for dt in dt00:
                            if r % 3 == 1:
                                data['group1'].append(dt)
                            elif r % 3 == 2:
                                data['group2'].append(dt)
                            elif r % 3 == 0:
                                data['group3'].append(dt)
                            r += 1
                    elif event_id == 1:
                        r = 1
                        for dt in dt01:
                            if r % 3 == 1:
                                data['group1'].append(dt)
                            elif r % 3 == 2:
                                data['group2'].append(dt)
                            elif r % 3 == 0:
                                data['group3'].append(dt)
                            r += 1
                    elif event_id == 2:
                        r = 1
                        for dt in dt02:
                            if r % 3 == 1:
                                data['group1'].append(dt)
                            elif r % 3 == 2:
                                data['group2'].append(dt)
                            elif r % 3 == 0:
                                data['group3'].append(dt)
                            r += 1
                elif topic_id == 1 :
                    if event_id == 0:
                        r = 1
                        for dt in dt10:
                            if r % 3 == 1:
                                data['group1'].append(dt)
                            elif r % 3 == 2:
                                data['group2'].append(dt)
                            elif r % 3 == 0:
                                data['group3'].append(dt)
                            r += 1
                    elif event_id == 1:
                        r = 1
                        for dt in dt11:
                            if r % 3 == 1:
                                data['group1'].append(dt)
                            elif r % 3 == 2:
                                data['group2'].append(dt)
                            elif r % 3 == 0:
                                data['group3'].append(dt)
                            r += 1
                for user3 in u3:
                	data['group2'].append(user3)

                random.shuffle(data['group2'])

                json_out['data'] = data
                json_out['success'] = True
                json_out['code'] = 0
            except:
                traceback.print_exc()
                json_out['code']=1
                json_out['success']=False
                json_out['data']={}

            return HttpResponse(json.dumps(json_out, cls=MyEncoder,sort_keys=True),content_type="application/json")

class Opinion_Mining(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        json_out={}
        data=[]
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        topic_id = int(request.GET['s_id']) - 4
        event_id = int(request.GET['ev_id']) 
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

                objs = Point_Mining.objects(Q(topic_id=topic_id)&Q(event_id=event_id))
                for obj in objs:
                    tmp = {}
                    viewpoint = obj.viewpoint
                    usercomment = []
                    for usct in obj.usercomment:                      
                        usercomment.append(usct)                                                     

                    tmp['viewpoint'] = viewpoint
                    tmp['usercomment'] = usercomment                

                    data.append(tmp)            

                json_out['data'] = data
                json_out['success'] = True
                json_out['code'] = 0
            except:
                traceback.print_exc()
                json_out['code']=1
                json_out['success']=False
                json_out['data']={}

            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

class Emotion_Analysis(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        json_out={}
        data=[]
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        topic_id = int(request.GET['s_id']) - 4
        event_id = int(request.GET['ev_id']) 
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
                n = 0
                objs = Emotion_Mining.objects(Q(topic_id=topic_id)&Q(event_id=event_id))
                for obj in objs:
                    tmp = {}
                    num = n
                    post_url = obj.post_url
                    site_name = obj.site_name
                    title = obj.title
                    content = obj.content
                    pt_time = obj.pt_time
                    good_num = obj.good_num
                    comm_num = obj.comm_num
                    img_url = obj.img_url
                    repost_num = obj.repost_num
                    poster_url = obj.poster_url
                    poster = obj.poster
                    user_id = obj.user_id
                    video_url = obj.video_url
                    label = obj.label

                    tmp['id'] = num
                    tmp['post_url'] = post_url
                    tmp['site_name'] = site_name
                    tmp['title'] = title
                    tmp['content'] = content
                    tmp['pt_time'] = pt_time
                    tmp['good_num'] = good_num
                    tmp['comm_num'] = comm_num
                    tmp['img_url'] = img_url
                    tmp['repost_num'] = repost_num
                    tmp['poster_url'] = poster_url
                    tmp['poster'] = poster
                    tmp['user_id'] = user_id
                    tmp['video_url'] = video_url
                    tmp['label'] = label

                    n = n + 1

                    data.append(tmp)

                json_out['data'] = data
                json_out['success'] = True
                json_out['code'] = 0
            except:
                traceback.print_exc()
                json_out['code']=1
                json_out['success']=False
                json_out['data']={}

            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

class Score_Save(APIView):#?id=0%time=2018-8-15%result=80%fin=false%expert=待评价
    @csrf_exempt
    def post(self, request, format=None):
        json_data = request.data
        json_out={}
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
                # _id = ObjectId()
                if len(Save_Score.objects(Q(event_id=json_data['id'])&Q(time=json_data['time'])))!= 0:
                    for obj in Save_Score.objects(Q(event_id=json_data['id'])&Q(time=json_data['time'])):                     
                        obj.event_id = json_data['id']
                        obj.time = json_data['time']
                        obj.result = json_data['result']
                        if json_data['fin'] == "false":
                            obj.fin = False
                            obj.expert = -1
                            obj.consistent = -1
                        else:
                            obj.fin = True
                            obj.expert = json_data['expert']
                            if obj.result > obj.expert:
                                x = float(obj.expert)/obj.result
                                obj.consistent = float('%.2f' % x)
                            else:
                                x = float(obj.result)/obj.expert
                                obj.consistent = float('%.2f' % x)
                        obj.save()
                else:
                    event_id = json_data['id']
                    tm = json_data['time']
                    result = json_data['result']
                    if json_data['fin'] == "false":
                        fin = False
                        expert = -1
                        consistent = -1
                    else:
                        fin = True                
                        expert = json_data['expert']
                        if result > expert:
                            y = float(expert)/result
                            consistent = float('%.2f' % y)
                        else:
                            y = float(result)/expert
                            consistent = float('%.2f' % y)

                    save_score = Save_Score(
                        _id = ObjectId(),
                        event_id = event_id,
                        time = tm,
                        result = result,
                        fin = fin,
                        expert = expert,
                        consistent = consistent
                        )

                    save_score.save()
               
                json_out['success'] = True
                json_out['code'] = 0
            except:
                traceback.print_exc()
                json_out['code']=1
                json_out['success']=False
                

            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

class Score_Search(APIView):#?id=0%time=2018-8-15%result=80%fin=false%expert=待评价
    @csrf_exempt
    def get(self, request, format=None):
        json_out={}
        data=[]
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
                event_id = request.GET['id']           
                for obj in Save_Score.objects(Q(event_id=event_id)):
                    tmp = {}
                    tm = obj.time
                    result = obj.result                                                               
                  
                    if obj.fin == True:
                        fin = "true"
                        expert = obj.expert
                        consistent = obj.consistent
                    elif obj.fin == False:
                        fin = "false"
                        expert = "待评价"
                        consistent = ""

                    tmp['time'] = tm
                    tmp['result'] = result                
                    tmp['fin'] = fin 
                    tmp['expert'] = expert
                    tmp['consistent'] = consistent

                    data.append(tmp)            

                json_out['data'] = data
                json_out['success'] = True
                json_out['code'] = 0
            except:
                traceback.print_exc()
                json_out['code']=1
                json_out['success']=False
                json_out['data']={}

            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
class Strategy_Save(APIView):#?id=0%time=2018-8-15%strategy=文本
    @csrf_exempt
    def post(self, request, format=None):
        json_data = request.data
        json_out={}
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
                if len(Save_Strategy.objects(Q(event_id=json_data['id'])&Q(time=json_data['time']))) != 0:
                    for obj in Save_Strategy.objects(Q(event_id=json_data['id'])&Q(time=json_data['time'])):                        
                        obj.event_id = json_data['id']
                        obj.time = json_data['time']
                        obj.strategy1 = json_data['strategy1']                        
                        obj.strategy2 = json_data['strategy2']

                        obj.save()
                else:
                    event_id = json_data['id']
                    tm = json_data['time']
                    strategy1 = json_data['strategy1']
                    strategy2 = json_data['strategy2']

                    save_strategy = Save_Strategy(
                        event_id = event_id,
                        time = tm,
                        strategy1 = strategy1,
                        strategy2 = strategy2
                        )

                    save_strategy.save()

                json_out['success'] = True
                json_out['code'] = 0
            except:
                traceback.print_exc()
                json_out['code']=1
                json_out['success']=False
                

            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
class Strategy_Search(APIView):#?id=0%time=2018-8-15%result=80%fin=false%expert=待评价
    @csrf_exempt
    def get(self, request, format=None):
        json_out={}
        data=[]
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
                event_id = request.GET['id']         
                tm = request.GET['time']
                for obj in Save_Strategy.objects(Q(event_id=event_id)&Q(time=tm)):
                    tmp = {}                    
                    strategy1 = obj.strategy1
                    strategy2 = obj.strategy2

                    tmp['time'] = tm
                    tmp['strategy1'] = strategy1
                    tmp['strategy2'] = strategy2

                    data.append(tmp)            

                json_out['data'] = data
                json_out['success'] = True
                json_out['code'] = 0
            except:
                traceback.print_exc()
                json_out['code']=1
                json_out['success']=False
                json_out['data']={}

            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")