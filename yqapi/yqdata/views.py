# -*-coding:utf-8 -*-

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from yqdata.models import Poster, Post, Topic, Site_topic, Site, Datatype_name
from datetime import date, timedelta
import datetime
import pandas as pd
import traceback
from django.http import HttpResponse
import random

from mongoengine import *
import json
from mongoengine.queryset.visitor import Q

import logging
logger = logging.getLogger('django')

connect('yuqing', alias='default', host='118.190.133.203', port=27016,username='yuqing',password='yuqing@2017')
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
                    day_dict['topic_id'] = topic._id
                    day_dict['topic_name'] = topic.topic_name
                    for data in datatype_list:
                        day_dict['dataTypeName'] = data.datatype_name
                        day_dict['data_type'] = data.data_type
                        post_datatype = post(Q(data_type=data.data_type) & Q(topic_id=topic._id))
                        # logger.info('post_num = ' + str(len(post_datatype)))
                        day_dict['post_num'] = len(post_datatype)

                        day_dict_ = dict(day_dict)
                        days_list.append(day_dict_)

                day -= 1
                days_num += 1


            #######  Hot for all host posts
            hot_dict = {}
            hot_posts = post_7days(Q(data_type=3) | Q(data_type=2)).order_by \
                                  ('comm_num')[:10].only("_id", "url", \
                                    "board", "title", "content", "pt_time", \
                                    "img_url", "poster")

            # hot_poster = post_7days.only('poster').all()
            # logger.info("hot_poster = " + str(hot_poster.count()))
    
            hot_weibo = post_7days(Q(data_type=2)).order_by \
                                ('-comm_num')[:10].only("_id", "url", \
                                "board", "title", "content", "pt_time", \
                               "img_url")

            hot_dict['hotPost'] = handle_post_list(hot_posts)
            hot_dict['hotPoster'] = handle_poster_list(hot_posts)
            hot_dict['hotWeibo'] = handle_post_list(hot_weibo)


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
        post_dict['content'] = post.content
        post_dict['pt_time'] = post.pt_time
        post_dict['image_url'] = post.img_url
        hot_post_list.append(post_dict)
    return hot_post_list


def handle_poster_list(poster_list):
    hot_poster_list = []
   # hot_poster = list(poster_list)
   # hot_poster.extend(weibo_list)
    for poster in poster_list:
        #logger.info(type(poster.poster))
        poster_dict = {}
        poster_dict['id'] = poster.poster.id
        poster_dict['name'] = poster.poster.name
        poster_dict['home_url'] = poster.poster.home_url
        poster_dict['img_url'] = poster.poster.img_url
        poster_dict['post_num'] = random.choice([2,4,6,8,5,3,7,9])
        hot_poster_list.append(poster_dict)
    return hot_poster_list
