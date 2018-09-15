# -*-coding:utf-8 -*-

#https://github.com/django-json-api/django-rest-framework-json-api/blob/develop/rest_framework_json_api/views.py
#http://django-rest-framework-json-api.readthedocs.io/en/stable/getting-started.html#running-the-example-app

from yqdata.models import Post, Topic, Site_topic, TiebaPost
from serializers import PostSerializer
from rest_framework.views import APIView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from mongoengine import *
from mongoengine.queryset.visitor import Q

import json
import traceback

import logging
logger = logging.getLogger('django')

import time
from datetime import date
import datetime

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from bson.objectid import ObjectId
import re

import base64,re
from yqdata.Auths import *
connect('yuqing', alias='default', host='118.190.133.203', port=27016,username='yuqing',password='yuqing@2017')
# topic_objs = Topic.objects.only("_id",'topic_name')
# TOPICLIST= [(i._id, i.topic_name) for i in topic_objs]
# TOPICDICT= {i._id:i.topic_name for i in topic_objs}
# TOPICDICT[-1] = "全部"

def decode_base64(auth_token):
    missing_padding = 4 - len(auth_token)%4
    if missing_padding:
            auth_token+=b'='*missing_padding
    tokens = base64.decodestring(auth_token)
    return tokens

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


def PostDict(post_dict, post):
    post_dict['_id'] = str(post._id)
    post_dict['url'] = post.url
    post_dict['site_id'] = post.site_id
    post_dict['site_name'] = post.site_name
    post_dict['topic_id'] = post.topic_id
    post_dict['board'] = post.board
    post_dict['data_type'] = post.data_type
    post_dict['title'] = post.title
    post_content = post.content.strip()
    if post.data_type == 2:
        post_content= re.sub(r'n{2,}t{2,}|t{1,}n{1,}t{1,}|n{1,}t{2,}n{1,}|t{3,}|n{3,}', '', post_content)
    post_content = post_content.decode('utf-8')
    if len(post_content) > 50:
        post_dict['content'] = post_content[:50].encode('utf-8') + '...'
    else:
        post_dict['content'] = post_content.encode('utf-8')
    post_dict['pt_time'] = post.pt_time
    post_dict['st_time'] = post.st_time
    post_dict['read_num'] = post.read_num
    post_dict['comm_num'] = post.comm_num
    post_dict['img_url'] = post.img_url
    post_dict['repost_num'] = post.repost_num
    post_dict['lan_type'] = post.lan_type
    post_dict['is_read'] = post.is_read
    post_dict['repost_pt_id'] = post.repost_pt_id
    post_dict['text_type'] = post.text_type
    if post.poster != None:
        poster = {}
    poster['home_url'] = post.poster.home_url
    poster['img_url'] = post.poster.img_url
    poster['id'] = post.poster.id
    poster['name'] = post.poster.name
    post_dict['poster'] = poster




class RealtimeMonitorAll(APIView):

    @csrf_exempt
    def get(self, request, format=None):
        json_out = {}

        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:
            tokens = re.sub(r'#.*#.*','',tokens)
            print tokens
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)
            # print pld
            userid = pld['data']['id']
            login_time = pld['data']['login_time']
            # userid = 0
            try:
                pageCount = int(request.GET['pageCount'])
                post_time = datetime.datetime.strptime(request.GET['date'], "%Y-%m-%d")
                data_list = []
                # 返回全部数据?
                # date=2016-12-30&pageCount=20&siteId=-1&dataType=-1
                if request.GET['siteId'] == u'-1' and request.GET['dataType'] == u'-1':
                    print "#####################"
                    self.get_posts(pageCount, userid,post_time, data_list, 1)

                # 返回具体站点    
                # date=2016-12-30&pageCount=20&siteId=301&dataType=-1
                elif request.GET['siteId'] != u'-1':
                    print "******************"
                    self.get_posts(pageCount, userid,post_time, data_list, 2, siteId=int(request.GET['siteId']))
                    
                # 返回不同dataType
                # date=2016-12-30&pageCount=20&siteId=-1&dataType=2
                else:
                    print "^^^^^^^^^^^^^^^^^^^^"
                    self.get_posts(pageCount, userid,post_time, data_list, 3, dataType=int(request.GET['dataType']))

                json_out['data'] = data_list
                json_out['code'] = 0
                json_out['success'] = True
                json.dumps(json_out, cls=MyEncoder)
            except:
                traceback.print_exc()
                json_out['code'] = 1
                json_out['data'] = []
                json_out['success'] = False

            return HttpResponse(json.dumps(json_out, cls=MyEncoder), content_type="application/json")
        else:
            json_out['code'] = 1
            json_out['data'] = {}
            json_out['success'] = False

            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")



    def get_posts(self, pageCount, userid,post_time, data_list, flag, **kwargs):
        value = [kwargs[key] for key in kwargs]
        value = value[0] if len(value) > 0 else value

        # posts = Post.objects(Q(user_id_list=userid))
        # 
        print post_time

        # posts = Post.objects(Q(pt_time__gte=post_time) & \
                    # Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max)) & Q(user_id_list=userid) )
        now=datetime.datetime.now()
        if flag == 2:
            if str(value).startswith('3'):
                now=datetime.datetime.now()
                site_topic = Site_topic.objects(Q(site_id=value) & Q(user_id=userid)).only('topic_id','topic_name')
                for id_name in site_topic:
                    t_post_dict = {}
                    post_list = []
                    topicId = id_name.topic_id
                    t_post_dict['topicId'] = topicId
                    t_post_dict['topicName'] = id_name.topic_name
                    posts_len = TiebaPost.objects(Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max.replace(now.hour,now.minute,now.second,now.microsecond))) & Q(user_id_list=userid)& Q(topic_id=topicId) & Q(site_id=value)).count()
                    page_Count = posts_len if posts_len < pageCount else pageCount
                    if page_Count != 0:
                        posts_ = TiebaPost.objects(Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max.replace(now.hour,now.minute,now.second,now.microsecond))) & Q(user_id_list=userid)& Q(topic_id=topicId) & Q(site_id=value)).order_by('-pt_time')[:pageCount]
                        t_post_dict['newTime'] = posts_[0].pt_time
                        t_post_dict['oldTime'] = posts_[page_Count-1].pt_time
                        for post in posts_:
                            post_dict = {}
                            PostDict(post_dict, post)
                            post_list.append(post_dict)
                            # post_list.append(PostSerializer(post).data)   # 序列化费?
                        t_post_dict['postData'] = post_list
                    else:
                        t_post_dict['newTime'] = post_time
                        t_post_dict['oldTime'] = post_time
                        t_post_dict['postData'] = []
                    data_list.append(t_post_dict)


                posts_len = TiebaPost.objects(Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max.replace(now.hour,now.minute,now.second,now.microsecond))) & Q(user_id_list=userid) & Q(site_id=value)).count()
                t_post_dict = {}
                post_list = []
                t_post_dict['topicId'] = -1
                t_post_dict['topicName'] = '全部'


                page_Count = posts_len if posts_len < pageCount else pageCount
                if page_Count != 0:
                    posts_ = TiebaPost.objects(Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max.replace(now.hour,now.minute,now.second,now.microsecond))) & Q(user_id_list=userid) & Q(site_id=value)).order_by('-pt_time')[:pageCount]
                    t_post_dict['newTime'] = posts_[0].pt_time
                    t_post_dict['oldTime'] = posts_[page_Count-1].pt_time
                    for post in posts_:
                        post_dict = {}
                        PostDict(post_dict, post)
                        post_list.append(post_dict)
                        # post_list.append(PostSerializer(post).data)   # 序列化费?
                    t_post_dict['postData'] = post_list
                else:
                    t_post_dict['newTime'] = post_time
                    t_post_dict['oldTime'] = post_time
                    t_post_dict['postData'] = []
                data_list.append(t_post_dict)

            else:
                site_topic = Site_topic.objects(Q(site_id=value) & Q(user_id=userid)).only('topic_id','topic_name')
                for id_name in site_topic:
                    t_post_dict = {}
                    post_list = []
                    topicId = id_name.topic_id
                    t_post_dict['topicId'] = topicId
                    t_post_dict['topicName'] = id_name.topic_name
                    posts_len = Post.objects(Q(user_id_list=userid) & Q(topic_id=topicId) & Q(site_id=value) & Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max.replace(now.hour,now.minute,now.second,now.microsecond)))).count()

                    page_Count = posts_len if posts_len < pageCount else pageCount
                    if page_Count != 0:
                        posts_ = Post.objects(Q(user_id_list=userid) & Q(topic_id=topicId) & Q(site_id=value) & Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max.replace(now.hour,now.minute,now.second,now.microsecond)))).order_by('-pt_time')[:page_Count]
                        t_post_dict['newTime'] = posts_[0].pt_time
                        t_post_dict['oldTime'] = posts_[page_Count-1].pt_time
                        for post in posts_:
                            if post.img_url == '1':
                                continue
                            post_dict = {}
                            PostDict(post_dict, post)
                            post_list.append(post_dict)
                            # post_list.append(PostSerializer(post).data)   # 序列化费?
                        t_post_dict['postData'] = post_list
                    else:
                        t_post_dict['newTime'] = post_time
                        t_post_dict['oldTime'] = post_time
                        t_post_dict['postData'] = []
                    data_list.append(t_post_dict)


                posts_len = Post.objects(Q(user_id_list=userid) & Q(site_id=value) & Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max.replace(now.hour,now.minute,now.second,now.microsecond)))).count()
                t_post_dict = {}
                post_list = []
                t_post_dict['topicId'] = -1
                t_post_dict['topicName'] = '全部'


                page_Count = posts_len if posts_len < pageCount else pageCount
                if page_Count != 0:
                    posts_ = Post.objects(Q(user_id_list=userid) & Q(site_id=value) & Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max.replace(now.hour,now.minute,now.second,now.microsecond)))).order_by('-pt_time')[:pageCount]
                    t_post_dict['newTime'] = posts_[0].pt_time
                    t_post_dict['oldTime'] = posts_[page_Count-1].pt_time
                    for post in posts_:
                        if post.img_url == '1':
                            continue
                        post_dict = {}
                        PostDict(post_dict, post)
                        post_list.append(post_dict)
                        # post_list.append(PostSerializer(post).data)   # 序列化费?
                    t_post_dict['postData'] = post_list
                else:
                    t_post_dict['newTime'] = post_time
                    t_post_dict['oldTime'] = post_time
                    t_post_dict['postData'] = []
                data_list.append(t_post_dict)


        else:
            topic_objs = Topic.objects(Q(user_id=userid)).only("_id",'topic_name')
            TOPICDICT= {i._id:i.topic_name for i in topic_objs}
            TOPICDICT[-1] = "全部"
            print TOPICDICT
            now=datetime.datetime.now();
    
            for topicId in TOPICDICT:
                t_post_dict = {}
                t_post_dict['topicId'] = topicId
                t_post_dict['topicName'] = TOPICDICT[topicId]
                post_list = []
                if flag == 1:
                    posts_ = Post.objects(Q(user_id_list=userid) & Q(topic_id=topicId) & Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max.replace(now.hour,now.minute,now.second,now.microsecond)))).order_by('-pt_time')[:pageCount] if topicId != -1 else Post.objects(Q(user_id_list=userid) & Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max.replace(now.hour,now.minute,now.second,now.microsecond)))).order_by('-pt_time')[:pageCount]
                else:
                    posts_ = Post.objects(Q(user_id_list=userid) & Q(topic_id=topicId) &Q(data_type=value) & Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max.replace(now.hour,now.minute,now.second,now.microsecond)))).order_by('-pt_time')[:pageCount]  if topicId != -1 else Post.objects(Q(user_id_list=userid) &Q(data_type=value) & Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max.replace(now.hour,now.minute,now.second,now.microsecond)))).order_by('-pt_time')[:pageCount]
                posts_len = len(posts_)
                print 'posts_len: ' + str(posts_len)
                page_Count = posts_len if posts_len < pageCount else pageCount
                if page_Count != 0:
                    # posts_ = posts_[:page_Count]
                    t_post_dict['newTime'] = posts_[0].pt_time
                    t_post_dict['oldTime'] = posts_[page_Count-1].pt_time
                    for post in posts_:
                        if post.img_url == '1':
                            continue
                        post_dict = {}
                        PostDict(post_dict, post)
                        post_list.append(post_dict)
                        # post_list.append(PostSerializer(post).data)   # 序列化费?
                    t_post_dict['postData'] = post_list
                else:
                    t_post_dict['newTime'] = post_time
                    t_post_dict['oldTime'] = post_time
                    t_post_dict['postData'] = []
                data_list.append(t_post_dict)

class RealtimeMonitorGroup(APIView):

    @csrf_exempt
    def get(self, request, format=None):
        json_out = {}

        try:
            pageCount = int(request.GET['pageCount'])
            post_time = datetime.datetime.strptime(request.GET['date'], "%Y-%m-%d")
            userstr = request.GET['userlist']
            data_list = []
            # 返回全部数据溿
            # date=2016-12-30&pageCount=20&siteId=-1&dataType=-1
            user_list=[]
            if userstr.find(',') == -1:
                user_list.append(userstr)
            else:
                user_list=userstr.split(',')

            if request.GET['siteId'] == u'-1' and request.GET['dataType'] == u'-1':
                print "#####################"
                for user in user_list:
                    userid=User.objects(Q(user_account=user)).only('user_id').first().user_id
                    self.get_posts(pageCount, user,userid,post_time, data_list, 1)

            # 返回具体站点    
            # date=2016-12-30&pageCount=20&siteId=301&dataType=-1
            elif request.GET['siteId'] != u'-1':
                print "******************"
                siteId=int(request.GET['siteId'])
                for user in user_list:
                    userid=User.objects(Q(user_account=user)).first().user_id
                    self.get_posts(pageCount, user,userid,post_time, data_list, 2, siteId)

            # 返回不同dataType
            # date=2016-12-30&pageCount=20&siteId=-1&dataType=2
            else:
                print "^^^^^^^^^^^^^^^^^^^^"
                dataType=int(request.GET['dataType'])
                for user in user_list:
                    userid=User.objects(Q(user_account=user)).first().user_id
                    self.get_posts(pageCount, user,userid,post_time, data_list, 3, dataType)

            json_out['data'] = data_list
            json_out['code'] = 0
            json_out['success'] = True
            json.dumps(json_out, cls=MyEncoder)
        except:
            traceback.print_exc()
            json_out['code'] = 1
            json_out['data'] = []
            json_out['success'] = False

        return HttpResponse(json.dumps(json_out, cls=MyEncoder), content_type="application/json")



    def get_posts(self, pageCount, user,userid,post_time, data_list, flag, **kwargs):
        value = [kwargs[key] for key in kwargs]
        value = value[0] if len(value) > 0 else value

        posts= Post.objects(Q(pt_time__gte=post_time) & \
                    Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max)) & Q(user_id_list=userid) )


        if flag == 2:
            if str(value).startswith('3'):
                tieba_posts = TiebaPost.objects(Q(pt_time__gte=post_time) & Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max)) & Q(user_id_list=userid))
                site_topic = Site_topic.objects(Q(site_id=value) & Q(user_id=userid)).only('topic_id','topic_name')
                for id_name in site_topic:
                    t_post_dict = {}
                    post_list = []
                    topicId = id_name.topic_id
                    t_post_dict['topicId'] = topicId
                    t_post_dict['topicName'] = id_name.topic_name
                    posts_ = tieba_posts(topic_id=topicId, site_id=value)
                    posts_len = len(posts_)
                    page_Count = posts_len if posts_len < pageCount else pageCount
                    if page_Count != 0:
                        posts_ = posts_[:page_Count]
                        t_post_dict['newTime'] = posts_[0].pt_time
                        t_post_dict['oldTime'] = posts_[page_Count-1].pt_time
                        for post in posts_:
                            if post.img_url == '1':
                                continue
                            post_dict = {}
                            PostDict(post_dict, post)
                            post_list.append(post_dict)
                            # post_list.append(PostSerializer(post).data)   # 序列化费旿
                        t_post_dict['postData'] = post_list
                        t_post_dict['username'] = user
                        t_post_dict['userid'] = userid
                    else:
                        t_post_dict['newTime'] = post_time
                        t_post_dict['oldTime'] = post_time
                        t_post_dict['postData'] = []
                        t_post_dict['username'] = user
                        t_post_dict['userid'] = userid
                    data_list.append(t_post_dict)


                posts_ = posts(site_id=value)
                t_post_dict = {}
                post_list = []
                t_post_dict['topicId'] = -1
                t_post_dict['topicName'] = '全部'
                posts_len = len(posts_)
                page_Count = posts_len if posts_len < pageCount else pageCount
                if page_Count != 0:
                    posts_ = posts_[:page_Count]
                    t_post_dict['newTime'] = posts_[0].pt_time
                    t_post_dict['oldTime'] = posts_[page_Count-1].pt_time
                    for post in posts_:
                        if post.img_url == '1':
                            continue
                        post_dict = {}
                        PostDict(post_dict, post)
                        post_list.append(post_dict)
                        # post_list.append(PostSerializer(post).data)   # 序列化费旿
                    t_post_dict['postData'] = post_list
                    t_post_dict['username'] = user
                    t_post_dict['userid'] = userid
                else:
                    t_post_dict['newTime'] = post_time
                    t_post_dict['oldTime'] = post_time
                    t_post_dict['postData'] = []
                    t_post_dict['username'] = user
                    t_post_dict['userid'] = userid
                data_list.append(t_post_dict)

            else:
                site_topic = Site_topic.objects(Q(site_id=value) & Q(user_id=userid)).only('topic_id','topic_name')
                for id_name in site_topic:
                    t_post_dict = {}
                    post_list = []
                    topicId = id_name.topic_id
                    t_post_dict['topicId'] = topicId
                    t_post_dict['topicName'] = id_name.topic_name
                    posts_ = posts(topic_id=topicId, site_id=value)
                    posts_len = len(posts_)
                    page_Count = posts_len if posts_len < pageCount else pageCount
                    if page_Count != 0:
                        posts_ = posts_[:page_Count]
                        t_post_dict['newTime'] = posts_[0].pt_time
                        t_post_dict['oldTime'] = posts_[page_Count-1].pt_time
                        for post in posts_:
                            if post.img_url == '1':
                                continue
                            post_dict = {}
                            PostDict(post_dict, post)
                            post_list.append(post_dict)
                            # post_list.append(PostSerializer(post).data)   # 序列化费旿
                        t_post_dict['postData'] = post_list
                        t_post_dict['username'] = user
                        t_post_dict['userid'] = userid
                    else:
                        t_post_dict['newTime'] = post_time
                        t_post_dict['oldTime'] = post_time
                        t_post_dict['postData'] = []
                        t_post_dict['username'] = user
                        t_post_dict['userid'] = userid
                    data_list.append(t_post_dict)


                posts_ = posts(site_id=value)
                t_post_dict = {}
                post_list = []
                t_post_dict['topicId'] = -1
                t_post_dict['topicName'] = '全部'
                posts_len = len(posts_)
                page_Count = posts_len if posts_len < pageCount else pageCount
                if page_Count != 0:
                    posts_ = posts_[:page_Count]
                    t_post_dict['newTime'] = posts_[0].pt_time
                    t_post_dict['oldTime'] = posts_[page_Count-1].pt_time
                    for post in posts_:
                        if post.img_url == '1':
                            continue
                        post_dict = {}
                        PostDict(post_dict, post)
                        post_list.append(post_dict)
                        # post_list.append(PostSerializer(post).data)   # 序列化费旿
                    t_post_dict['postData'] = post_list
                    t_post_dict['username'] = user
                    t_post_dict['userid'] = userid
                else:
                    t_post_dict['newTime'] = post_time
                    t_post_dict['oldTime'] = post_time
                    t_post_dict['postData'] = []
                    t_post_dict['username'] = user
                    t_post_dict['userid'] = userid
                data_list.append(t_post_dict)


        else:
            topic_objs = Topic.objects(Q(user_id=userid)).only("_id",'topic_name')
            TOPICDICT= {i._id:i.topic_name for i in topic_objs}
            TOPICDICT[-1] = "全部"
            print TOPICDICT
    
            for topicId in TOPICDICT:
                t_post_dict = {}
                t_post_dict['topicId'] = topicId
                t_post_dict['topicName'] = TOPICDICT[topicId]
                post_list = []
                if flag == 1:
                    posts_ = posts(topic_id=topicId) if topicId != -1 else posts
                else:
                    posts_ = posts(topic_id=topicId, data_type=value) if topicId != -1 else posts(data_type=value)
                posts_len = len(posts_)
                page_Count = posts_len if posts_len < pageCount else pageCount
                if page_Count != 0:
                    posts_ = posts_[:page_Count]
                    t_post_dict['newTime'] = posts_[0].pt_time
                    t_post_dict['oldTime'] = posts_[page_Count-1].pt_time
                    for post in posts_:
                        if post.img_url == '1':
                            continue
                        post_dict = {}
                        PostDict(post_dict, post)
                        post_list.append(post_dict)
                        # post_list.append(PostSerializer(post).data)   # 序列化费旿
                    t_post_dict['postData'] = post_list
                    t_post_dict['username'] = user
                    t_post_dict['userid'] = userid
                else:
                    t_post_dict['newTime'] = post_time
                    t_post_dict['oldTime'] = post_time
                    t_post_dict['postData'] = []
                    t_post_dict['username'] = user
                    t_post_dict['userid'] = userid
                data_list.append(t_post_dict)



#gai成post, 增加刷新的条?
class RealtimeMonitorFlush(APIView):
    @csrf_exempt
    def post(self, request, format=None):
        json_out = {}
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]
        if abs(int(time_stamp)-int(time.time())) < 60:
            tokens = re.sub(r'#.*#.*','',tokens)
            pld = Auth.decode_auth_token(tokens)
            userid = pld['data']['id']
            login_time = pld['data']['login_time']
            try:
                # post 方法
                params = request.data
                topicLists = params['topicLists']
                date_time = datetime.datetime.strptime(params['date'], "%Y-%m-%d")
                siteId = int(params['siteId'])
                dataType = int(params['dataType'])

                data_list = []
                # 全部数据?
                if siteId == -1 and dataType == -1:
                    self.get_posts(topicLists, userid,data_list, date_time, 1)

                # 具体站点  
                elif siteId != -1:
                    self.get_posts(topicLists, userid,data_list, date_time, 2, siteId=siteId)
                    
                # 返回不同dataType
                else:
                    self.get_posts(topicLists, userid,data_list, date_time, 3, dataType=dataType)

                json_out['data'] = data_list
                json_out['code'] = 0
                json_out['success'] = True
            except:
                traceback.print_exc()
                json_out['code'] = 1
                json_out['data'] = []
                json_out['success'] = False

            return HttpResponse(json.dumps(json_out, cls=MyEncoder), content_type="application/json")
        else:
            json_out['code'] = 1
            json_out['data'] = {}
            json_out['success'] = False

            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")



    def get_posts(self, topicLists, userid,data_list, date_time, flag, **kwargs):
        value = [kwargs[key] for key in kwargs]
        value = value[0] if len(value) > 0 else value

        if flag ==2 and str(value).startswith('3'):
            posts_day = TiebaPost.objects(Q(pt_time__gt=date_time) & \
                        Q(pt_time__lte=datetime.datetime.combine(date_time, datetime.time.max)) & Q(user_id_list=userid))

            for topic in topicLists:
                t_post_dict = {}
                topicId = topic['topicId']
                t_post_dict['topicId'] = topicId
                t_post_dict['topicName'] = "全部" if topicId == -1 else Topic.objects(_id=topicId)[0].topic_name
                logger.info(t_post_dict['topicId'])
                logger.info(t_post_dict['topicName'])
                newTime = datetime.datetime.strptime(topic['newTime'], "%Y-%m-%d %H:%M:%S")
                
                posts = posts_day(Q(pt_time__gt=newTime))

                post_list = []
                if flag == 1:
                    posts_ = posts(topic_id=topicId) if topicId != -1 else posts
                elif flag == 2:
                    posts_ = posts(topic_id=topicId, site_id=value) if topicId != -1 else posts(site_id=value)
                else:
                    posts_ = posts(topic_id=topicId, data_type=value) if topicId != -1 else posts(data_type=value)
                count = posts_.count()
                t_post_dict['count'] = count
                time1 = time.time()
                if count > 0:
                    t_post_dict['newTime'] = posts_[0].pt_time
                    for post in posts_:
                        if post.img_url == '1':
                            continue
                        post_dict = {}
                        PostDict(post_dict, post)
                        post_list.append(post_dict)
                        # post_list.append(PostSerializer(post).data)
                    t_post_dict['postData'] = post_list
                    logger.info(time.time()-time1)
                else:
                    t_post_dict['newTime'] = newTime
                    t_post_dict['postData'] = []
                data_list.append(t_post_dict)

        else:
            posts_day = Post.objects(Q(pt_time__gt=date_time) & \
                        Q(pt_time__lte=datetime.datetime.combine(date_time, datetime.time.max)) & Q(user_id_list=userid))

            for topic in topicLists:
                t_post_dict = {}
                topicId = topic['topicId']
                t_post_dict['topicId'] = topicId
                t_post_dict['topicName'] = "全部" if topicId == -1 else Topic.objects(_id=topicId)[0].topic_name
                logger.info(t_post_dict['topicId'])
                logger.info(t_post_dict['topicName'])
                newTime = datetime.datetime.strptime(topic['newTime'], "%Y-%m-%d %H:%M:%S")
                
                posts = posts_day(Q(pt_time__gt=newTime))

                post_list = []
                if flag == 1:
                    posts_ = posts(topic_id=topicId) if topicId != -1 else posts
                elif flag == 2:
                    posts_ = posts(topic_id=topicId, site_id=value) if topicId != -1 else posts(site_id=value)
                else:
                    posts_ = posts(topic_id=topicId, data_type=value) if topicId != -1 else posts(data_type=value)
                count = posts_.count()
                t_post_dict['count'] = count
                time1 = time.time()
                if count > 0:
                    t_post_dict['newTime'] = posts_[0].pt_time
                    for post in posts_:
                        if post.img_url == '1':
                            continue
                        post_dict = {}
                        PostDict(post_dict, post)
                        post_list.append(post_dict)
                        # post_list.append(PostSerializer(post).data)
                    t_post_dict['postData'] = post_list
                    logger.info(time.time()-time1)
                else:
                    t_post_dict['newTime'] = newTime
                    t_post_dict['postData'] = []
                data_list.append(t_post_dict)


class RealtimeMonitorLoad(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        json_out = {}

        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:
            tokens = re.sub(r'#.*#.*','',tokens)
            pld = Auth.decode_auth_token(tokens)
            userid = pld['data']['id']
            login_time = pld['data']['login_time']
            try:
                pageCount = int(request.GET['pageCount'])
                oldTime = datetime.datetime.strptime(request.GET['oldTime'], "%Y-%m-%d %H:%M:%S")
                topicId = int(request.GET['topicId'])
                data_list = []
                # 全部数据?
                if request.GET['siteId'] == u'-1' and request.GET['dataType'] == u'-1':
                    self.get_posts(pageCount, userid,topicId, oldTime, data_list, 1)

                # 具体站点  
                elif request.GET['siteId'] != u'-1':
                    self.get_posts(pageCount, userid,topicId, oldTime, data_list, 2, siteId=int(request.GET['siteId']))
                    
                # 返回不同dataType
                else:
                    self.get_posts(pageCount, userid,topicId, oldTime, data_list, 3, dataType=int(request.GET['dataType']))

                json_out['data'] = data_list
                json_out['code'] = 0
                json_out['success'] = True

            except:
                traceback.print_exc()
                json_out['code'] = 1
                json_out['data'] = []
                json_out['success'] = False

            return HttpResponse(json.dumps(json_out, cls=MyEncoder), content_type="application/json")
        else:
            json_out['code'] = 1
            json_out['data'] = {}
            json_out['success'] = False

            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")


    def get_posts(self, pageCount, userid,topicId, oldTime, data_list, flag, **kwargs):
        value = [kwargs[key] for key in kwargs]
        value = value[0] if len(value) > 0 else value

        if flag ==2 and str(value).startswith('3'):

            t_post_dict = {}
            t_post_dict['topicId'] = topicId
            t_post_dict['topicName'] = "全部" if topicId == -1 else Topic.objects(_id=topicId)[0].topic_name

            if flag == 1:
                posts_ = TiebaPost.objects(Q(pt_time__lt=oldTime) & Q(user_id_list=userid) & Q(topic_id=topicId)).order_by('-pt_time')[:pageCount] if topicId != -1 else TiebaPost.objects(Q(pt_time__lt=oldTime) & Q(user_id_list=userid)).order_by('-pt_time')[:pageCount]
            elif flag == 2:
                posts_ = TiebaPost.objects(Q(pt_time__lt=oldTime) & Q(user_id_list=userid) & Q(topic_id=topicId) & Q(site_id=value)).order_by('-pt_time')[:pageCount] if topicId != -1 else TiebaPost.objects(Q(pt_time__lt=oldTime) & Q(user_id_list=userid) & Q(site_id=value)).order_by('-pt_time')[:pageCount]
            else:
                posts_ = TiebaPost.objects(Q(pt_time__lt=oldTime) & Q(user_id_list=userid) & Q(topic_id=topicId) & Q(data_type=value)).order_by('-pt_time')[:pageCount] if topicId != -1 else TiebaPost.objects(Q(pt_time__lt=oldTime) & Q(user_id_list=userid) & Q(data_type=value)).order_by('-pt_time')[:pageCount]

            posts_len = len(posts_)
            page_Count = posts_len if posts_len < pageCount else pageCount
            post_list = []
            if page_Count != 0:
                t_post_dict['oldTime'] = posts_[page_Count-1].pt_time
                for post in posts_:
                    post_dict = {}
                    PostDict(post_dict, post)
                    post_list.append(post_dict)
                    # post_list.append(PostSerializer(post).data)
                t_post_dict['postData'] = post_list
            else:
                t_post_dict['oldTime'] = oldTime  
                t_post_dict['postData'] = []
            data_list.append(t_post_dict)

        else: 

            t_post_dict = {}
            t_post_dict['topicId'] = topicId
            t_post_dict['topicName'] = "全部" if topicId == -1 else Topic.objects(_id=topicId)[0].topic_name

            if flag == 1:
                posts_ = Post.objects(Q(pt_time__lt=oldTime) & Q(user_id_list=userid) & Q(topic_id=topicId)).order_by('-pt_time')[:pageCount] if topicId != -1 else Post.objects(Q(pt_time__lt=oldTime) & Q(user_id_list=userid)).order_by('-pt_time')[:pageCount]
            elif flag == 2:
                posts_ = Post.objects(Q(pt_time__lt=oldTime) & Q(user_id_list=userid) & Q(topic_id=topicId) & Q(site_id=value)).order_by('-pt_time')[:pageCount] if topicId != -1 else Post.objects(Q(pt_time__lt=oldTime) & Q(user_id_list=userid) & Q(site_id=value)).order_by('-pt_time')[:pageCount]
            else:
                posts_ = Post.objects(Q(pt_time__lt=oldTime) & Q(user_id_list=userid) & Q(topic_id=topicId) & Q(data_type=value)).order_by('-pt_time')[:pageCount] if topicId != -1 else Post.objects(Q(pt_time__lt=oldTime) & Q(user_id_list=userid) & Q(data_type=value)).order_by('-pt_time')[:pageCount]

            posts_len = len(posts_)
            page_Count = posts_len if posts_len < pageCount else pageCount
            post_list = []
            if page_Count != 0:
                t_post_dict['oldTime'] = posts_[page_Count-1].pt_time
                for post in posts_:
                    if post.img_url == '1':
                        continue
                    post_dict = {}
                    PostDict(post_dict, post)
                    post_list.append(post_dict)
                    # post_list.append(PostSerializer(post).data)
                t_post_dict['postData'] = post_list
            else:
                t_post_dict['oldTime'] = oldTime  
                t_post_dict['postData'] = []
            data_list.append(t_post_dict)



class RealtimeMonitorIsRead(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        json_out = {}
        try:
            postId = request.GET['postId']
            post_id = ObjectId(postId)
            posts = Post.objects(_id=post_id).first()
            logger.info(posts)
            # posts.is_read = 1
            # posts.save()
            post_dict = {}
            PostDict(post_dict, posts)
            json_out['data'] = post_dict
            json_out['code'] = 0
            json_out['success'] = True
        except:
            json_out['code'] = 1
            json_out['success'] = False
        return HttpResponse(json.dumps(json_out, cls=MyEncoder), content_type="application/json")
