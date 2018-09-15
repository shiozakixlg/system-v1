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
from bson.objectid import ObjectId
from django.http import HttpResponse
import random
import time
import re
from mongoengine import *
import json
import base64
from mongoengine.queryset.visitor import Q
from serializers import PostSerializer
from yqdata.Auths import *
import os
import logging
logger = logging.getLogger('django')

connect('yuqing', alias='default', host='118.190.133.203', port=27016,username='yuqing',password='yuqing@2017')

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



class userMessageSendUI(APIView):  #../yqdata/sendusermsgui
    @csrf_exempt
    def get(self, request, format=None):
        json_out={}
        # tokens = base64.b64decode(request.META.get('HTTP_AUTHORIZATION'))
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']
            data = []
            try:
                user_obj = User.objects(user_id=user_id).first()
                user_group_id = user_obj.user_group_id
                user_role_id = user_obj.user_role_id
                user_name = user_obj.user_account

                if user_role_id == 0 :

                    send_user_objs = User.objects(Q(user_role_id__ne=0))
                    for send_user_obj in send_user_objs :

                        temp = {}
                        # temp['user_id'] = send_user_obj.user_id
                        temp['user_'] = send_user_obj.user_account
                        data.append(temp)

                elif user_role_id == 1:

                    send_user_objs = User.objects(Q(user_group_id=user_group_id)&Q(user_account__ne=user_name))
                    for send_user_obj in send_user_objs :

                        temp = {}
                        # temp['user_id'] = send_user_obj.user_id
                        temp['user_'] = send_user_obj.user_account
                        data.append(temp)
                    temp = {}
                    temp['user_'] = 'admin'
                    data.append(temp)

                else:

                    send_user_objs = User.objects(Q(user_role_id=1)&Q(user_group_id=user_group_id))
                    for send_user_obj in send_user_objs :

                        temp = {}
                        # temp['user_id'] = send_user_obj.user_id
                        temp['user_'] = send_user_obj.user_account
                        data.append(temp)
                    temp = {}
                    temp['user_'] = 'admin'
                    data.append(temp)



                json_out['code'] = 0
                json_out['success'] = True
                json_out['data'] = data
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")


            except:
                print traceback.print_exc()
                json_out['code'] = 1
                json_out['success'] = False
                json_out['data'] = '添加失败！'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else:
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")



class userMessageSend(APIView):     #.../yqdata/sendUserMsg

    @csrf_exempt
    def post(self, request, format=None):
        json_out={}
        json_data=request.data


        # tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            send_userid = pld['data']['id']
            login_time = pld['data']['login_time']
            
            try :

                
                # send_userid = json_data['send_userid']
                rec_useracc = json_data['rec_username']
                title = json_data['title']
                content = json_data['content']
                cur_time = datetime.datetime.now()
                try:
                    desc = json_data['desc']
                except:
                    desc = ' '
                is_read = 0
                group_id = User.objects(user_id=send_userid).first().user_group_id
                send_useracc = User.objects(user_id=send_userid).first().user_account
                send_user_role = User.objects(user_id=send_userid).first().user_role_id
                if send_user_role == 0:
                    send_user_role = 3
                for item in rec_useracc:
                    rec_userid = User.objects(user_account=item).first().user_id
                    obj_id = ObjectId()
                    content_path = ObjectId()
                    msg_obj = Message(
                                _id=obj_id,
                                send_user_id=send_userid,
                                rec_user_id=rec_userid,
                                title=title,
                                # content=content,
                                send_time=cur_time,
                                is_read=is_read,
                                group_id=group_id,
                                send_user_acc=send_useracc,
                                send_user_role=send_user_role,
                                rec_user_acc=item,
                                desc=desc,
                                content_path=content_path
                                )
                    content_path_str = '/var/www/yqapi/yqdata/messagefile/' + str(content_path) + '.txt'
                    with open(content_path_str,'wb') as f :
                        f.write(content)


                    msg_obj.save()

                json_out['code'] = 0
                json_out['success'] = True
                json_out['data'] = '添加成功！'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
            except:
                print traceback.print_exc()
                json_out['code'] = 1
                json_out['success'] = False
                json_out['data'] = '添加失败！'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else :
            # print traceback.print_exc()
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

# is read
class isRead(APIView):   #../yqdata/isread
    @csrf_exempt
    def get(self, request, format=None):
        # tokens = request.GET['tokens'] #暂定
        # pld = Auth.decode_auth_token(tokens)

        # user_id = pld['data']['id']
        # login_time = pld['data']['login_time']
        msg_id = request.GET['id']
        json_out = {}

        a = ObjectId(msg_id)
        # tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']
            
            try :
                try:
                    user_info = User.objects(user_id=user_id).first()
                    msg_obj = Message.objects(_id=a).first()

                    if msg_obj.is_read == 0 :

                        msg_obj.is_read = 1
                        msg_obj.read_time = datetime.datetime.now()
                        msg_obj.save()
                        json_out['code'] = 0
                        json_out['success'] = True
                        json_out['data'] = '添加成功！'
                        return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
                    else:
                        json_out['code'] = 0
                        json_out['success'] = False
                        json_out['data'] = '重复操作'
                        return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
                except:
                    json_out['code'] = 1
                    json_out['success'] = False
                    json_out['data'] = '找不到用户'
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

            except:
                print traceback.print_exc()
                json_out['code'] = 1
                json_out['success'] = False
                json_out['data'] = '添加失败！'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else :
            # print traceback.print_exc()
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")



#push msg
class pushMsg(APIView):  #  ../yqdata/pushmsg
    @csrf_exempt
    def get(self, request, format=None):

        # tokens = request.GET['tokens'] #暂定
        # pld = Auth.decode_auth_token(tokens)

        # user_id = pld['data']['id']
        # login_time = pld['data']['login_time']
        json_out = {}
        data = []
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = tokens[:-35]
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            print pld

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']

            try:
                try:
                    user_info = User.objects(user_id=user_id).first()

                    msg_objs = Message.objects(rec_user_id=user_id)
                    for msg_obj in msg_objs:
                        obj_dic = {}
                        obj_dic['group_id'] = msg_obj.group_id
                        obj_dic['send_user_id'] = msg_obj.send_user_id
                        obj_dic['send_user_acc'] = msg_obj.send_user_acc
                        obj_dic['send_user_role'] = msg_obj.send_user_role
                        obj_dic['title'] = msg_obj.title

                        content_path = str(msg_obj.content_path)
                        content_path_str = '/var/www/yqapi/yqdata/messagefile/' + content_path + '.txt'
                        content = open(content_path_str,'rb').read()
                        obj_dic['content'] = content
                        # obj_dic['content'] = msg_obj.content
                        obj_dic['send_time'] = msg_obj.send_time
                        obj_dic['desc'] = msg_obj.desc
                        obj_dic['_id'] = str(msg_obj._id)
                        obj_dic['is_read'] = msg_obj.is_read
                        try:
                            obj_dic['read_time'] = msg_obj.read_time
                        except:
                            obj_dic['read_time'] = ' '

                        data.append(obj_dic)

                    json_out['code'] = 0
                    json_out['success'] = True
                    json_out['data'] = data
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
                except:
                    print traceback.print_exc()
                    json_out['code'] = 1
                    json_out['success'] = False
                    json_out['data'] = '无消息'
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
            except:
                print traceback.print_exc()
                json_out['code'] = 1
                json_out['success'] = False
                json_out['data'] = '调取失败'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else:
            # print traceback.print_exc()
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

#shan tie 
class delUserMsg(APIView):  #../yqdata/delusermsg
    @csrf_exempt
    def post(self, request, format=None):

        json_out = {}
        json_data = request.data

        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)
            try:
                user_id = pld['data']['id']
                login_time = pld['data']['login_time']
                try:
                    id_list = json_data['_id']

                    for msg_id in id_list:

                        a = ObjectId(msg_id)

                        post_obj = Message.objects(_id=a).first()
                        content_path = post_obj.content_path
                        content_path_str = '/var/www/yqapi/yqdata/messagefile/' + str(content_path) + '.txt'
                        if os.path.exists(content_path_str):
                            os.remove(content_path_str)
                            
                        # content_path = post_obj.


                        post_obj.delete()

                        json_out['code'] = 0
                        json_out['success'] = True
                        json_out['data'] = '删除成功'
                        return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
                except:
                    print traceback.print_exc()
                    json_out['code'] = 1
                    json_out['success'] = False
                    json_out['data'] = '删除失败'
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
            except:
                print traceback.print_exc()
                json_out['code'] = 1
                json_out['success'] = False
                json_out['data'] = '删除失败'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else:
            # print traceback.print_exc()
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")


class showMsgDetail(APIView):  #   ../yqdata/showmsgdetail  
    @csrf_exempt
    def get(self, request, format=None):

        json_out = {}
        _id = request.GET['_id']
        
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']
            try:
                a = ObjectId(_id)

                msg_obj = Message.objects(_id=a).first()
                data = {}
                
                data['group_id'] = msg_obj.group_id
                data['send_user_id'] = msg_obj.send_user_id
                data['send_user_acc'] = msg_obj.send_user_acc
                data['send_user_role'] = msg_obj.send_user_role
                data['title'] = msg_obj.title

                content_path = str(msg_obj.content_path)
                content_path_str = '/var/www/yqapi/yqdata/messagefile/' + content_path + '.txt'
                content = open(content_path_str,'rb').read()
                data['content'] = content

                # data['content'] = msg_obj.content
                data['send_time'] = msg_obj.send_time
                data['desc'] = msg_obj.desc
                data['_id'] = str(msg_obj._id)
                data['is_read'] = True

                msg_obj.is_read = True
                msg_obj.save()

                json_out['code'] = 0
                json_out['success'] = True
                json_out['data'] = data
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
            except:
                print traceback.print_exc()
                json_out['code'] = 1
                json_out['success'] = False
                json_out['data'] = '操作错误'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else:
            # print traceback.print_exc()
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")


#未读集合
class notReadList(APIView):  # ../yqdata/notreadlist
    @csrf_exempt
    def get(self, request, format=None):

        json_out = {}
        
        
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']
            data = []
            try:
                message_unread_list = Message.objects(Q(rec_user_id=user_id)&Q(is_read=False))
                for msg_obj in message_unread_list:
                    temp = {}
                    temp['group_id'] = msg_obj.group_id
                    temp['send_user_id'] = msg_obj.send_user_id
                    temp['send_user_acc'] = msg_obj.send_user_acc
                    temp['send_user_role'] = msg_obj.send_user_role
                    temp['title'] = msg_obj.title
                    
                    temp['send_time'] = msg_obj.send_time
                    temp['desc'] = msg_obj.desc
                    temp['_id'] = str(msg_obj._id)
                    data.append(temp)

                json_out['code'] = 0
                json_out['success'] = True
                json_out['data'] = data
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
            except:
                json_out['code'] = 1
                json_out['success'] = False
                json_out['data'] = '操作错误'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

        else:
            # print traceback.print_exc()
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")


#返回未读数字
class unReadNum(APIView):  #../yqdata/unreadnum 
    @csrf_exempt
    def get(self, request, format=None):
        
        json_out = {}
        
        
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']
            data = {}

            try:
                message_unread_list = Message.objects(Q(rec_user_id=user_id)&Q(is_read=False))

                data['unread_num'] = len(message_unread_list)
                json_out['code'] = 0
                json_out['success'] = True
                json_out['data'] = data
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
            except:
                print traceback.print_exc()
                json_out['code'] = 1
                json_out['success'] = False
                json_out['data'] = '操作错误'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

        else:
            # print traceback.print_exc()
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")




