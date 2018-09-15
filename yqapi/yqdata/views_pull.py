# -*- coding: utf-8 -*-
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

class PullPost(APIView):  #/yqdata/pullpost
    @csrf_exempt
    def get(self, request, format=None):

        json_out = {}


        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))

        # tokens = base64.b64decode(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]
        data = []
        # if abs(int(time_stamp)-int(time.time())) < 60:
        if 1:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']

            
            
            try:
                cur = datetime.datetime.now()-datetime.timedelta(minutes=5)

                cur = cur.strftime('%b-%d-%Y %H:%M:%S')
                pull_posts = TiebaPost.objects(Q(pt_time__gte=cur)&Q(should_pull=1))

                for each in pull_posts:
                    post = {}

                    post['title'] = each.title
                    post['content'] = each.content
                    data.append(post)

                json_out['data'] = data
                json_out['code'] = 0
                json_out['success'] = True
                return HttpResponse(json.dumps(json_out,cls=MyEncoder),content_type="application/json")

            except:
                traceback.print_exc()
                json_out['code'] = 1
                json_out['success'] = False
                return HttpResponse(json.dumps(json_out,cls=MyEncoder),content_type="application/json")
        else:
            json_out['code'] = 1
            json_out['data'] = '认证失败'
            json_out['success'] = False
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")





