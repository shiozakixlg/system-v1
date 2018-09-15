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



#
class SetTopic(APIView):  # 127.0.0.1:8000/yqdata/settopic

    @csrf_exempt
    def get(self, request, format=None):
        json_out = {}
        main_out = {}
        # user_id = int(request.GET['userId'])     #
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
                #sourcedata
                allsites_list = []
                topicData_list = []


                # allSites部分
                for dataType in range(0,6):
                    site_dict = {}
                    site_dict['siteTypeId'] = dataType
                    datatypename = Datatype_name.objects(Q(data_type=dataType))
                    for dataobj in datatypename:
                        site_dict['siteTypeName'] = dataobj.datatype_name
                        if site_dict['siteTypeName'] == u'微信类':
                            site_dict['siteTypeName'] = u'推特类'
                    detailsite_list = []

                    smallsite = Site.objects(data_type=dataType)
                    for ssite in smallsite:
                        ditailsite_dict = {}
                        ditailsite_dict['siteId'] = ssite._id
                        ditailsite_dict['siteName'] = ssite.site_name
                        if ditailsite_dict['siteName'] == u'微信公众号':
                            ditailsite_dict['siteName'] = u'推特'
                        detailsite_list.append(ditailsite_dict)
                    site_dict['detail_sites'] = detailsite_list
                    allsites_list.append(site_dict)


                # topicData
                allTopic = Topic.objects(user_id=user_id)
                for alltopic in allTopic:
                    topicdata_dict = {}
                    topic_id = alltopic._id
                    topicdata_dict['topicId'] = topic_id
                    topicdata_dict['topicName'] = alltopic.topic_name
                    #
                    # topicdata_dict['topicKeywords'] = alltopic.topic_kws
                    #
                    topicdata_dict['topicKeywords'] = alltopic.topic_kw
                    # for _list in alltopic.topic_kw :

                    #     topicdata_dict['topicKeywords'].append(_list)

                    sitelists_list = []
                    sitesets = Site_topic.objects(topic_id=topic_id)
                    for siteset in sitesets:
                        sitelists_dict = {}
                        siteid = siteset.site_id
                        sitelists_dict['siteId'] = siteid
                        nameForSite = Site.objects(_id=siteid)
                        for nameforsite in nameForSite:
                            sitelists_dict['siteName'] = nameforsite.site_name
                        sitelists_list.append(sitelists_dict)
                    topicdata_dict['siteLists'] = sitelists_list
                    topicData_list.append(topicdata_dict)

                # 
                main_out['allSites'] = allsites_list
                main_out['topicData'] = topicData_list


                #
                json_out['code'] = 0
                json_out['success'] = True
                json_out['data'] = main_out
            except:
                traceback.print_exc()
                json_out['code'] = 1
                json_out['data'] = {}
                json_out['success'] = False


            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else:
            json_out['code'] = 1
            json_out['data'] = '认证失败'
            json_out['success'] = False
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

#
class IsRepeat(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        # user_id = int(request.POST('userId'))  #
        topicname = request.POST('topicName') #
        json_out = {}


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
                topicsets = Topic.objects(Q(user_id=user_id) & Q(topic_name=topicname))
                if topicsets : 
                    json_out['code'] = 1
                    json_out['success'] = False
                    return HttpResponse(json.dumps(json_out,cls=MyEncoder),content_type="application/json")

                json_out['code'] = 0
                json_out['success'] = True
                return HttpResponse(json.dumps(json_out,cls=MyEncoder),content_type="application/json")

            except:
                json_out['code'] = 1
                json_out['success'] = False
                return HttpResponse(json.dumps(json_out,cls=MyEncoder),content_type="application/json")
        else:
            json_out['code'] = 1
            json_out['data'] = '认证失败'
            json_out['success'] = False
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

#增加话题

class addTopic(APIView):
    @csrf_exempt
    def post(self, request, format=None):
        json_data = request.data
        json_out = {}

        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        data = {}
        # tokens = base64.b64decode(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']
            try:
                # user_id = int(json_data['userId'])
                topic_name = json_data['topicName']
                #原来
                # topic_kws = json_data['topicKeywords']
                #改关键词结构

                topic_kw = json_data['topicKeywords']



                topic_kws = []
                for each in topic_kw :
                    for item in each :
                        topic_kws.append(item)



                sites = json_data['sites']

                try:
                    id_now = Topic.objects().order_by('-_id').only('_id').first()
                    #加一个userName
                    topic_id = id_now._id + 1
                except:
                    topic_id = 1

                # name_now = Topic.objects(user_name=)
                user = User.objects(user_id=user_id).first()
                user_name = user.user_account
                for item in topic_kws:
                    
                    # if item not in user.topic_kws :
                    user.topic_kws.append(item)
                user.save()


                topic_col = Topic(_id=topic_id, topic_name=topic_name, topic_kws=topic_kws, user_id=user_id, user_name=user_name,topic_kw=topic_kw)
                topic_col.save()
                len_list = len(json_data['sites'])
                site_number = 0
                while(site_number < len_list):
                    site_id = json_data['sites'][site_number]['siteId']

                    topic_site_col = Site_topic(site_id=site_id, topic_id=topic_id, topic_name=topic_name, topic_kws=topic_kws, user_id=user_id, user_name=user_name,topic_kw=topic_kw)
                    topic_site_col.save()
                    site_number += 1

                # # 判断过去3天数据中有无新增信息
                # cur = datetime.datetime.now()-datetime.timedelta(hours=12)
                # cur = cur.strftime('%b-%d-%Y %H:%M:%S')
                # posts = Post.objects(pt_time__gte=cur).first()
                # posts_tieba = TiebaPost.objects(pt_time__gte=cur).first()
                # # posts_tieba = TiebaPost.objects(pt_time__gte=cur)[:]
                # for item in posts:
                #     content = item.content
                #     for phrase in topic_kw :
                #         i = 1
                #         for word in phrase:
                #             if word not in content:
                #                 i = -1
                #                 break
                #             else:
                #                 i = 1
                #         if i == 1:
                #             break

                #     topic_id_list = item.topic_id.append(topic_id)
                #     item.update(topic_id=topic_id_list)

                # for item in posts_tieba:
                #     content = item.content
                #     for phrase in topic_kw :
                #         i = 1
                #         for word in phrase:
                #             if word not in content:
                #                 i = -1
                #                 break
                #             else:
                #                 i = 1
                #         if i == 1:
                #             break

                #     topic_id_list = item.topic_id.append(topic_id)
                #     item.update(topic_id=topic_id_list)



                data['topic_id'] = topic_id
                json_out['code'] = 0
                json_out['success'] = True
                json_out['data'] = data 
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


#修改话题
#ParseJson2，粘贴到view.py中
class modifyTopic(APIView):
    @csrf_exempt
    def post(self, request, format=None):
        json_data = request.data
        json_out = {}

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
                # user_id = int(json_data['userId'])
                topic_name = json_data['topicName']
                #修改
                topic_kw = json_data['topicKeywords']

                topic_kws = []
                for each in topic_kw :
                    for item in each :
                        topic_kws.append(item)

                sites = json_data['sites']

                topic_obj = Topic.objects(topic_name=topic_name).first()
                topic_kws_before = topic_obj.topic_kws
                topic_id = topic_obj._id

                user = User.objects(user_id=user_id).first()
                for kw in topic_kws_before :
                    if kw in user.topic_kws :
                        user.topic_kws.remove(kw)
                for kw in topic_kws:
                    # if kw not in user.topic_kws :
                    user.topic_kws.append(kw)
                user.save()
                user_name = user.user_account
                topic_obj.topic_kw = topic_kw
                topic_obj.topic_kws = topic_kws
                topic_obj.save()
                print topic_name
                print user_id
                # test_col = Site_topic.objects(Q(topic_name=topic_name)&Q(user_id=user_id)&Q(site_id=201))
                # print len(test_col)
                site_topic_col = Site_topic.objects(Q(topic_name=topic_name) & Q(user_id=user_id))
                site_topic_col.delete()

                # test2_col = Site_topic.objects(Q(topic_name=topic_name) & Q(user_id=user_id))
                # print len(test2_col)

                # test3_col = Site_topic.objects(Q(topic_id=19)&Q(user_id=user_id)&Q(site_id=201))
                # print len(test3_col)

                len_list = len(json_data['sites'])
                site_number = 0
                while(site_number < len_list):
                    site_id = request.data['sites'][site_number]['siteId']

                    topic_site_col = Site_topic(site_id=site_id, topic_id=topic_id, topic_name=topic_name, topic_kws=topic_kws, user_id=user_id, user_name=user_name,topic_kw=topic_kw)
                    topic_site_col.save()
                    site_number += 1

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


#删除话题
class DeleteTopic(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        # user_id = int(request.GET['userId']) #传入数据
        topic_id = request.GET['topicId'] #传入数据
        json_out = {}
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
                topic_col = Topic.objects(Q(user_id=user_id) & Q(_id=topic_id)).first()

                kws_list = topic_col.topic_kws
                topic_col.delete()

                user = User.objects(user_id=user_id).first()
                for kw in kws_list :
                    if kw in user.topic_kws :
                        user.topic_kws.remove(kw)
                user.save()

                site_topic_cols = Site_topic.objects(Q(user_id=user_id) & Q(topic_id=topic_id))
                for site_topic_col in site_topic_cols:
                    site_topic_col.delete()

                json_out['code'] = 0
                json_out['success'] = True
                return HttpResponse(json.dumps(json_out,cls=MyEncoder),content_type="application/json")
            except:
                json_out['code'] = 1
                json_out['success'] = False
                return HttpResponse(json.dumps(json_out,cls=MyEncoder),content_type="application/json")
        else:
            json_out['code'] = 1
            json_out['data'] = '认证失败'
            json_out['success'] = False
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

#返回站点树
class dataSourceTree(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        json_out = {}
        main_out = {}
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
                #sourcedata
                allsites_list = []
                topicData_list = []


                # allSites部分
                for dataType in range(0,6):
                    site_dict = {}
                    site_dict['siteTypeId'] = dataType
                    datatypename = Datatype_name.objects(Q(data_type=dataType))
                    for dataobj in datatypename:
                        site_dict['siteTypeName'] = dataobj.datatype_name
                        if site_dict['siteTypeName'] == u'微信类':
                            site_dict['siteTypeName'] = u'推特类'
                    detailsite_list = []

                    smallsite = Site.objects(data_type=dataType)
                    for ssite in smallsite:
                        ditailsite_dict = {}
                        ditailsite_dict['siteId'] = ssite._id
                        ditailsite_dict['siteName'] = ssite.site_name
                        if ditailsite_dict['siteName'] == u'微信公众号':
                            ditailsite_dict['siteName'] = u'推特'
                        detailsite_list.append(ditailsite_dict)
                    site_dict['detail_sites'] = detailsite_list
                    allsites_list.append(site_dict)



                # 外层data部分
                main_out['allSites'] = allsites_list


                #最最外层
                json_out['code'] = 0
                json_out['success'] = True
                json_out['data'] = main_out
            except:
                traceback.print_exc()
                json_out['code'] = 1
                json_out['data'] = {}
                json_out['success'] = False
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else:
            json_out['code'] = 1
            json_out['data'] = '认证失败'
            json_out['success'] = False
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

#小测试用类
class TestView(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        allsites_list = []
        json_out = {}

        user_id = 1
        ts = Topic.objects(user_id=user_id).order_by('-_id').only('_id').first()
        print ts._id

        return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")


#管理员管理话题
class adminManageTopic(APIView):   #../yqdata/adminmanagetopic
    @csrf_exempt
    def get(self, request, format=None):
        json_out = {}

        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))

        # tokens = base64.b64decode(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']
            data = {}
            data['topic'] = {}
            try:
                user_obj = User.objects(user_id=user_id).first()
                user_group_id = user_obj.user_group_id
                user_role_id = user_obj.user_role_id

                if user_role_id == 2 or user_role_id == 0 :
                    users = User.objects(user_group_id=user_group_id)

                    allsites_list = []
                    # allSites部分
                    for dataType in range(0,6):
                        site_dict = {}
                        site_dict['siteTypeId'] = dataType
                        datatypename = Datatype_name.objects(Q(data_type=dataType))
                        for dataobj in datatypename:
                            site_dict['siteTypeName'] = dataobj.datatype_name
                        detailsite_list = []

                        smallsite = Site.objects(data_type=dataType)
                        for ssite in smallsite:
                            ditailsite_dict = {}
                            ditailsite_dict['siteId'] = ssite._id
                            ditailsite_dict['siteName'] = ssite.site_name
                            detailsite_list.append(ditailsite_dict)
                        site_dict['detail_sites'] = detailsite_list
                        allsites_list.append(site_dict)


                    for item in users :

                        user_id_topics = Topic.objects(user_id=item.user_id)
                        this_user_name = item.user_account
                        data['topic'][this_user_name] = []
                        for alltopic in user_id_topics:
                            topicdata_dict = {}

                            topic_id = alltopic._id
                            topicdata_dict['topicId'] = topic_id
                            topicdata_dict['topicName'] = alltopic.topic_name
                            #
                            # topicdata_dict['topicKeywords'] = alltopic.topic_kws
                            topicdata_dict['user_name'] = alltopic.user_name
                            topicdata_dict['topicKeywords'] = alltopic.topic_kw
                            # for _list in alltopic.topic_kw :

                            #     topicdata_dict['topicKeywords'].append(_list)

                            sitelists_list = []
                            sitesets = Site_topic.objects(Q(topic_id=topic_id)&Q(user_name=this_user_name))
                            for siteset in sitesets:
                                sitelists_dict = {}
                                siteid = siteset.site_id
                                sitelists_dict['siteId'] = siteid
                                nameForSite = Site.objects(_id=siteid)
                                for nameforsite in nameForSite:
                                    sitelists_dict['siteName'] = nameforsite.site_name
                                sitelists_list.append(sitelists_dict)
                            topicdata_dict['siteLists'] = sitelists_list
                            data['topic'][this_user_name].append(topicdata_dict)
                    data['allSites'] = allsites_list
                    json_out['code'] = 0
                    json_out['success'] = True
                    json_out['data'] = data
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

                else:
                    json_out['code'] = 1
                    json_out['success'] = False
                    json_out['data'] = '权限不足'
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


# 批量添加话题UI
class batchSettingTopicUI(APIView): # ../yqdata/batchsetui
    @csrf_exempt
    def get(self, request, format=None):
        # json_data = request.data
        json_out = {}

        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))

        # tokens = base64.b64decode(request.META.get('HTTP_AUTHORIZATION'))
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
                user_role_id = user_obj.user_role_id
                user_group_id = user_obj.user_group_id

                if user_role_id == 0:
                    all_user = User.objects()
                    for item in all_user:
                        item_name = item.user_account
                        data.append(item_name)
                    json_out['code'] = 0
                    json_out['success'] = True
                    json_out['data'] = data
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
                elif user_role_id == 1:
                    json_out['code'] = 0
                    json_out['success'] = True
                    json_out['data'] = '普通用户权限不足'
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
                else :
                    all_user = User.objects(user_group_id=user_group_id)
                    for item in all_user:
                        item_name = item.user_account
                        data.append(item_name)
                    json_out['code'] = 0
                    json_out['success'] = True
                    json_out['data'] = data
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
            except:
                print traceback.print_exc()
                json_out['code'] = 1
                json_out['success'] = False
                json_out['data'] = '过程出错'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")



        else:
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

# 批量添加话题
class batchSettingTopic(APIView):   #../yqdata/batchsettopic
    @csrf_exempt
    def post(self, request, format=None):
        json_data = request.data
        json_out = {}

        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))

        # tokens = base64.b64decode(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']
            rec_useracc = json_data['user_name']
            print len(rec_useracc)
            try:
                user_obj = User.objects(user_id=user_id).first()
                user_role_id = user_obj.user_role_id
                user_group_id = user_obj.user_group_id

                if user_role_id == 1:
                    json_out['code'] = 0
                    json_out['success'] = True
                    json_out['data'] = '普通用户权限不足'
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

                else:
                    #得到输入的话题和需要的站点
                    topic_name = json_data['topicName']
                    topic_kw = json_data['topicKeywords']
                    sites = json_data['sites']
                    topic_kws = []
                    for each in topic_kw :
                        for item in each :
                            topic_kws.append(item)
                    #需要发送的每个用户的名字
                    for user_acc in rec_useracc:    
                        print '111111'
                        print user_acc
                        user_acc_obj = User.objects(user_account=user_acc).first()
                        user_acc_id = user_acc_obj.user_id

                        print user_acc_id
                        user_acc_topic = Topic.objects(user_id=user_acc_id)
                        if user_acc_topic:
                            user_acc_topic_list = []
                            for item in user_acc_topic:
                                user_acc_topic_list.append(item.topic_name)
                        else :
                            user_acc_topic_list = []
                        #进入修改模块
                        # print user_acc_topic_list
                        # print topic_name
                        if topic_name in user_acc_topic_list:
                            print user_acc
                            print '22222'
                            topic_obj = Topic.objects(Q(user_id=user_acc_id)&Q(topic_name=topic_name)).first()
                            topic_kws_before = topic_obj.topic_kws
                            topic_id = topic_obj._id

                            for kw in topic_kws_before:
                                if kw in user_acc_obj.topic_kws:
                                    user_acc_obj.topic_kws.remove(kw)
                            for kw in topic_kws:
                                # if kw not in user_acc_obj.topic_kws:
                                user_acc_obj.topic_kws.append(kw)

                            user_acc_obj.save()

                            topic_obj.topic_kw = topic_kw
                            topic_obj.topic_kws = topic_kws
                            topic_obj.save()

                            site_topic_col = Site_topic.objects(Q(topic_name=topic_name)&Q(user_id=user_acc_id))
                            site_topic_col.delete()
                            len_list = len(json_data['sites'])
                            site_number = 0
                            while(site_number < len_list):
                                site_id = request.data['sites'][site_number]['siteId']

                                topic_site_col = Site_topic(site_id=site_id,topic_id=topic_id,topic_name=topic_name,topic_kws=topic_kws,user_id=user_acc_id,user_name=user_acc,topic_kw=topic_kw)
                                topic_site_col.save()
                                site_number += 1

                            # continue

                        #进入添加话题模块
                        else:
                            try:
                                print user_acc
                                print '3333'
                                id_now = Topic.objects().order_by('-_id').only('_id').first()
                                topic_id = id_now._id + 1
                            except:
                                topic_id = 1

                            for item in topic_kws:
                                # if item not in user_acc_obj.topic_kws:
                                user_acc_obj.topic_kws.append(item)
                            user_acc_obj.save()

                            topic_col = Topic(_id=topic_id, topic_name=topic_name, topic_kws=topic_kws, user_id=user_acc_id, user_name=user_acc,topic_kw=topic_kw)
                            topic_col.save()
                            len_list = len(json_data['sites'])
                            site_number = 0
                            while(site_number < len_list):
                                site_id = json_data['sites'][site_number]['siteId']

                                topic_site_col = Site_topic(site_id=site_id, topic_id=topic_id, topic_name=topic_name, topic_kws=topic_kws, user_id=user_acc_id, user_name=user_acc,topic_kw=topic_kw)
                                topic_site_col.save()
                                site_number += 1

                    json_out['code'] = 0
                    json_out['success'] = True
                    json_out['data'] = '修改成功'
                    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
            except:
                print traceback.print_exc()
                json_out['code'] = 1
                json_out['success'] = False
                json_out['data'] = '过程出错'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

        else:
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")




# 删除他人话题
class deleteTopicOther(APIView):  # ../yqdata/deletetopicother 
    @csrf_exempt
    def get(self, request, format=None):
        json_out = {}
        # json_data = request.data
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))

        # tokens = base64.b64decode(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]
        user_acc = request.GET['user_name']
        topic_id = request.GET['topicId']
        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']

            try :

                # user_acc = json_data['user_name']
                # topic_id = json_data['topic_id']

                topic_col = Topic.objects(Q(user_name=user_acc)&Q(_id=topic_id)).first()
                kws_list = topic_col.topic_kws
                topic_col.delete()

                user = User.objects(user_account=user_acc).first()
                for kw in kws_list :
                    if kw in user.topic_kws :
                        user.topic_kws.remove(kw)
                user.save()

                site_topic_cols = Site_topic.objects(Q(user_name=user_acc) & Q(topic_id=topic_id))
                for site_topic_col in site_topic_cols:
                    site_topic_col.delete()

                json_out['code'] = 0
                json_out['success'] = True
                json_out['data'] = '删除成功'
                return HttpResponse(json.dumps(json_out,cls=MyEncoder),content_type="application/json")

            except:
                print traceback.print_exc()
                json_out['code'] = 1
                json_out['success'] = False
                json_out['data'] = '过程出错'
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

        else:
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")















