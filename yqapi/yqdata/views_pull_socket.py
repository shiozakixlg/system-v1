# -*- coding: utf-8 -*-
#https://github.com/django-json-api/django-rest-framework-json-api/blob/develop/rest_framework_json_api/views.py
#http://django-rest-framework-json-api.readthedocs.io/en/stable/getting-started.html#running-the-example-app
# http://getblimp.github.io/django-rest-framework-jwt/
from django.shortcuts import render
from dwebsocket.decorators import accept_websocket,require_websocket
from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from yqdata.models import *
from datetime import date, timedelta
import datetime
import pandas as pd
from rest_framework.views import APIView
import traceback
import base64
import time
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from yqdata.Auths import *
from django.http import HttpResponse
import random
import re
from mongoengine import *
import json
from mongoengine.queryset.visitor import Q
from serializers import PostSerializer

import logging
logger = logging.getLogger('django')
connect('yuqing', alias='default', host='118.190.133.203', port=27016,username='yuqing',password='yuqing@2017')

datatype_objs = Datatype_name.objects.only("data_type", 'datatype_name')
DTLIST = [(i.data_type, i.datatype_name) for i in datatype_objs]

topic_objs = Topic.objects.only("_id",'topic_name')
TOPICLIST= [(i._id, i.topic_name) for i in topic_objs]


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


@accept_websocket
def PullPost(request):
    if not request.is_websocket():#判断是不是websocket连接
        json_out = {}
        json_out['code'] = 1
        json_out['data'] = '非socket连接'
        json_out['success'] = False
        return HttpResponse(json.dumps(json_out, cls=MyEncoder), content_type="application/json")


    else:
        # for message in request.websocket:
        #     request.websocket.send(message)#发送消息到客户端
        while 1:
            try:
                cur = datetime.datetime.now()-datetime.timedelta(minutes=10)
                json_out = {}
                data = []
                cur = cur.strftime('%b-%d-%Y %H:%M:%S')
                print cur
                # pull_posts1 = TiebaPost.objects(Q(pt_time__gte=cur)&Q(should_pull=1))
                # pull_posts2 = Post.objects(Q(pt_time__gte=cur)&Q(should_pull=1))
                pull_posts1 = TiebaPost.objects(Q(should_pull = true))
                pull_posts2 = Post.objects(Q(should_pull = true))
                print len(pull_posts1)
                print len(pull_posts2)

                for each in pull_posts1:
                    tie = {}
                    tie['url'] = each.url
                    tie['title'] = each.title
                    tie['content'] = each.content
                    tie['poster'] = each.poster.name
                    tie['poster_img'] = each.poster.img_url
                    data.append(tie)
                for each in pull_posts2:
                    tie = {}
                    tie['url'] = each.url
                    tie['title'] = each.title
                    tie['content'] = each.content
                    tie['poster'] = each.poster.name
                    tie['poster_img'] = each.poster.img_url
                    data.append(tie)
                json_out['data'] = data
                json_out['code'] = 0
                json_out['success'] = True
                request.websocket.send(json.dumps(json_out, cls=MyEncoder))
            except:
                traceback.print_exc()
                json_out = {}
                json_out['code'] = 1
                json_out['data'] = '非socket连接'
                json_out['success'] = False
                traceback.exc_print()


            time.sleep(10)


class PullTable(APIView):  # /yqdata/pull_table

    @csrf_exempt
    def get(self, request, format=None):
        # userid=int(request.GET['userId'])
        json_out={}
        data=[]

        # tokens = base64.b64decode(request.META.get('HTTP_AUTHORIZATION'))
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)
            user_id = pld['data']['id']
            login_time = pld['data']['login_time']

            try:
                post1 = Post.objects(should_pull=1)
                post2 = TiebaPost.objects(should_pull=1)

                for each in post1:
                    tie = {}
                    tie['url'] = each.url
                    tie['title'] = each.title
                    tie['content'] = each.content
                    tie['poster'] = each.poster.name
                    tie['poster_img'] = each.poster.img_url
                    data.append(tie)

                for each in post2:
                    tie = {}
                    tie['url'] = each.url
                    tie['title'] = each.title
                    tie['content'] = each.content
                    tie['poster'] = each.poster.name
                    tie['poster_img'] = each.poster.img_url
                    data.append(tie)


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
            # print traceback.print_exc()
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")






