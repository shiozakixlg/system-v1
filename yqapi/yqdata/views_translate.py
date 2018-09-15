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
from mongoengine.queryset.visitor import Q
from serializers import PostSerializer
import base64,re
from yqdata.Auths import *
import logging
logger = logging.getLogger('django')

connect('yuqing', alias='default', host='118.190.133.203', port=27016,username='yuqing',password='yuqing@2017')


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

def decode_base64(auth_token):
    missing_padding = 4 - len(auth_token)%4
    if missing_padding:
            auth_token+=b'='*missing_padding
    tokens = base64.decodestring(auth_token)
    return tokens

class Translate(APIView):  # http://127.0.0.1:8081/yqdata/user_analysis/
    @csrf_exempt
    def get(self, request, format=None):
        post_url =request.GET['url']
        json_out ={}
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
                # with switch_collection(TwitterPost, 'tran_wall_post') as TwitterPost:
                #     posts = TwitterPost.objects(Q(topic_id=hot_topic_id)).only('url', 'pt_time', 'read_num', 'comm_num', 'img_url', 'repost_num', 'poster')


                posts=Tran_Wall_Post.objects(url=post_url).only('transText')
                json_out['code']=0
                json_out['success']=True
                json_out['data']=posts[0].transText
            except:
                traceback.print_exc()
                json_out['code']=1
                json_out['success']=False
                json_out['data']=""

            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else:
            json_out['code'] = 1
            json_out['data'] = '认证失败'
            json_out['success'] = False
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")




