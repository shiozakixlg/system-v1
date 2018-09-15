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
from django.conf import settings
from Auths import Auth

from mongoengine import *
import json
from mongoengine.queryset.visitor import Q
from serializers import PostSerializer

import logging
logger = logging.getLogger('django')

connect('yuqing', alias='default', host='118.190.133.203', port=27016,username='yuqing',password='yuqing@2017')
secret = settings.SECRET_KEY

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)



class login(APIView):
    @csrf_exempt    
    def post(self, request, format=None):
        json_out = {}
        json_data = request.data
        try:
            username = json_data["user_account"]
            password = json_data["user_pwd"]
            if (not username or not password):
                msg =  '用户名和密码不可为空'
            else:
                data = Auth.authenticate(Auth,username, password)
            json_out['code'] = 0
            json_out['success'] = True
            json_out['data'] = data
        except:
            traceback.print_exc()
            json_out['code']=1
            json_out['success']=False
            json_out['data']={}
        return HttpResponse(json.dumps(json_out),content_type="application/json")