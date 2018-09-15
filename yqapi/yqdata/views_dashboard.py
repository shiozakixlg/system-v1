# -*-coding:utf-8 -*-

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from yqdata.models import Poster, Post, Topic, Site_topic, Site, Datatype_name, Cloud_formain
from datetime import date, timedelta
import datetime
import pandas as pd
import traceback
from django.http import HttpResponse
import random
from rest_framework.views import APIView
from mongoengine import *
import json
from mongoengine.queryset.visitor import Q

import logging
logger = logging.getLogger('django')
import base64,re
from yqdata.Auths import *
import re

connect('yuqing', alias='default', host='10.31.243.108', port=27016, username='yuqing', password='yuqing@2017')
datatype_objs = Datatype_name.objects.only("data_type", 'datatype_name')
DTLIST = [(i.data_type, i.datatype_name) for i in datatype_objs]

topic_objs = Topic.objects.only("_id",'topic_name')
TOPICLIST= [(i._id, i.topic_name) for i in topic_objs]

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S') 
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')     
        else:
            return json.JSONEncoder.default(self, obj)
def decode_base64(auth_token):
    print auth_token
    print len(auth_token)
    missing_padding = 4 - len(auth_token)%4
    if missing_padding:
            auth_token+=b'='*missing_padding
    tokens = base64.decodestring(auth_token)
    return tokens
@csrf_exempt
def post_by_siteId(request):
    if request.method == 'GET':
        json_out = {}
        try:
            data = {}
            site_id = int(request.GET['siteid'])
            p_num = len(Post.objects.all())

            post_list = []
            for post in Post.objects.all():
                p_detail = {}
                p_detail['url']  = post.url
                p_detail['site_name'] = post.site_name
                p_detail['topic_id'] = post.topic_id
                p_detail['board'] = post.board
                p_detail['title'] = post.title
                p_detail['content'] = post.content
                p_detail['pt_time'] = post.pt_time
                p_detail['st_time'] = post.st_time
                p_detail['read_num'] = post.read_num
                p_detail['comm_num'] = post.comm_num
                p_detail['img_url'] = post.img_url
                p_detail['repost_num'] = post.repost_num
                p_detail['lan_type'] = post.lan_type
                p_detail['is_read'] = post.is_read
                #p_detail['html'] = post.html.read()
                post_list.append(p_detail)
        
            data['site_id'] = site_id
            data['post_num'] = p_num
            data['data'] = post_list
            json_out['content'] = data
            json_out['return'] = 1
        except:
            traceback.print_exc()
            json_out['return'] = 0

        return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
@csrf_exempt
def realtime_monitor_new(request):
    if request.method == "GET":
        site_id = int(request.GET['siteId'])
        data_type = int(request.GET['dataType'])
        page_num = int(request.GET['pageNum'])
        page_cnt = int(request.GET['pageCount'])

        json_out = {}
        main_out = {}

        try:
            if data_type == -1 and site_id == -1: # 获取全部topic的帖子(不分datatype and site_id)
                post_tp = []
                for topic_tuple in TOPICLIST:
                    topic_id, topic_name = topic_tuple
                    tp_posts = Post.objects(topic_id=topic_id)  

                    topic_dict = {}
                    topic_dict['posts'] = []
                    topic_dict['topic_id'] = topic_id
                    topic_dict['topic_nm'] = topic_name
                    for post in tp_posts:
                        dd = {}
                        dd['_id'] = str(post._id)
                        dd['url'] = post.url
                        dd['site_id'] = post.site_id
                        dd['board'] = post.board
                        dd['topic_id'] = post.topic_id
                        dd['title'] = post.title
                        dd['content'] = post.content
                        dd['pt_time'] = post.pt_time
                        dd['read_num'] = post.read_num
                        dd['comm_num'] = post.comm_num
                        dd['img_url'] = post.img_url
                        dd['repost_num'] = post.repost_num
                        dd['repost_num'] = post.repost_num
                        dd['poster_id'] = post.poster.id
                        dd['poster_name'] = post.poster.name
                        dd['poster_imgurl'] = post.poster.img_url
                        dd['poster_homeurl'] = post.poster.home_url  
                        topic_dict['posts'].append(dd)
                    post_tp.append(topic_dict)

            json_out['code'] = 0 
            json_out['data'] = post_tp 
            json_out['success'] = True

        except:
            traceback.print_exc()
            json_out['code'] = 1 
            json_out['data'] = {}
            json_out['success'] = False
            
        return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

@csrf_exempt
def realtime_monitor(request):
    if request.method == "GET":
        json_out = {}
        main_out = []

        try:
            for dt_tuple  in DTLIST:
                data_dict= {}
                data_dict['topics'] = []
                dt_type, dt_name = dt_tuple
                posts_set = Post.objects.get_posts_by_datatype(dt_type)
                topic_list = []
                for topic_tuple in TOPICLIST:
                    topic_dict = {}
                    topic_dict['posts'] = []
                    topic_id, topic_name = topic_tuple
                    dt_topic_posts_set = posts_set(topic_id=topic_id)
                    topic_dict['topic_id'] = topic_id
                    topic_dict['topic_nm'] = topic_name
                    for post in dt_topic_posts_set:
                        dd = {}
                        dd['_id'] = str(post._id)
                        dd['url'] = post.url
                        dd['site_id'] = post.site_id
                        dd['board'] = post.board
                        dd['topic_id'] = post.topic_id
                        dd['title'] = post.title
                        dd['content'] = post.content
                        dd['pt_time'] = post.pt_time
                        dd['read_num'] = post.read_num
                        dd['comm_num'] = post.comm_num
                        dd['img_url'] = post.img_url
                        dd['repost_num'] = post.repost_num
                        topic_dict['posts'].append(dd)

                    data_dict['topics'].append(topic_dict)
                    #topic_list.append(topic_dct)

                data_dict['dt_name'] = dt_name
                data_dict['dt'] = dt_type

                main_out.append(data_dict)
            json_out['code'] = 0
            json_out['data'] = main_out
            json_out['success'] = True

        except:
            traceback.print_exc()
            json_out['code'] = 1
            json_out['data'] = {}
            json_out['success'] = False

        return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")



# class dashboard_sourceData(APIView):  # http://127.0.0.1:8081/yqdata/dashboard/

#     @csrf_exempt
#     def get(self, request, format=None):
#          json_out = {}
#          main_out = {}
#          days_num = 0
#          data = {}

#          try:
#              # sourcedata
#              days_list = []
#              day = pd.Period(datetime.datetime.now(),freq='D')
#              # logger.info(type(Topic.objects)) # Topic.objects.all()Topic.objects()返回类型相同
#              topic_list = Topic.objects
#              datatype_list = Datatype_name.objects

#              post_7days = Post.objects(Q(pt_time__gte=datetime.datetime.combine\
#                              (date.today()-datetime.timedelta(6),datetime.time.min)) &
#                              Q(pt_time__lte=datetime.datetime.combine(date.today(), datetime.time.max)))

#              while days_num < 7:
#                  day_dict = {}
#                  day_str = day.strftime('%Y%m%d')
#                  day_dict['time'] = day_str

#                  post = post_7days(Q(pt_time__gte=\
#                              datetime.datetime.combine(date.today()-\
#                              datetime.timedelta(days=days_num), \
#                              datetime.time.min)) & \
#                              Q(pt_time__lte=datetime.datetime.combine\
#                              (date.today()-datetime.timedelta(days=days_num), \
#                              datetime.time.max)))


#                  for data in datatype_list:
#                      day_dict['dataTypeName'] = data.datatype_name
#                      day_dict['data_type'] = data.data_type
#                      post_datatype = post(Q(data_type=data.data_type))
#                      # logger.info('post_num = ' + str(len(post_datatype)))
#                      day_dict['post_num'] = len(post_datatype)

#                      day_dict_ = dict(day_dict)
#                      days_list.append(day_dict_)

#                  day -= 1
#                  days_num += 1


#              #######  Hot for all host posts
#              hot_dict = {}
#              hot_posts = post_7days(Q(data_type=3)).order_by \
#                                    ('comm_num')[:10].only("_id", "url", \
#                                      "board", "title", "content", "pt_time", \
#                                      "img_url", "poster","comm_num","repost_num")

#              hot_weibo = post_7days(Q(data_type=2)).order_by \
#                                  ('-comm_num')[:10].only("_id", "url", \
#                                  "board", "title", "content", "pt_time", \
#                                 "img_url","poster","comm_num","repost_num")

#              hot_dict['hotPost'] = self.handle_post_list(hot_posts)
#              hot_dict['hotPoster'] = self.handle_poster_list(hot_posts)
#              hot_dict['hotWeibo'] = self.handle_post_list(hot_weibo)
#              hot_dict['hotWeiboUser'] = self.handle_poster_list(hot_weibo)


#              #######  map data
#              mapData_list = [{'id':'001',
#                                       'pro':"陕西",
#                                       'nums':52
#                                      },
#                                      {
#                                       'id':'002',
#                                       'pro':"北京",
#                                       'nums':100
#                                      },
#                                      {
#                                      'id':'003',
#                                       'pro':"上海",
#                                       'nums':60
#                                       },
#                                      {
#                                      'id':'004',
#                                       'pro':"杭州",
#                                       'nums':48
#                                       },
#                                      {
#                                      'id':'005',
#                                      'pro':"南京",
#                                      'nums':50
#                                      }
#                                  ]

#              wordlist = []
#              wordlist.append({'word': '皇甫','weight':'200'})
#              wordlist.append({'word': '卫罡','weight':'100'})
#              wordlist.append({'word': '吴明伟','weight':'400'})
#              wordlist.append({'word': '薛鲁国','weight':'250'})
#              wordlist.append({'word': '彭祯','weight':'100'})
            

#              main_out['mapData'] = mapData_list
#              main_out['sourceData'] = days_list
#              main_out['Hot'] = hot_dict
#              main_out['word_cloud'] = wordlist

#              json_out['code'] = 0
#              json_out['success'] = True
#              json_out['data'] = main_out
#          except:
#              traceback.print_exc()
#              json_out['code'] = 1
#              json_out['data'] = {}
#              json_out['success'] = False

#          return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

#     def handle_post_list(self, post_list):
#         hot_post_list = []
#         for post in post_list:
#             post_dict = {}
#             post_dict['id'] = str(post._id)
#             post_dict['url'] = post.url
#             post_dict['board'] = post.board
#             post_dict['title'] = post.title
#             post_dict['content'] = post.content
#             post_dict['pt_time'] = post.pt_time
#             post_dict['image_url'] = post.img_url
#             post_dict['comm_num'] = post.comm_num
#             post_dict['repost_num'] = post.repost_num
#             hot_post_list.append(post_dict)
#         return hot_post_list

#     def handle_poster_list(self, poster_list):
#         hot_poster_list = []
#         for poster in poster_list:
#             #logger.info(type(poster.poster))
#             poster_dict = {}
#             poster_dict['id'] = poster.poster.id
#             poster_dict['name'] = poster.poster.name
#             poster_dict['home_url'] = poster.poster.home_url
#             poster_dict['img_url'] = poster.poster.img_url
#             poster_dict['post_num'] = random.choice([2,4,6,8,5,3,7,9])
#             poster_dict['Follows'] = 'abc'
#             poster_dict['Following'] = 'def'
#             poster_dict['level'] = '2'
#             poster_dict['location'] = 'china'
#             poster_dict['intro'] = 'hello world'
#             poster_dict['birthday'] = '1995-01-01'
#             poster_dict['company'] = 'jiaotong university'
#             hot_poster_list.append(poster_dict)
#         return hot_poster_list


@csrf_exempt
def dashboard_sourceData(request):
    if request.method == 'GET':
        json_out = {}
        main_out = {}
        days_num = 0
        data = {}
    
        try:
            # sourcedata
            days_list = []
            day = pd.Period(datetime.datetime.now(),freq='D')
            # logger.info(type(Topic.objects)) # Topic.objects.all()Topic.objects()返回类型相同
            topic_list = Topic.objects
            datatype_list = Datatype_name.objects

            today = date.today()
            post_7days = Post.objects(Q(pt_time__gte=datetime.datetime.combine\
                            (today-datetime.timedelta(7),datetime.time.min)) &
                            Q(pt_time__lte=datetime.datetime.combine(today, datetime.time.max)))

            while days_num < 7:
                day_str = day.strftime('%Y%m%d')  

                day_change = today - datetime.timedelta(days=days_num)
                post = post_7days(Q(pt_time__gte=\
                            datetime.datetime.combine(day_change,datetime.time.min)) & \
                            Q(pt_time__lte=datetime.datetime.combine\
                            (day_change, datetime.time.max)))


                for topic in topic_list:
                    for data in datatype_list:
                        day_dict = {}
                        day_dict['time'] = day_str
                        day_dict['topic_id'] = topic._id
                        day_dict['topic_name'] = topic.topic_name
                        day_dict['dataTypeName'] = data.datatype_name
                        day_dict['data_type'] = data.data_type
                        post_datatype = post(Q(data_type=data.data_type) & Q(topic_id=topic._id))
                        # logger.info('post_num = ' + str(len(post_datatype)))
                        day_dict['post_num'] = post_datatype.count()
                        days_list.append(day_dict)

                for data in datatype_list:
                    day_dict = {}
                    day_dict['time'] = day_str
                    day_dict['topic_id'] = 0
                    day_dict['topic_name'] = ''
                    day_dict['dataTypeName'] = data.datatype_name
                    day_dict['data_type'] = data.data_type
                    post_datatype = post(Q(data_type=data.data_type) & Q(topic_id=0))
                    # logger.info('post_num = ' + str(len(post_datatype)))
                    day_dict['post_num'] = post_datatype.count()
                    days_list.append(day_dict)

                day -= 1
                days_num += 1


            #######  Hot for all host posts
            hot_dict = {}
            hot_posts = post_7days(Q(topic_id__ne=0) & (Q(data_type=3) | Q(data_type=2))).order_by \
                                  ('-comm_num')[:10].only("_id", "url", \
                                    "board", "title", "content", "pt_time", \
                                    "img_url", "poster")

            # hot_poster = post_7days.only('poster').all()
            # logger.info("hot_poster = " + str(hot_poster.count()))
    
            hot_weibo = post_7days(Q(topic_id__ne=0) & Q(data_type=2)).order_by \
                                ('-comm_num')[:10].only("_id", "url", \
                                "board", "title", "content", "pt_time", \
                               "img_url")

            hot_dict['hotPost'] = handle_post_list(hot_posts)
            hot_dict['hotPoster'] = handle_poster_list(hot_posts)
            hot_dict['hotWeibo'] = handle_post_list(hot_weibo)


            # wordlist = []
            # wordres=Cloud_formain.objects.only("word", "frequency")
            # for worditem in wordres:
            #     temp={}
            #     temp['word']=worditem.word
            #     temp['weight']=worditem.frequency
            #     wordlist.append(temp)


            #######  map data
            mapData_list = [{'id':'001',
                                     'pro':"陕西",
                                     'nums':52
                                    },
                                    {
                                     'id':'002',
                                     'pro':"北京",
                                     'nums':100
                                    },
                                    {
                                    'id':'003',
                                     'pro':"上海",
                                     'nums':60
                                     },
                                    {
                                    'id':'004',
                                     'pro':"杭州",
                                     'nums':48
                                     },
                                    {
                                    'id':'005',
                                    'pro':"南京",
                                    'nums':50
                                    }
                                ]

            main_out['mapData'] = mapData_list
            main_out['sourceData'] = days_list
            main_out['Hot'] = hot_dict
            # main_out['word_cloud'] = wordlist



            json_out['code'] = 0
            json_out['success'] = True
            json_out['data'] = main_out
        except:
            traceback.print_exc()
            json_out['code'] = 1
            json_out['data'] = {}
            json_out['success'] = False

        return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")



def handle_post_list(post_list):
    hot_post_list = []
    for post in post_list:
        post_dict = {}
        post_dict['id'] = str(post._id)
        post_dict['url'] = post.url
        post_dict['board'] = post.board
        post_dict['title'] = post.title

        post_content = post.content.strip()
        if post.data_type == 2:
            post_content = re.sub(r'n{2,}t{2,}|t{1,}n{1,}t{1,}|n{1,}t{2,}n{1,}|t{3,}|n{3,}', '', post_content)
        post_content = post_content.decode('utf-8')
        if len(post_content) > 50:
            post_dict['content'] = post_content[:50].encode('utf-8') + '...'
        else:
            post_dict['content'] = post_content.encode('utf-8')
        post_dict['pt_time'] = post.pt_time
        post_dict['image_url'] = post.img_url
        hot_post_list.append(post_dict)
    return hot_post_list


def handle_poster_list(poster_list):
    hot_poster_list = []
    for poster in poster_list:
        poster_dict = {}
        poster_dict['id'] = poster.poster.id
        poster_dict['name'] = poster.poster.name
        poster_dict['home_url'] = poster.poster.home_url
        poster_dict['img_url'] = poster.poster.img_url
        poster_dict['post_num'] = random.choice([2,4,6,8,5,3,7,9])
        hot_poster_list.append(poster_dict)
    return hot_poster_list


@csrf_exempt
def dashboard_sourceData_temp(request):
    if request.method == 'GET':
        json_out = {}
        main_out = {}
        days_num = 0
        data = {}

        try:
            # sourcedata
            days_list = []
            topic_list = Topic.objects
            day = pd.Period(datetime.datetime.now(),freq='D')
            # logger.info(type(Topic.objects)) # Topic.objects.all()Topic.objects()返回类型相同
            datatype_list = Datatype_name.objects

            post_7days = Post.objects(Q(pt_time__gte=datetime.datetime.combine\
                             (date.today()-datetime.timedelta(6),datetime.time.min)) &
                             Q(pt_time__lte=datetime.datetime.combine(date.today(), datetime.time.max)))

            while days_num < 7:
                day_dict = {}
                day_str = day.strftime('%Y%m%d')
                day_dict['time'] = day_str

                post = post_7days(Q(pt_time__gte=\
                             datetime.datetime.combine(date.today()-\
                             datetime.timedelta(days=days_num), \
                             datetime.time.min)) & \
                             Q(pt_time__lte=datetime.datetime.combine\
                             (date.today()-datetime.timedelta(days=days_num), \
                             datetime.time.max)))

                for topic in topic_list:
                    for data in datatype_list:
                        day_dict = {}
                        day_dict['time'] = day_str
                        day_dict['topic_id'] = topic._id
                        day_dict['topic_name'] = topic.topic_name
                        day_dict['dataTypeName'] = data.datatype_name
                        day_dict['data_type'] = data.data_type
                        post_datatype = post(Q(data_type=data.data_type) & Q(topic_id=topic._id))
                        # logger.info('post_num = ' + str(len(post_datatype)))
                        day_dict['post_num'] = post_datatype.count()
                        days_list.append(day_dict)


                # for data in datatype_list:
                #     day_dict['dataTypeName'] = data.datatype_name
                #     day_dict['data_type'] = data.data_type
                #     post_datatype = post(Q(data_type=data.data_type))
                #     # logger.info('post_num = ' + str(len(post_datatype)))
                #     day_dict['post_num'] = len(post_datatype)

                #     day_dict_ = dict(day_dict)
                #     days_list.append(day_dict_)

                day -= 1
                days_num += 1


            #######  Hot for all host posts
            hot_dict = {}
            hot_posts_temp = post_7days(Q(data_type=3))
            hot_posts = hot_posts_temp.order_by \
                                   ('-comm_num')[:10].only("_id", "url", \
                                     "board", "title", "content", "pt_time", \
                                     "img_url","comm_num","repost_num")

            hot_weibo_temp = post_7days(Q(data_type=2))
            hot_weibo = hot_weibo_temp.order_by \
                                 ('-comm_num')[:10].only("_id", "url", \
                                 "board", "title", "content", "pt_time", \
                                "img_url","comm_num","repost_num")

            hot_poster = hot_posts_temp.order_by('-poster.post_num')[:10].only("poster")

            hot_weibouser_post_num = hot_weibo_temp.order_by('-poster.post_num').only("poster")
            hot_weibouser = []
            hot_weibouser_id = []
            num_ten=0
            for item in hot_weibouser_post_num:
              if num_ten ==10:
                break
              else:
                if item.poster.id not in hot_weibouser_id:
                  hot_weibouser.append(item)
                  hot_weibouser_id.append(item.poster.id)
                  num_ten=num_ten+1

            hot_dict['hotPost'] = handle_post_list1(hot_posts)
            hot_dict['hotPoster'] = handle_poster_list1(hot_poster)
            hot_dict['hotWeibo'] = handle_post_list1(hot_weibo)
            # hot_dict['hotPoster'] = handle_poster_list(hot_posts)

            hot_dict['hotWeiboUser'] = handle_weibouser_list1(hot_weibouser)


             #######  map data
            mapData_list = [{'id':'001',
                                      'pro':"陕西",
                                      'nums':52
                                     },
                                     {
                                      'id':'002',
                                      'pro':"北京",
                                      'nums':100
                                     },
                                     {
                                     'id':'003',
                                      'pro':"上海",
                                      'nums':60
                                      },
                                     {
                                     'id':'004',
                                      'pro':"杭州",
                                      'nums':48
                                      },
                                     {
                                     'id':'005',
                                     'pro':"南京",
                                     'nums':50
                                     }
                                 ]

            wordlist = []
            wordres=Cloud_formain.objects(Q(topic_id=999)).only("word", "frequency")
            for worditem in wordres:
                temp={}
                temp['word']=worditem.word
                temp['weight']=worditem.frequency
                wordlist.append(temp)

            

            main_out['mapData'] = mapData_list
            main_out['sourceData'] = days_list
            main_out['Hot'] = hot_dict
            main_out['word_cloud'] = wordlist

            json_out['code'] = 0
            json_out['success'] = True
            json_out['data'] = main_out
        except:
            traceback.print_exc()
            json_out['code'] = 1
            json_out['data'] = {}
            json_out['success'] = False

        return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")


@csrf_exempt
def dashboard_sourceData_time(request):
    if request.method == 'GET':
        json_out = {}
        main_out = {}
        days_num = 0
        data = {}
        post_time = datetime.datetime.strptime(request.GET['date'], "%Y-%m-%d")
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]
        if abs(int(time_stamp)-int(time.time())) < 60:
        # if 1:
            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)
            userid = pld['data']['id']
            login_time = pld['data']['login_time']
            try:
                # sourcedata
                days_list = []
                userrole_id=User.objects(Q(user_id=userid)).only('user_role_id').first().user_role_id
                if userrole_id==0:
                    topic_list = Topic.objects
                    post_7days = Post.objects(Q(pt_time__gte=datetime.datetime.combine\
                                 (post_time-datetime.timedelta(6),datetime.time.min)) &
                                 Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max)) & Q(user_id_list__ne=None))
                elif userrole_id==2:
                    usergroup_id=User.objects(Q(user_id=userid)).only('user_group_id').first().user_group_id
                    userid_res=User.objects(Q(user_group_id=usergroup_id)).only('user_id')
                    userid_list=[i.user_id for i in userid_res]
                    topic_list = Topic.objects(Q(user_id__in=userid_list))
                    post_7days = Post.objects(Q(pt_time__gte=datetime.datetime.combine\
                                 (post_time-datetime.timedelta(6),datetime.time.min)) &
                                 Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max)) & Q(user_id_list__in=userid_list))
                else:
                    topic_list = Topic.objects(Q(user_id=userid))
                    post_7days = Post.objects(Q(pt_time__gte=datetime.datetime.combine\
                                 (post_time-datetime.timedelta(6),datetime.time.min)) &
                                 Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max)) & Q(user_id_list=userid))
                # day = pd.Period(datetime.datetime.now(),freq='D')
                # logger.info(type(Topic.objects)) # Topic.objects.all()Topic.objects()返回类型相同
                datatype_list = Datatype_name.objects

                # post_7days = Post.objects(Q(pt_time__gte=datetime.datetime.combine\
                                 # (post_time-datetime.timedelta(6),datetime.time.min)) &
                                 # Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max)) & Q(user_id_list=userid))

                while days_num < 7:
                    # day_dict = {}
                    # day_str = day.strftime('%Y%m%d')
                    # day_dict['time'] = day_str

                    post = post_7days(Q(pt_time__gte=\
                                 datetime.datetime.combine(post_time-\
                                 datetime.timedelta(days=days_num), \
                                 datetime.time.min)) & \
                                 Q(pt_time__lte=datetime.datetime.combine\
                                 (post_time-datetime.timedelta(days=days_num), \
                                 datetime.time.max)))

                    for topic in topic_list:
                        for data in datatype_list:
                            day_dict = {}
                            ptime = post_time - datetime.timedelta(days_num)
                            day_dict['time'] = ptime.strftime('%Y-%m-%d')
                            day_dict['topic_id'] = topic._id
                            day_dict['topic_name'] = topic.topic_name
                            day_dict['dataTypeName'] = data.datatype_name
                            day_dict['data_type'] = data.data_type
                            post_datatype = post(Q(data_type=data.data_type) & Q(topic_id=topic._id))
                            # logger.info('post_num = ' + str(len(post_datatype)))
                            day_dict['post_num'] = post_datatype.count()
                            days_list.append(day_dict)


                    # for data in datatype_list:
                    #     day_dict['dataTypeName'] = data.datatype_name
                    #     day_dict['data_type'] = data.data_type
                    #     post_datatype = post(Q(data_type=data.data_type))
                    #     # logger.info('post_num = ' + str(len(post_datatype)))
                    #     day_dict['post_num'] = len(post_datatype)

                    #     day_dict_ = dict(day_dict)
                    #     days_list.append(day_dict_)

                    # day -= 1
                    days_num += 1


                #######  Hot for all host posts
                hot_dict = {}
                hot_posts_temp = post_7days(Q(data_type=3))
                hot_posts = hot_posts_temp.order_by \
                                       ('-comm_num')[:10].only("_id", "url", \
                                         "board", "title", "content", "pt_time", \
                                         "img_url","comm_num","repost_num")

                hot_weibo_temp = post_7days(Q(data_type=2))
                hot_weibo = hot_weibo_temp.order_by \
                                     ('-comm_num')[:10].only("_id", "url", \
                                     "board", "title", "content", "pt_time", \
                                    "img_url","comm_num","repost_num")

                hot_poster = hot_posts_temp.order_by('-poster.post_num')[:10].only("poster")

                hot_weibouser_post_num = hot_weibo_temp.order_by('-poster.post_num').only("poster")
                hot_weibouser = []
                hot_weibouser_id = []
                num_ten=0
                for item in hot_weibouser_post_num:
                  if num_ten ==10:
                    break
                  else:
                    if item.poster.id not in hot_weibouser_id:
                      hot_weibouser.append(item)
                      hot_weibouser_id.append(item.poster.id)
                      num_ten=num_ten+1

                hot_dict['hotPost'] = handle_post_list1(hot_posts)
                hot_dict['hotPoster'] = handle_poster_list1(hot_poster)
                hot_dict['hotWeibo'] = handle_post_list1(hot_weibo)
                # hot_dict['hotPoster'] = handle_poster_list(hot_posts)

                hot_dict['hotWeiboUser'] = handle_weibouser_list1(hot_weibouser)


                 #######  map data
                mapData_list = [{'id':'001',
                                          'pro':"陕西",
                                          'nums':52
                                         },
                                         {
                                          'id':'002',
                                          'pro':"北京",
                                          'nums':100
                                         },
                                         {
                                         'id':'003',
                                          'pro':"上海",
                                          'nums':60
                                          },
                                         {
                                         'id':'004',
                                          'pro':"杭州",
                                          'nums':48
                                          },
                                         {
                                         'id':'005',
                                         'pro':"南京",
                                         'nums':50
                                         }
                                     ]

                wordlist = []
                # post_time = datetime.datetime.strptime(request.GET['date'], "%Y-%m-%d %H:%M:%S")
         #        Post.objects(Q(pt_time__gt=date_time) & \
                        # Q(pt_time__lte=datetime.datetime.combine(date_time, datetime.time.max)))
                # wordres=Cloud_formain.objects(Q(topic_id=999)).only("word", "frequency")
                if request.GET['date'] == '2017-11-04' or request.GET['date'] == '2017-10-28':
                    wordres=Cloud_formain.objects(Q(topic_id = 999) & Q(sday__gte = post_time) & Q(sday__lte = datetime.datetime.combine(post_time, datetime.time.max))).only("word", "frequency")
                else:
                    wordres=Cloud_formain.objects(Q(topic_id=999)).only("word", "frequency")
                for worditem in wordres:
                    temp={}
                    temp['word']=worditem.word
                    temp['weight']=worditem.frequency
                    wordlist.append(temp)

                

                main_out['mapData'] = mapData_list
                main_out['sourceData'] = days_list
                main_out['Hot'] = hot_dict
                main_out['word_cloud'] = wordlist

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
            traceback.print_exc()
            json_out['code'] = 1
            json_out['data'] = {}
            json_out['success'] = False

            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")




# @csrf_exempt
# def dashboard_sourceData_time(request):
#     if request.method == 'GET':
#         json_out = {}
#         main_out = {}
#         days_num = 0
#         data = {}
#         post_time = datetime.datetime.strptime(request.GET['date'], "%Y-%m-%d")

#         try:
#             # sourcedata
#             days_list = []
#             # day = pd.Period(datetime.datetime.now(),freq='D')
#             # logger.info(type(Topic.objects)) # Topic.objects.all()Topic.objects()返回类型相同
#             datatype_list = Datatype_name.objects
#             topic_list = Topic.objects


            

#             post_7days = Post.objects(Q(pt_time__gte=datetime.datetime.combine\
#                              (post_time-datetime.timedelta(6),datetime.time.min)) &
#                              Q(pt_time__lte=datetime.datetime.combine(post_time, datetime.time.max)))

#             while days_num < 7:
#                 # day_dict = {}
#                 # day_str = day.strftime('%Y%m%d')
#                 # day_dict['time'] = day_str

#                 post = post_7days(Q(pt_time__gte=\
#                              datetime.datetime.combine(post_time-\
#                              datetime.timedelta(days=days_num), \
#                              datetime.time.min)) & \
#                              Q(pt_time__lte=datetime.datetime.combine\
#                              (post_time-datetime.timedelta(days=days_num), \
#                              datetime.time.max)))


#                 for topic in topic_list:
#                     for data in datatype_list:
#                         day_dict = {}
#                         # day_dict['time'] = day_str
#                         # day_dict['topic_id'] = topic._id
#                         # day_dict['topic_name'] = topic.topic_name
#                         day_dict['dataTypeName'] = data.datatype_name
#                         day_dict['data_type'] = data.data_type
#                         post_datatype = post(Q(data_type=data.data_type) & Q(topic_id=topic._id))
#                         # logger.info('post_num = ' + str(len(post_datatype)))
#                         day_dict['post_num'] = len(post_datatype)
#                         day_dict_ = dict(day_dict)
#                         days_list.append(day_dict_)


#                 # for data in datatype_list:
#                 #     day_dict['dataTypeName'] = data.datatype_name
#                 #     day_dict['data_type'] = data.data_type
#                 #     post_datatype = post(Q(data_type=data.data_type))
#                 #     # logger.info('post_num = ' + str(len(post_datatype)))
#                 #     day_dict['post_num'] = len(post_datatype)

#                 #     day_dict_ = dict(day_dict)
#                 #     days_list.append(day_dict_)

#                 # day -= 1
#                 days_num += 1


#             #######  Hot for all host posts
#             hot_dict = {}
#             hot_posts_temp = post_7days(Q(data_type=3))
#             hot_posts = hot_posts_temp.order_by \
#                                    ('-comm_num')[:10].only("_id", "url", \
#                                      "board", "title", "content", "pt_time", \
#                                      "img_url","comm_num","repost_num","poster")

#             hot_weibo_temp = post_7days(Q(data_type=2))
#             hot_weibo = hot_weibo_temp.order_by \
#                                  ('-comm_num')[:10].only("_id", "url", \
#                                  "board", "title", "content", "pt_time", \
#                                 "img_url","comm_num","repost_num","poster")

#             # hot_poster = hot_posts_temp.order_by('-poster.post_num').only("poster")
#             hot_weibouser_post_num = hot_weibo_temp.order_by('-poster.post_num').only("poster")
#             hot_weibouser = []
#             hot_weibouser_id = []
#             num_ten=0
#             for item in hot_weibouser_post_num:
#               if num_ten ==10:
#                 break
#               else:
#                 if item.poster.id not in hot_weibouser_id:
#                   hot_weibouser.append(item)
#                   hot_weibouser_id.append(item.poster.id)
#                   num_ten=num_ten+1




#             hot_dict['hotPost'] = handle_post_list1(hot_posts)
#             # hot_dict['hotPoster'] = handle_poster_list(hot_poster)
#             hot_dict['hotWeibo'] = handle_post_list1(hot_weibo)
#             hot_dict['hotWeiboUser'] = handle_weibouser_list1(hot_weibouser)


#              #######  map data
#             mapData_list = [{'id':'001',
#                                       'pro':"陕西",
#                                       'nums':52
#                                      },
#                                      {
#                                       'id':'002',
#                                       'pro':"北京",
#                                       'nums':100
#                                      },
#                                      {
#                                      'id':'003',
#                                       'pro':"上海",
#                                       'nums':60
#                                       },
#                                      {
#                                      'id':'004',
#                                       'pro':"杭州",
#                                       'nums':48
#                                       },
#                                      {
#                                      'id':'005',
#                                      'pro':"南京",
#                                      'nums':50
#                                      }
#                                  ]

#             wordlist = []
#             wordres=Cloud_formain.objects.only("word", "frequency")
#             for worditem in wordres:
#                 temp={}
#                 temp['word']=worditem.word
#                 temp['weight']=worditem.frequency
#                 wordlist.append(temp)

            

#             main_out['mapData'] = mapData_list
#             main_out['sourceData'] = days_list
#             main_out['Hot'] = hot_dict
#             main_out['word_cloud'] = wordlist

#             json_out['code'] = 0
#             json_out['success'] = True
#             json_out['data'] = main_out
#         except:
#             traceback.print_exc()
#             json_out['code'] = 1
#             json_out['data'] = {}
#             json_out['success'] = False

#         return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")



def handle_post_list1(post_list):
    hot_post_list = []
    for post in post_list:
        post_dict = {}
        post_dict['id'] = str(post._id)
        post_dict['url'] = post.url
        post_dict['board'] = post.board
        post_dict['title'] = post.title
        content_temp1 = post.content.strip()
        content_temp2 = content_temp1.strip('nt展开全文c...')
        post_dict['content'] = content_temp2[(content_temp2.find('t')+1):]
        post_dict['pt_time'] = post.pt_time
        post_dict['image_url'] = post.img_url
        post_dict['comm_num'] = post.comm_num
        post_dict['repost_num'] = post.repost_num
        post_dict['read_num'] = post.read_num
        post_dict['img_url'] = post.poster.img_url
        post_dict['name'] = post.poster.name
        hot_post_list.append(post_dict)
    return hot_post_list

poster_id_list = ['1742944894','1533789260','1225314032','1788911247','1750067330']
poster_name_list = [u'何凯文',u'陈学冬',u'新浪教育',u'谷大白话',u'高考直通车']
poster_homeurl_list = ['https://weibo.com/p/1005051742944894/home?from=usercardnew&is_hot=1#place&refer_flag=0000020001_','https://weibo.com/cheneydong?refer_flag=1001030101_&is_hot=1','https://weibo.com/edublog?refer_flag=1001030101_','https://weibo.com/ichthy?refer_flag=1001030103_','https://weibo.com/gaokao96040?refer_flag=1001030102_']
poster_imgurl_list = ['https://tva3.sinaimg.cn/crop.0.0.180.180.180/67e33a7ejw1e8qgp5bmzyj2050050aa8.jpg','https://tvax3.sinaimg.cn/crop.0.0.512.512.180/5b6bc44cly8fhd9rb7x34j20e80e8t8y.jpg','https://tva4.sinaimg.cn/crop.0.0.180.180.180/4908cef0jw1e8qgp5bmzyj2050050aa8.jpg','https://tva1.sinaimg.cn/crop.0.0.180.180.180/6aa09e8fjw1e8qgp5bmzyj2050050aa8.jpg','https://tva2.sinaimg.cn/crop.0.0.180.180.180/684fe882jw1e8qgp5bmzyj2050050aa8.jpg']
poster_postnum_list = [5480,874,33273,30035,85821]
poster_follows_list = [3020567,28232264,4485611,9347920,1265385]
poster_following_list = [30,339,1387,1324,474]
poster_location_list = [u'北京',u'其他',u'北京',u'北京',u'广东']
poster_intro_list = [u'将激情和实力完美演绎的考研名师',u'演员',u'新浪教育官方微博。 第一时间发布新闻资讯。 欢迎报料、投稿',u'THERES NO『俗』WITHOUT『谷』',u'高考直通车官方微博，全国最大的中学生学习交流平台。']

def handle_weibouser_list1(weibouser_list):
    hot_poster_list = []
    for i  in range(0,5):
        #logger.info(type(poster.poster))
        poster_dict = {}
        poster_dict['id'] = poster_id_list[i]
        poster_dict['name'] = poster_name_list[i]
        poster_dict['home_url'] = poster_homeurl_list[i]
        poster_dict['img_url'] = poster_imgurl_list[i]
        poster_dict['post_num'] = poster_postnum_list[i]
        poster_dict['Follows'] = poster_follows_list[i]
        poster_dict['Following'] = poster_following_list[i]
        poster_dict['location'] = poster_location_list[i]
        poster_dict['intro'] = poster_intro_list[i]
        # poster_dict['id'] = poster.poster.id
        # poster_dict['name'] = poster.poster.name
        # poster_dict['home_url'] = poster.poster.home_url
        # poster_dict['img_url'] = poster.poster.img_url
        # poster_dict['post_num'] = poster.poster.post_num
        # poster_dict['Follows'] = poster.poster.follows
        # poster_dict['Following'] = poster.poster.following
        # poster_dict['location'] = poster.poster.location
        # poster_dict['intro'] = poster.poster.intro
        hot_poster_list.append(poster_dict)
    return hot_poster_list

def handle_poster_list1(poster_list):
    hot_poster_list = []
    for poster in poster_list:
        #logger.info(type(poster.poster))
        poster_dict = {}
        poster_dict['id'] = poster.poster.id
        poster_dict['name'] = poster.poster.name
        poster_dict['home_url'] = poster.poster.home_url
        poster_dict['img_url'] = poster.poster.img_url
        poster_dict['post_num'] = poster.poster.post_num
        poster_dict['Follows'] = poster.poster.follows
        poster_dict['Following'] = poster.poster.following
        hot_poster_list.append(poster_dict)
    return hot_poster_list