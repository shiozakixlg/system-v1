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
from yqdata.Auths import *
from django.http import HttpResponse
from bson.objectid import ObjectId
import random
import base64
from mongoengine import *
import json
import time
from mongoengine.queryset.visitor import Q
from serializers import PostSerializer
import re
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



class UserAnalysis(APIView):  # http://127.0.0.1:8081/yqdata/user_analysis/
    @csrf_exempt
    def get(self, request, format=None):
        topic_id=int(request.GET['topicId'])
        json_out={}
        data=[]
        try:

            posts =Tran_Wall_Post.objects(hot_topic_id=topic_id).only('_id', 'url', 'site_name', 'site_id', 'lan_type','content', 'pt_time', 'read_num', 'repost_num', 'poster')
            posts_new = sorted(posts, key=lambda post: int(post.poster.follows), reverse=True)
            sen_user = []
            sen_user_id = set()
            num_ten=0
            for item in posts_new:
              if num_ten == 20:
                break
              else:
                if item.poster.id not in sen_user_id:
                    sen_user.append(item)
                    sen_user_id.add(item.poster.id)
                    num_ten=num_ten+1

            posts_content = posts(Q(content__contains=u'安倍晋三') | Q(content__contains=u'反对党') | \
        Q(content__contains=u'安倍') | Q(content__contains=u'习近平') | Q(content__contains=u'特朗普') | \
        Q(content__contains=u'川普') | Q(content__contains=u'郭文贵')  | Q(content__contains=u'共产党')  | \
        Q(content__contains=u'共产主义') | Q(content__contains=u'政治') | Q(content__contains=u'首脑')| \
        Q(content__contains=u'日本') | Q(content__contains=u'总统') | Q(content__contains=u'战争') | \
        Q(content__contains=u'北韩') | Q(content__contains=u'朝鲜') | Q(content__contains=u'危机') | \
        Q(content__contains=u'反共') | Q(content__contains=u'反对共产党') | Q(content__contains=u'反对习近平') |Q(content__contains=u'宪法') | Q(content__contains=u'民进党') | \
        Q(content__contains=u'在野党') | Q(content__contains=u'参议院') | Q(content__contains=u'国情') | \
        Q(content__contains=u'众议院') | Q(content__contains=u'执政') | Q(content__contains=u'政府') | Q(content__contains=u'政变'))
            num_ten=0
            for item in posts_content:
              if num_ten == 20:
                break
              else:
                if item.poster.id not in sen_user_id:
                    sen_user.append(item)
                    sen_user_id.add(item.poster.id)
                    num_ten=num_ten+1
            
            for item in sen_user:
                post_dict = dict()
                post_dict['posts'] = []
                user = item.poster
                poster = {}
                poster['home_url'] = user.home_url 
                poster['img_url'] = user.img_url
                poster['id'] = user.id
                poster['name'] = user.name
                poster['follows'] = user.follows
                poster['following'] = user.following
                poster['post_num'] = user.post_num
                poster['level'] = user.level
                poster['location'] = user.location
                poster['birthday'] = user.birthday
                poster['site_name'] = "twitter"
                post_dict['poster'] = poster

                user_posts = posts(poster__id=user.id)
                count = 10 if len(user_posts) > 10 else len(user_posts)
                for item in user_posts[:count]:
                    post = {}
                    post['_id'] = str(item._id)
                    post['post_url'] = item.url
                    post['hot_topic_id'] = item.hot_topic_id
                    post['content'] = item.content
                    post['pt_time'] = item.pt_time
                    post['like_num'] = item.read_num
                    post['repost_num'] = item.repost_num
                    post['lan_type'] = item.lan_type
                    post['site_id'] = item.site_id
                    post['site_name'] = item.site_name
                    post_dict['posts'].append(post)
                data.append(post_dict)


            json_out['code']=0
            json_out['success']=True
            json_out['data']=data
        except:
            traceback.print_exc()
            json_out['code']=1
            json_out['success']=False
            json_out['data']={}

        return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

class attrUser(APIView):  # http://127.0.0.1:8081/yqdata/user_attr

    @csrf_exempt
    def get(self, request, format=None):
        # userid=int(request.GET['userId'])
        json_out={}
        data={}

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
                user_acc = User.objects(user_id=user_id).first()

                user_attr = {}

                data['user_id'] = user_id
                data['user_account'] = user_acc.user_account
                data['user_passwd'] = user_acc.user_passwd
                data['user_group_id'] = user_acc.user_group_id
                data['user_role_id'] = user_acc.user_role_id
                data['user_logintime'] = user_acc.user_logintime
                data['topic_kws'] = user_acc.topic_kws
                data['real_name'] = user_acc.real_name
                data['phone_num'] = user_acc.phone_num
                data['email'] = user_acc.email
                #传用户图片
                head_img_str = str(user_acc.img_url)
                head_img_path = '/var/www/yqapi/yqdata/headimg/' + head_img_str + '.txt'
                head_img = open(head_img_path,'rb').read()
                data['img_url'] = head_img

                # data['user_attr'] = user_attr


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



class showUserList(APIView):  #../yqdata/showuserlist
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
        
            try:
                data = []
                user_obj = User.objects(user_id=user_id).first()

                role_id = user_obj.user_role_id
                group_id = user_obj.user_group_id

                if role_id == 2:

                    users = User.objects(user_group_id=group_id)
                    for user in users :
                        temp = {}
                        temp['user_id'] = user.user_id
                        temp['user_account'] = user.user_account
                        temp['user_group_id'] = user.user_group_id
                        temp['user_role_id'] = user.user_role_id
                        temp['user_logintime'] = user.user_logintime
                        temp['topic_kws'] = user.topic_kws
                        temp['real_name'] = user.real_name
                        temp['phone_num'] = user.phone_num
                        temp['email'] = user.email
                        #传用户图片
                        head_img_str = str(user.img_url)
                        head_img_path = '/var/www/yqapi/yqdata/headimg/' + head_img_str + '.txt'
                        head_img = open(head_img_path,'rb').read()
                        temp['img_url'] = head_img
                        data.append(temp)

                    json_out['code']=0
                    json_out['success']=True
                    json_out['data']=data
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
                elif role_id == 0:
                    users = User.objects(user_group_id__gte=0)
                    for user in users :
                        temp = {}
                        temp['user_id'] = user.user_id
                        temp['user_account'] = user.user_account
                        temp['user_group_id'] = user.user_group_id
                        temp['user_role_id'] = user.user_role_id
                        temp['user_logintime'] = user.user_logintime
                        temp['topic_kws'] = user.topic_kws
                        temp['real_name'] = user.real_name
                        temp['phone_num'] = user.phone_num
                        temp['email'] = user.email
                        #传用户图片
                        head_img_str = str(user.img_url)
                        head_img_path = '/var/www/yqapi/yqdata/headimg/' + head_img_str + '.txt'
                        head_img = open(head_img_path,'rb').read()
                        temp['img_url'] = head_img
                        data.append(temp)

                    json_out['code']=0
                    json_out['success']=True
                    json_out['data']=data
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
                else:
                    traceback.print_exc()
                    json_out['code']=1
                    json_out['success']=False
                    json_out['data']={}
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
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

class watchAttrUser(APIView):  # http://127.0.0.1:8081/yqdata/watch_user_attr

    @csrf_exempt
    def get(self, request, format=None):
        # userid=int(request.GET['userId'])
        json_out={}
        data={}


        # tokens = base64.b64decode(request.META.get('HTTP_AUTHORIZATION'))
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:


            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)
            user_id = pld['data']['id']
            login_time = pld['data']['login_time']
            user_name = request.GET['user_name'] # 暂时

            try:
                user_acc0 = User.objects(user_id=user_id).first()
                user_role_id1 = user_acc0.user_role_id
                user_group_id1 = user_acc0.user_group_id
                user_acc = User.objects(user_account=user_name).first()
                user_group_id2 = user_acc.user_group_id 
                if user_role_id1 == 0:
                    # user_acc = User.objects(user_account=user_name).first()
                    user_attr = {}

                    data['user_id'] = user_id
                    data['user_account'] = user_acc.user_account
                    data['user_passwd'] = user_acc.user_passwd
                    data['user_group_id'] = user_acc.user_group_id
                    data['user_role_id'] = user_acc.user_role_id
                    data['user_logintime'] = user_acc.user_logintime
                    data['topic_kws'] = user_acc.topic_kws
                    data['real_name'] = user_acc.real_name
                    data['phone_num'] = user_acc.phone_num
                    data['email'] = user_acc.email
                    #传用户图片
                    head_img_str = str(user_acc.img_url)
                    head_img_path = '/var/www/yqapi/yqdata/headimg/' + head_img_str + '.txt'
                    head_img = open(head_img_path,'rb').read()
                    data['img_url'] = head_img
                    # data['user_attr'] = user_attr


                    json_out['code']=0
                    json_out['success']=True
                    json_out['data']=data
                elif user_role_id1 == 2 and user_group_id1 == user_group_id2 :
                    # user_acc = User.objects(user_account=user_name).first()
                    user_attr = {}

                    data['user_id'] = user_id
                    data['user_account'] = user_acc.user_account
                    data['user_passwd'] = user_acc.user_passwd
                    data['user_group_id'] = user_acc.user_group_id
                    data['user_role_id'] = user_acc.user_role_id
                    data['user_logintime'] = user_acc.user_logintime
                    data['topic_kws'] = user_acc.topic_kws
                    data['real_name'] = user_acc.real_name
                    data['phone_num'] = user_acc.phone_num
                    data['email'] = user_acc.email
                    #传用户图片
                    head_img_str = str(user_acc.img_url)
                    head_img_path = '/var/www/yqapi/yqdata/headimg/' + head_img_str + '.txt'
                    head_img = open(head_img_path,'rb').read()
                    data['img_url'] = head_img
                    # data['user_attr'] = user_attr


                    json_out['code']=0
                    json_out['success']=True
                    json_out['data']=data
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
                else:
                    json_out['code'] = 1
                    json_out['success'] = False
                    json_out['data'] = '权限不足'
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

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

#注册界面UI
class userSignUpUI(APIView):   # ../usersignupui
    @csrf_exempt
    def get(self, request, format=None):
        # userid=int(request.GET['userId'])
        # json_data = request.data
        json_out={}
        data={}

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
                img_base64 = 'data:image/jpg;base64,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'

                data['head_img'] = img_base64

                user_obj = User.objects(user_id=user_id).first()
                user_role_id = user_obj.user_role_id
                user_group_id = user_obj.user_group_id

                if user_role_id == 1:
                    json_out['code'] = 2
                    json_out['success'] = False
                    json_out['data'] = '无权限'
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
                elif user_role_id == 2 :
                    data['user_group_id'] = user_group_id
                else:
                    data['user_group_id'] = -1
            
                json_out['code']=0
                json_out['success']=True
                json_out['data']=data
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
            except:
                json_out['code'] = 1
                json_out['success'] = False
                json_out['data'] = '过程错误'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

        else:
            # print traceback.print_exc()
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")



# 用户注册
class userSignUp(APIView):  #../yqdata/usersignup
    @csrf_exempt
    def post(self, request, format=None):
        # userid=int(request.GET['userId'])
        json_data = request.data
        json_out={}
        data={}

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
                _id = ObjectId()
                # content_path = ObjectId()
                print json_data
                user_id_max = User.objects().order_by('-user_id').first().user_id
                user_id = user_id_max + 1 
                real_name = json_data['real_name']
                user_passwd = json_data['user_passwd']
                phone_num = json_data['phone_num']
                email = json_data['email']
                topic_kws = []
                user_role_id = json_data['user_role_id']
                user_group_id = json_data['user_group_id']
                user_account = json_data['user_account']
                # 头像之后写 img_url
                head_img = json_data['img_url']
                head_img_id = ObjectId()
                head_img_path = '/var/www/yqapi/yqdata/headimg/' + str(head_img_id) + '.txt'
                with open(head_img_path,'wb') as f :
                    f.write(head_img)



                user_obj = User(
                            _id=_id,
                            user_id=user_id,
                            user_account=user_account,
                            user_passwd=user_passwd,
                            user_logintime=time.time(),
                            user_group_id=user_group_id,
                            user_role_id=user_role_id,
                            topic_kws=topic_kws,
                            real_name=real_name,
                            phone_num=phone_num,
                            email=email,
                            img_url=head_img_id
                            )

                user_obj.save()
                json_out['code']=0
                json_out['success']=True
                json_out['data']=data
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
            except:
                print traceback.print_exc()
                json_out['code'] = 1
                json_out['success'] = False
                json_out['data'] = '过程错误'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

        else:
            # print traceback.print_exc()
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

# admin查看组信息
class groupMessage(APIView): # ../yqdata/groupmessage

    @csrf_exempt
    def get(self, request, format=None):
        # userid=int(request.GET['userId'])
        # json_data = request.data
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
                user_obj = User.objects(user_id=user_id).first()
                user_role_id = user_obj.user_role_id

                if user_role_id == 0:
                    group_objs = User_Group.objects()
                    for item in group_objs:
                        temp = {}
                        temp['group_id'] = item.group_id
                        temp['group_name'] = item.group_name
                        data.append(temp)

                    json_out['code'] = 0
                    json_out['success'] = True
                    json_out['data'] = data
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

                else:
                    print traceback.print_exc()
                    json_out['code'] = 1
                    json_out['success'] = False
                    json_out['data'] = '权限不足'
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")



            except:
                print traceback.print_exc()
                json_out['code'] = 1
                json_out['success'] = False
                json_out['data'] = '过程错误'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else:
            # print traceback.print_exc()
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")



# 修改用户信息
class modifyUserInfo(APIView):  # ../yqdata/modifyuserinfo
    @csrf_exempt
    def post(self, request, format=None):
        # userid=int(request.GET['userId'])
        json_data = request.data
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
                user_group_id = User.objects(user_id=user_id).first().user_group_id
                user_role_id = User.objects(user_id=user_id).first().user_role_id

                if user_role_id == 0 | user_role_id == 2 :
                    user_name = json_data['user_account']
                    user_obj = User.objects(user_account=user_name).first()
                    phone_num = json_data['phone_num']
                    email = json_data['email']
                    real_name = json_data['real_name']

                    user_obj.phone_num=phone_num
                    user_obj.email=email
                    user_obj.real_name=real_name
                    user_obj.save()

                    json_out['code'] = 0
                    json_out['success'] = True
                    json_out['data'] = '添加成功'
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

                else:
                    user_name = json_data['user_account']
                    user_obj = User.objects(user_account=user_name).first()
                    phone_num = json_data['phone_num']
                    email = json_data['email']
                    real_name = json_data['real_name']
                    user_passwd = json_data['user_passwd']
                    img_url = json_data['img_url']

                    img_path = str(user_obj.img_url)
                    file_path = '/var/www/yqapi/yqdata/headimg/' + img_path + '.txt'
                    with open(file_path,'wb') as f:
                        f.write(img_url)

                    user_obj.phone_num=phone_num
                    user_obj.email=email
                    user_obj.real_name=real_name
                    user_obj.user_passwd=user_passwd

                    user_obj.save()

                    json_out['code'] = 0
                    json_out['success'] = True
                    json_out['data'] = '添加成功'
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")



            except:
                print traceback.print_exc()
                json_out['code'] = 1
                json_out['success'] = False
                json_out['data'] = '过程错误'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

        else:
            # print traceback.print_exc()
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

# 删除用户
class deleteUser(APIView):
    @csrf_exempt
    def post(self, request, format=None):
        # userid=int(request.GET['userId'])
        json_data = request.data
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
                user_group_id = User.objects(user_id=user_id).first().user_group_id
                user_role_id = User.objects(user_id=user_id).first().user_role_id

                if user_role_id == 1:
                    print traceback.print_exc()
                    json_out['code'] = 1
                    json_out['success'] = False
                    json_out['data'] = '没有权限'
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

                else:
                    user_name = json_data['user_name']
                    for name_obj in user_name :
                        print name_obj
                        user_objs = User.objects(user_account=name_obj)
                        print len(user_objs)
                        for item in user_objs:
                            user_id = item.user_id

                            topic_objs = Topic.objects(user_id=user_id)
                            for each in topic_objs:
                                each.delete()
                            site_topic_objs = Site_topic.objects(user_id=user_id)
                            for each in site_topic_objs:
                                each.delete()

                            item.user_account = str(user_id)
                            item.user_passwd = ' '
                            item.user_logintime = 0
                            item.user_group_id = -1
                            item.user_role_id = -1
                            item.topic_kws = []
                            item.real_name = ' '
                            item.phone_num = ' '
                            item.email = ' '
                            content_path = item.img_url
                            content_path_str = '/var/www/yqapi/yqdata/headimg/' + str(content_path) + '.txt'
                            if os.path.exists(content_path_str):
                                os.remove(content_path_str)
                            item.save()

                    json_out['code'] = 0
                    json_out['success'] = True
                    json_out['data'] = '删除成功'
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")



            except:
                print traceback.print_exc()
                json_out['code'] = 1
                json_out['success'] = False
                json_out['data'] = '过程错误'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

        else:
            # print traceback.print_exc()
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
# 加组
class addGroup(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        # userid=int(request.GET['userId'])
        # json_data = request.data
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
                _id = ObjectId()
                # group_id = request.GET['group_id']
                group_max_id = User_Group.objects().order_by('-group_id').first().group_id
                group_id = group_max_id + 1

                group_name = request.GET['group_name']

                user_group = User_Group(
                                        _id=_id,
                                        group_id=group_id,
                                        group_name=group_name,
                                        )
                user_group.save()
                json_out['code'] = 0
                json_out['success'] = True
                json_out['data'] = '添加成功'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

            except:
                print traceback.print_exc()
                json_out['code'] = 1
                json_out['success'] = False
                json_out['data'] = '过程错误'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

        else:
            # print traceback.print_exc()
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")








