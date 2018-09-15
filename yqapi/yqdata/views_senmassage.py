# -*-coding:utf-8 -*-

#https://github.com/django-json-api/django-rest-framework-json-api/blob/develop/rest_framework_json_api/views.py
#http://django-rest-framework-json-api.readthedocs.io/en/stable/getting-started.html#running-the-example-app
# http://getblimp.github.io/django-rest-framework-jwt/

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from yqdata.models import Poster, Post, Topic, Site_topic, Site, Datatype_name, Sen_message, User, TiebaPost
from datetime import date, timedelta
import datetime
import pandas as pd
from rest_framework.views import APIView
import traceback
import time
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
import random
from bson.objectid import ObjectId
from mongoengine import *
import json
from mongoengine.queryset.visitor import Q
from serializers import PostSerializer
import base64,re
from yqdata.Auths import *
import logging
import traceback
logger = logging.getLogger('django')
ISOTIMEFORMAT='%Y-%m-%d %X'
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


#取证api
class Evidence(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        # userid = int(request.GET['userId'])
        post_id = request.GET['id']
      
        a = ObjectId(post_id)
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']
            try:
                post_msg = Post.objects(_id=a).first()
                
                file_str = post_msg.html.read()

                # file_name = "%s_%s.html" % (post_msg['title'],post_msg['pt_time'])
                file_name = post_id + ".html"
                
                response = HttpResponse(file_str,content_type='application/octet-stream')
                response['Content-Disposition'] = 'attachment;filename=%s' % (file_name)
                return response
            except:
                print traceback.print_exc()
        else:
            # print traceback.print_exc()
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")


#添加敏感信息，点击界面
class addSenmsg_UI(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        # user_id = int(request.GET['userId'])
        post_id = request.GET['id']
        json_out = {}
        a = ObjectId(post_id)
        print a
        print type(a)
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
                data_msg = {}
                #从post表取出
                post_msg = Post.objects(_id=a)
                # print len(post_msg)
                # print '11111'
                # for post_msg in post_msgs:
                # print post_msg.url
                # print post_msg.title
                # print post_msg.html.grid_id
                if post_msg:
                    temp=post_msg.first()
                    post_msg=temp
                    data_msg['id'] = str(a)
                    data_msg['url'] = post_msg.url
                    data_msg['title'] = post_msg.title
                    data_msg['content'] = post_msg.content
                    data_msg['pt_time'] = post_msg.pt_time
                    data_msg['dataType'] = post_msg.data_type
                    if post_msg.site_id == 201:
                        data_msg['board'] = u'新浪微博'
                    else:
                        data_msg['board'] = post_msg.board
                    data_msg['st_time'] = post_msg.st_time
                    data_msg['is_report'] = ''
                    data_msg['QQ'] = ''
                    data_msg['cellphone'] = ''
                    data_msg['Ip'] = ''
                    data_msg['poster'] = {}
                    data_msg['site_id'] = post_msg.site_id
                    data_msg['site_name'] = post_msg.site_name
                    data_msg['topic_id'] = post_msg.topic_id
                    data_msg['html'] = str(post_msg.html.grid_id)
                    data_msg['st_time'] = post_msg.st_time
                    data_msg['read_num'] = post_msg.read_num
                    data_msg['comm_num'] = post_msg.comm_num
                    data_msg['img_url'] = post_msg.img_url
                    data_msg['repost_num'] = post_msg.repost_num
                    data_msg['lan_type'] = post_msg.lan_type
                    data_msg['repost_pt_id'] = post_msg.repost_pt_id
                    data_msg['text_type'] = post_msg.text_type
                    data_msg['user_id_list'] = post_msg.user_id_list
                    print post_msg.poster
                    if post_msg.poster:
                        data_msg['poster']['home_url'] = post_msg.poster.home_url
                        data_msg['poster']['img_url'] = post_msg.poster.img_url
                        data_msg['poster']['id'] = post_msg.poster.id
                        data_msg['poster']['name'] = post_msg.poster.name
                        data_msg['poster']['authentication'] = post_msg.poster.authentication
                        data_msg['poster']['birthday'] = post_msg.poster.birthday
                        data_msg['poster']['following'] = post_msg.poster.following
                        data_msg['poster']['follows'] = post_msg.poster.follows
                        data_msg['poster']['intro'] = post_msg.poster.intro
                        data_msg['poster']['level'] = post_msg.poster.level
                        data_msg['poster']['location'] = post_msg.poster.location
                        data_msg['poster']['post_num'] = post_msg.poster.post_num
                    else:
                        data_msg['poster']['home_url'] = ""
                        data_msg['poster']['img_url'] = ""
                        data_msg['poster']['id'] = ""
                        data_msg['poster']['name'] = ""
                        data_msg['poster']['authentication'] = ""
                        data_msg['poster']['birthday'] = ""
                        data_msg['poster']['following'] = ""
                        data_msg['poster']['follows'] = ""
                        data_msg['poster']['intro'] = ""
                        data_msg['poster']['level'] = ""
                        data_msg['poster']['location'] = ""
                        data_msg['poster']['post_num'] = ""
                    print '2222'

                    data.append(data_msg)
                else:
                    post_msg = TiebaPost.objects(_id=a).first()
                    data_msg['id'] = str(a)
                    data_msg['url'] = post_msg.url
                    print '333'
                    data_msg['title'] = post_msg.title
                    data_msg['content'] = post_msg.content
                    data_msg['pt_time'] = post_msg.pt_time
                    data_msg['dataType'] = post_msg.data_type
                    if post_msg.site_id == 201:
                        data_msg['board'] = u'新浪微博'
                    else:
                        data_msg['board'] = post_msg.board
                    data_msg['st_time'] = post_msg.st_time
                    data_msg['is_report'] = ''
                    data_msg['QQ'] = ''
                    data_msg['cellphone'] = ''
                    data_msg['Ip'] = ''
                    data_msg['poster'] = {}
                    data_msg['site_id'] = post_msg.site_id
                    data_msg['site_name'] = post_msg.site_name
                    data_msg['topic_id'] = post_msg.topic_id
                    data_msg['html'] = str(post_msg.html.grid_id)
                    # data_msg['st_time'] = post_msg.st_time
                    data_msg['read_num'] = post_msg.read_num
                    data_msg['comm_num'] = post_msg.comm_num
                    data_msg['img_url'] = post_msg.img_url
                    data_msg['repost_num'] = post_msg.repost_num
                    data_msg['lan_type'] = post_msg.lan_type
                    data_msg['repost_pt_id'] = post_msg.repost_pt_id
                    data_msg['text_type'] = post_msg.text_type
                    data_msg['user_id_list'] = post_msg.user_id_list
                    print post_msg.poster
                    if post_msg.poster:
                        data_msg['poster']['home_url'] = post_msg.poster.home_url
                        data_msg['poster']['img_url'] = post_msg.poster.img_url
                        data_msg['poster']['id'] = post_msg.poster.id
                        data_msg['poster']['name'] = post_msg.poster.name
                        data_msg['poster']['authentication'] = post_msg.poster.authentication
                        data_msg['poster']['birthday'] = post_msg.poster.birthday
                        data_msg['poster']['following'] = post_msg.poster.following
                        data_msg['poster']['follows'] = post_msg.poster.follows
                        data_msg['poster']['intro'] = post_msg.poster.intro
                        data_msg['poster']['level'] = post_msg.poster.level
                        data_msg['poster']['location'] = post_msg.poster.location
                        data_msg['poster']['post_num'] = post_msg.poster.post_num
                    else:
                        data_msg['poster']['home_url'] = ""
                        data_msg['poster']['img_url'] = ""
                        data_msg['poster']['id'] = ""
                        data_msg['poster']['name'] = ""
                        data_msg['poster']['authentication'] = ""
                        data_msg['poster']['birthday'] = ""
                        data_msg['poster']['following'] = ""
                        data_msg['poster']['follows'] = ""
                        data_msg['poster']['intro'] = ""
                        data_msg['poster']['level'] = ""
                        data_msg['poster']['location'] = ""
                        data_msg['poster']['post_num'] = ""
                    print '2222'

                    data.append(data_msg)

                json_out['success'] = True
                json_out['code'] = 0
                json_out['data'] = data

                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
            except:
                print traceback.print_exc()
                json_out['success'] = False
                json_out['code'] = 1
                json_out['data'] = []
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else:
            # print traceback.print_exc()
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")




#添加敏感信息，进行添加
class addSenmsg_add(APIView):
    @csrf_exempt
    def post(self, request, format=None):
        json_out = {}
        json_data=request.data
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
                user_account = user_obj.user_account
                user_group_id = user_obj.user_group_id
                # user_id = json_data['userId']
                topic_id = json_data['postData'][0]['topic_id']
                print topic_id
                #获得topicname
                if topic_id != -1 :
                    try:
                        topic_name = []
                        topic_name_obj = Topic.objects(_id__in=topic_id)
                        print topic_name_obj
                        for topic_name_ in topic_name_obj:
                            topic_name.append(topic_name_.topic_name)
                    except:
                        traceback.print_exc()
                        topic_name = []
                else:
                    topic_name = []

                topic_name = list(set(topic_name))
                # print topic_name



                try:
                    post_id = ObjectId(json_data['postData'][0]['id'])
                except:
                    post_id = ObjectId()

                try:
                    post_obj = Post.objects(_id=post_id).first()
                    post_obj.is_read = 1
                    post_obj.save()
                except:
                    pass
                    
                url = json_data['postData'][0]['url']
                senmsg_find = Sen_message.objects(Q(_id=post_id)).first()
                if senmsg_find:
                    senmsg_find.user_id_list.append(user_id)
                    dup = Sen_message.objects(Q(url=url)&Q(user_id_list=user_id))
                    print '11111111111111111111111111111111111111111111'
                    print len(dup)
                    if len(dup) > 0 :
                        print '11111111111111'
                        json_out['code'] = 1
                        json_out['success'] = False
                        json_out['data'] = '重复添加！'
                        return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
                    
                    senmsg_find.save()
                else:
                    print '222222222222222'

                    title = json_data['postData'][0]['title']
                    content = json_data['postData'][0]['content']
                    pt_time = json_data['postData'][0]['pt_time']

                    dataType = json_data['postData'][0]['dataType']

                    board = json_data['postData'][0]['board']

                    is_report = json_data['postData'][0]['is_report']
                    QQ = json_data['postData'][0]['QQ']
                    cellphone = json_data['postData'][0]['cellphone']
                    Ip = json_data['postData'][0]['Ip']
                    poster = Poster(home_url=json_data['postData'][0]['poster']['home_url'],
                                    id=json_data['postData'][0]['poster']['id'],
                                    img_url=json_data['postData'][0]['poster']['img_url'],
                                    name=json_data['postData'][0]['poster']['name'],
                                    authentication=json_data['postData'][0]['poster']['authentication'],
                                    birthday=json_data['postData'][0]['poster']['birthday'],
                                    following=json_data['postData'][0]['poster']['following'],
                                    follows=json_data['postData'][0]['poster']['follows'],
                                    intro=json_data['postData'][0]['poster']['intro'],
                                    level=json_data['postData'][0]['poster']['level'],
                                    location=json_data['postData'][0]['poster']['location'],
                                    post_num=json_data['postData'][0]['poster']['post_num']
                                    )
                    site_id = json_data['postData'][0]['site_id']
                    site_name =json_data['postData'][0]['site_name']

                    html = json_data['postData'][0]['html'].encode('utf-8')
                    st_time = json_data['postData'][0]['st_time']
                    read_num = json_data['postData'][0]['read_num']
                    comm_num = json_data['postData'][0]['comm_num']
                    img_url = json_data['postData'][0]['img_url']
                    repost_num = json_data['postData'][0]['repost_num']
                    lan_type = json_data['postData'][0]['lan_type']
                    repost_pt_id = json_data['postData'][0]['repost_pt_id']
                    text_type = json_data['postData'][0]['text_type']
                    sen_words = json_data['postData'][0]['senwords']

                    userid_list = []
                    userid_list.append(user_id)




                        # add_msg_bonus = Sen_message.objects(_id=post_id)
                        # if len(add_msg_bonus) > 0:
                        #     add_msg_bonus_obj = add_msg_bonus.first()
                        #     add_msg_bonus_obj.user_id_list.append(user_id)
                            # add_msg_bonus_obj.save()
                        # else:

                    add_msg = Sen_message(
                                        _id=post_id,
                                        url=url,
                                        site_id=site_id,
                                        site_name=site_name,
                                        topic_id=topic_id,
                                        topic_name=topic_name,
                                        board=board,
                                        data_type=dataType,
                                        title=title,
                                        content=content,
                                        html=html,
                                        pt_time=pt_time,
                                        st_time=st_time,
                                        read_num=read_num,
                                        comm_num=comm_num,
                                        img_url=img_url,
                                        repost_num=repost_num,
                                        lan_type=lan_type,
                                        repost_pt_id=repost_pt_id,
                                        text_type=text_type,
                                        poster=poster,
                                        phone_num=cellphone,
                                        user_id_list=userid_list,
                                        qq_num=QQ,
                                        ip_addr=Ip,
                                        sen_words=sen_words,
                                        reporter_id=user_id,
                                        reporter_account=user_account,
                                        reporter_group_id=user_group_id
                                        )


                    add_msg.save()

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
        else:
            # print traceback.print_exc()
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")


#列表导出显示功能
class SenMsgOut(APIView): #/yqdata/senmassage/senmsgout?dataType=-1&endDate=(时间戳)&is_report=-1&pageCounts=all&pageNum=1&startDate=(时间戳)&topicId=-1&userId=1
    @csrf_exempt
    def get(self,request,format=None):
        json_out = {}
        # tokens = "2222222222222222222222"
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']

            user_role_id = User.objects(user_id=user_id).first().user_role_id
            user_group_id = User.objects(user_id=user_id).first().user_group_id

            try:
                # user_id = int(request.GET['userId'])
                try:
                    page_counts = int(request.GET['pageCounts'])  
                except:
                    page_counts = request.GET['pageCounts']  
                page_num = int(request.GET['pageNum'])
                is_report = int(request.GET['is_report'])
                topic_id = int(request.GET['topicId'])
                data_type = int(request.GET['dataType'])

                if request.GET['startDate'] != '""':           
                    timeStart = request.GET['startDate'] + " 00:00:00"
                    start_date = datetime.datetime.strptime(timeStart,"%Y-%m-%d %H:%M:%S")
                else:
                    start_date = request.GET['startDate']

                if request.GET['endDate'] != '""':
                    timeEnd = request.GET['endDate'] + " 00:00:00"
                    end_date = datetime.datetime.strptime(timeEnd,"%Y-%m-%d %H:%M:%S")
                else:
                    end_date = request.GET['endDate']

                print start_date,end_date
                
                data = {}

                #先根据条件筛选出符合的信息，再通过pagecounts和pagenum传给前端指定的部分信息

                if start_date == '""' and end_date == '""':
                    date_filtered_msg = Sen_message.objects()
                elif start_date != '""' and end_date == '""':
                    date_filtered_msg = Sen_message.objects(Q(pt_time__gte=start_date))
                elif start_date == '""' and end_date != '""':
                    date_filtered_msg = Sen_message.objects(Q(pt_time__lte=end_date))
                else:
                    date_filtered_msg = Sen_message.objects(Q(pt_time__lte=end_date) & Q(pt_time__gte=start_date))
                date_count0 = len(date_filtered_msg)
                print "date_count0:",date_count0
                
                if user_role_id==2:
                    userid_res=User.objects(Q(user_group_id=user_group_id)).only('user_id')
                    userid_list=[i.user_id for i in userid_res]                    
                    date_filtered_msg = date_filtered_msg((Q(user_id_list__in=userid_list) & Q(is_report=1)) | (Q(user_id_list=user_id)))
                elif user_role_id==1:
                    print 'yuqing'
                    date_filtered_msg = date_filtered_msg(Q(user_id_list=user_id))
                else:
                    print 'admin'
                    date_filtered_msg = date_filtered_msg(Q(is_report=1) | Q(user_id_list=user_id))
                #已经得到根据时间筛选，降序排列               

                if is_report != -1:
                    if topic_id == -1 and data_type == -1 :
                        all_filtered_msg = date_filtered_msg(is_report=is_report).order_by('-add_time')
                    elif topic_id != -1 and data_type == -1:
                        all_filtered_msg = date_filtered_msg(is_report=is_report,topic_id=topic_id).order_by('-add_time')
                    elif topic_id == -1 and data_type != -1:
                        all_filtered_msg = date_filtered_msg(is_report=is_report,data_type=data_type).order_by('-add_time')
                    else:
                        all_filtered_msg = date_filtered_msg(is_report=is_report,data_type=data_type,topic_id=topic_id).order_by('-add_time')
                else:
                    if topic_id == -1 and data_type == -1 :
                        all_filtered_msg = date_filtered_msg().order_by('-add_time')
                    elif topic_id != -1 and data_type == -1:
                        all_filtered_msg = date_filtered_msg(topic_id=topic_id).order_by('-add_time')
                    elif topic_id == -1 and data_type != -1:
                        all_filtered_msg = date_filtered_msg(data_type=data_type).order_by('-add_time')
                    else:
                        all_filtered_msg = date_filtered_msg(data_type=data_type,topic_id=topic_id).order_by('-add_time')


                #已经筛选出全部需要的
                totalCount = len(all_filtered_msg)
                print totalCount
                data['totalCount'] = totalCount
                if page_counts == "all":
                    totalPage = 0
                    data['totalPage'] = totalPage
                    postData = []

                    for page_filtered_msg in all_filtered_msg:
                        postData_json = {}
                        postData_json['id'] = str(page_filtered_msg._id)
                        postData_json['url'] = page_filtered_msg.url
                        postData_json['content'] = page_filtered_msg.content
                        postData_json['pt_time'] = page_filtered_msg.pt_time
                        postData_json['data_type'] = page_filtered_msg.data_type
                        postData_json['board'] = page_filtered_msg.board
                        postData_json['add_time'] = page_filtered_msg.add_time
                        postData_json['is_report'] = page_filtered_msg.is_report
                        postData_json['site_id'] = page_filtered_msg.site_id
                        postData_json['site_name'] = page_filtered_msg.site_name
                        postData_json['topic_id'] = page_filtered_msg.topic_id
                        postData_json['html'] = str(page_filtered_msg.html.grid_id)
                        postData_json['st_time'] = page_filtered_msg.st_time
                        postData_json['read_num'] = page_filtered_msg.read_num
                        postData_json['comm_num'] = page_filtered_msg.comm_num
                        postData_json['img_url'] = page_filtered_msg.img_url
                        postData_json['repost_num'] = page_filtered_msg.repost_num
                        postData_json['lan_type'] = page_filtered_msg.lan_type
                        postData_json['repost_pt_id'] = page_filtered_msg.repost_pt_id
                        postData_json['text_type'] = page_filtered_msg.text_type
                        postData_json['poster'] = {}
                        postData_json['ip_addr'] = page_filtered_msg.ip_addr
                        postData_json['qq_num'] = page_filtered_msg.qq_num
                        postData_json['phone_num'] = page_filtered_msg.phone_num
                        postData_json['is_report'] = page_filtered_msg.is_report
                        postData_json['title'] = page_filtered_msg.title
                        postData_json['senwords'] = page_filtered_msg.sen_words
                        postData_json['user_name_list']  = [i.user_account for i in User.objects(Q(user_id__in = page_filtered_msg.user_id_list))]


                        postData_json['poster']['home_url'] = page_filtered_msg.poster.home_url
                        postData_json['poster']['img_url'] = page_filtered_msg.poster.img_url
                        postData_json['poster']['id'] = page_filtered_msg.poster.id
                        postData_json['poster']['name'] = page_filtered_msg.poster.name
                        try:
                            postData_json['poster']['authentication'] = page_filtered_msg.poster.authentication
                            postData_json['poster']['birthday'] = page_filtered_msg.poster.birthday
                            postData_json['poster']['following'] = page_filtered_msg.poster.following
                            postData_json['poster']['follows'] = page_filtered_msg.poster.follows
                            postData_json['poster']['intro'] = page_filtered_msg.poster.intro
                            postData_json['poster']['level'] = page_filtered_msg.poster.level
                            postData_json['poster']['location'] = page_filtered_msg.poster.location
                            postData_json['poster']['post_num'] = page_filtered_msg.poster.post_num
                        except:
                            print traceback.print_exc()
                            postData_json['poster']['authentication'] = ""
                            postData_json['poster']['birthday'] = ""
                            postData_json['poster']['following'] = ""
                            postData_json['poster']['follows'] = ""
                            postData_json['poster']['intro'] = ""
                            postData_json['poster']['level'] = ""
                            postData_json['poster']['location'] = ""
                            postData_json['poster']['post_num'] = ""

                        postData.append(postData_json)
                else:
                    totalPage = totalCount / page_counts + 1
                    data['totalPage'] = totalPage

                    postData = []
                    #计算一页中开始与结束的信息序号
                    start_msg_num = (page_num - 1) * page_counts + 1
                    print start_msg_num
                    end_msg_num = page_num * page_counts

                    if end_msg_num > totalCount:
                        end_msg_num = totalCount

                    for page_filtered_msg in all_filtered_msg[start_msg_num - 1 : end_msg_num]:
                        postData_json = {}
                        postData_json['id'] = str(page_filtered_msg._id)
                        postData_json['url'] = page_filtered_msg.url
                        postData_json['content'] = page_filtered_msg.content
                        postData_json['pt_time'] = page_filtered_msg.pt_time
                        postData_json['data_type'] = page_filtered_msg.data_type
                        postData_json['board'] = page_filtered_msg.board
                        postData_json['add_time'] = page_filtered_msg.add_time
                        postData_json['is_report'] = page_filtered_msg.is_report
                        postData_json['site_id'] = page_filtered_msg.site_id
                        postData_json['site_name'] = page_filtered_msg.site_name
                        postData_json['topic_id'] = page_filtered_msg.topic_id
                        postData_json['html'] = str(page_filtered_msg.html.grid_id)
                        postData_json['st_time'] = page_filtered_msg.st_time
                        postData_json['read_num'] = page_filtered_msg.read_num
                        postData_json['comm_num'] = page_filtered_msg.comm_num
                        postData_json['img_url'] = page_filtered_msg.img_url
                        postData_json['repost_num'] = page_filtered_msg.repost_num
                        postData_json['lan_type'] = page_filtered_msg.lan_type
                        postData_json['repost_pt_id'] = page_filtered_msg.repost_pt_id
                        postData_json['text_type'] = page_filtered_msg.text_type
                        postData_json['poster'] = {}
                        postData_json['ip_addr'] = page_filtered_msg.ip_addr
                        postData_json['qq_num'] = page_filtered_msg.qq_num
                        postData_json['phone_num'] = page_filtered_msg.phone_num
                        postData_json['is_report'] = page_filtered_msg.is_report
                        postData_json['title'] = page_filtered_msg.title
                        postData_json['senwords'] = page_filtered_msg.sen_words
                        postData_json['user_name_list']  = [i.user_account for i in User.objects(Q(user_id__in = page_filtered_msg.user_id_list))]


                        postData_json['poster']['home_url'] = page_filtered_msg.poster.home_url
                        postData_json['poster']['img_url'] = page_filtered_msg.poster.img_url
                        postData_json['poster']['id'] = page_filtered_msg.poster.id
                        postData_json['poster']['name'] = page_filtered_msg.poster.name
                        try:
                            postData_json['poster']['authentication'] = page_filtered_msg.poster.authentication
                            postData_json['poster']['birthday'] = page_filtered_msg.poster.birthday
                            postData_json['poster']['following'] = page_filtered_msg.poster.following
                            postData_json['poster']['follows'] = page_filtered_msg.poster.follows
                            postData_json['poster']['intro'] = page_filtered_msg.poster.intro
                            postData_json['poster']['level'] = page_filtered_msg.poster.level
                            postData_json['poster']['location'] = page_filtered_msg.poster.location
                            postData_json['poster']['post_num'] = page_filtered_msg.poster.post_num
                        except:
                            print traceback.print_exc()
                            postData_json['poster']['authentication'] = ""
                            postData_json['poster']['birthday'] = ""
                            postData_json['poster']['following'] = ""
                            postData_json['poster']['follows'] = ""
                            postData_json['poster']['intro'] = ""
                            postData_json['poster']['level'] = ""
                            postData_json['poster']['location'] = ""
                            postData_json['poster']['post_num'] = ""

                        postData.append(postData_json)

                data['postData'] = postData

                json_out['success'] = True
                json_out['code'] = 0
                json_out['data'] = data

                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
            except:
                print traceback.print_exc()
                json_out['success'] = False
                json_out['code'] = 1
                json_out['data'] = []
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else:
            # print traceback.print_exc()
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")


#列表显示功能
class showSenMsg(APIView):
    @csrf_exempt
    def get(self,request,format=None):
        json_out = {}
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']

            user_role_id = User.objects(user_id=user_id).first().user_role_id
            user_group_id = User.objects(user_id=user_id).first().user_group_id


            try:
                # user_id = int(request.GET['userId'])
                try:
                    page_counts = int(request.GET['pageCounts'])  
                except:
                    page_counts = request.GET['pageCounts']  
                page_num = int(request.GET['pageNum'])
                is_report = int(request.GET['is_report'])
                topic_id = int(request.GET['topicId'])
                data_type = int(request.GET['dataType'])

                if request.GET['startDate'] != '""':           
                    timeStart = request.GET['startDate'] + " 00:00:00"
                    start_date = datetime.datetime.strptime(timeStart,"%Y-%m-%d %H:%M:%S")
                else:
                    start_date = request.GET['startDate']

                if request.GET['endDate'] != '""':
                    timeEnd = request.GET['endDate'] + " 00:00:00"
                    end_date = datetime.datetime.strptime(timeEnd,"%Y-%m-%d %H:%M:%S")
                else:
                    end_date = request.GET['endDate']

                print start_date,end_date

                data = {}
                print is_report

                #先根据条件筛选出符合的信息，再通过pagecounts和pagenum传给前端指定的部分信息

                if start_date == '""' and end_date == '""':
                    date_filtered_msg = Sen_message.objects()
                elif start_date != '""' and end_date == '""':
                    date_filtered_msg = Sen_message.objects(Q(pt_time__gte=start_date))
                elif start_date == '""' and end_date != '""':
                    date_filtered_msg = Sen_message.objects(Q(pt_time__lte=end_date))
                else:
                    date_filtered_msg = Sen_message.objects(Q(pt_time__lte=end_date) & Q(pt_time__gte=start_date))
                date_count0 = len(date_filtered_msg)
                print "date_count0:",date_count0
                
                if user_role_id==2:
                    userid_res=User.objects(Q(user_group_id=user_group_id)).only('user_id')
                    userid_list=[i.user_id for i in userid_res]                    
                    date_filtered_msg = date_filtered_msg((Q(user_id_list__in=userid_list) & Q(is_report=1)) | (Q(user_id_list=user_id)))
                    # date_filtered_msg = Sen_message.objects((Q(user_id_list__in=userid_list) & Q(is_report=1)) | (Q(user_id_list=user_id)))
                    # date_filtered_msg = Sen_message.objects((Q(user_id_list__in=userid_list)| (Q(user_id_list=user_id))))
                elif user_role_id==1:
                    print 'yuqing'
                    date_filtered_msg = date_filtered_msg(Q(user_id_list=user_id))
                    # date_filtered_msg = Sen_message.objects(Q(user_id_list=user_id))
                    # for d in date_filtered_msg:
                    #     print d
                else:
                    print 'admin'
                    date_filtered_msg = date_filtered_msg(Q(is_report=1) | Q(user_id_list=user_id))
                    # date_filtered_msg = Sen_message.objects(Q(is_report=1) | Q(user_id_list=user_id))
                #已经得到根据时间筛选，降序排列               

                if is_report != -1:
                    if topic_id == -1 and data_type == -1 :
                        all_filtered_msg = date_filtered_msg(is_report=is_report).order_by('-add_time')
                    elif topic_id != -1 and data_type == -1:
                        all_filtered_msg = date_filtered_msg(is_report=is_report,topic_id=topic_id).order_by('-add_time')
                    elif topic_id == -1 and data_type != -1:
                        all_filtered_msg = date_filtered_msg(is_report=is_report,data_type=data_type).order_by('-add_time')
                    else:
                        all_filtered_msg = date_filtered_msg(is_report=is_report,data_type=data_type,topic_id=topic_id).order_by('-add_time')
                else:
                    if topic_id == -1 and data_type == -1 :
                        all_filtered_msg = date_filtered_msg().order_by('-add_time')
                    elif topic_id != -1 and data_type == -1:
                        all_filtered_msg = date_filtered_msg(topic_id=topic_id).order_by('-add_time')
                    elif topic_id == -1 and data_type != -1:
                        all_filtered_msg = date_filtered_msg(data_type=data_type).order_by('-add_time')
                    else:
                        all_filtered_msg = date_filtered_msg(data_type=data_type,topic_id=topic_id).order_by('-add_time')

                # if user_role_id == 1:
                    
                #     all_filtered_msg = all_filtered_msg(reporter_id=user_id)


                # elif user_role_id == 2:

                #     all_filtered_msg = all_filtered_msg(reporter_group_id=reporter_group_id)

                # else:
                #     pass

                #已经筛选出全部需要的
                totalCount = len(all_filtered_msg)
                print "totalCount:",totalCount
                data['totalCount'] = totalCount
                if page_counts == "all":
                    totalPage = 0
                    data['totalPage'] = totalPage
                    postData = []

                    for page_filtered_msg in all_filtered_msg:
                        postData_json = {}
                        postData_json['id'] = str(page_filtered_msg._id)
                        postData_json['url'] = page_filtered_msg.url
                        postData_json['content'] = page_filtered_msg.content
                        postData_json['user_id_list'] = page_filtered_msg.user_id_list
                        postData_json['user_name_list']  = [i.user_account for i in User.objects(Q(user_id__in = page_filtered_msg.user_id_list))]
                        postData_json['pt_time'] = page_filtered_msg.pt_time
                        postData_json['data_type'] = page_filtered_msg.data_type
                        postData_json['board'] = page_filtered_msg.board
                        postData_json['add_time'] = page_filtered_msg.add_time
                        postData_json['is_report'] = page_filtered_msg.is_report
                        postData_json['site_id'] = page_filtered_msg.site_id
                        postData_json['site_name'] = page_filtered_msg.site_name
                        postData_json['topic_id'] = page_filtered_msg.topic_id
                        postData_json['html'] = str(page_filtered_msg.html.grid_id)
                        postData_json['st_time'] = page_filtered_msg.st_time
                        postData_json['read_num'] = page_filtered_msg.read_num
                        postData_json['comm_num'] = page_filtered_msg.comm_num
                        postData_json['img_url'] = page_filtered_msg.img_url
                        postData_json['repost_num'] = page_filtered_msg.repost_num
                        postData_json['lan_type'] = page_filtered_msg.lan_type
                        postData_json['repost_pt_id'] = page_filtered_msg.repost_pt_id
                        postData_json['text_type'] = page_filtered_msg.text_type
                        postData_json['poster'] = {}
                        postData_json['ip_addr'] = page_filtered_msg.ip_addr
                        postData_json['qq_num'] = page_filtered_msg.qq_num
                        postData_json['phone_num'] = page_filtered_msg.phone_num
                        postData_json['is_report'] = page_filtered_msg.is_report
                        postData_json['title'] = page_filtered_msg.title
                        postData_json['senwords'] = page_filtered_msg.sen_words
                        postData_json['reporter_id'] = page_filtered_msg.reporter_id
                        postData_json['reporter_account'] = page_filtered_msg.reporter_account
                        postData_json['reporter_group_id'] = page_filtered_msg.reporter_group_id

                        postData_json['poster']['home_url'] = page_filtered_msg.poster.home_url
                        postData_json['poster']['img_url'] = page_filtered_msg.poster.img_url
                        postData_json['poster']['id'] = page_filtered_msg.poster.id
                        postData_json['poster']['name'] = page_filtered_msg.poster.name
                        postData_json['poster']['authentication'] = page_filtered_msg.poster.authentication
                        postData_json['poster']['birthday'] = page_filtered_msg.poster.birthday
                        postData_json['poster']['following'] = page_filtered_msg.poster.following
                        postData_json['poster']['follows'] = page_filtered_msg.poster.follows
                        postData_json['poster']['intro'] = page_filtered_msg.poster.intro
                        postData_json['poster']['level'] = page_filtered_msg.poster.level
                        postData_json['poster']['location'] = page_filtered_msg.poster.location
                        postData_json['poster']['post_num'] = page_filtered_msg.poster.post_num


                        postData.append(postData_json)

                else:
                    totalPage = totalCount / page_counts + 1
                    data['totalPage'] = totalPage

                    postData = []
                    #计算一页中开始与结束的信息序号
                    start_msg_num = (page_num - 1) * page_counts + 1
                    print start_msg_num
                    end_msg_num = page_num * page_counts

                    if end_msg_num > totalCount:
                        end_msg_num = totalCount

                    for page_filtered_msg in all_filtered_msg[start_msg_num - 1 : end_msg_num]:
                        postData_json = {}
                        postData_json['id'] = str(page_filtered_msg._id)
                        postData_json['url'] = page_filtered_msg.url
                        postData_json['content'] = page_filtered_msg.content
                        postData_json['user_id_list'] = page_filtered_msg.user_id_list
                        postData_json['user_name_list']  = [i.user_account for i in User.objects(Q(user_id__in = page_filtered_msg.user_id_list))]
                        postData_json['pt_time'] = page_filtered_msg.pt_time
                        postData_json['data_type'] = page_filtered_msg.data_type
                        postData_json['board'] = page_filtered_msg.board
                        postData_json['add_time'] = page_filtered_msg.add_time
                        postData_json['is_report'] = page_filtered_msg.is_report
                        postData_json['site_id'] = page_filtered_msg.site_id
                        postData_json['site_name'] = page_filtered_msg.site_name
                        postData_json['topic_id'] = page_filtered_msg.topic_id
                        postData_json['html'] = str(page_filtered_msg.html.grid_id)
                        postData_json['st_time'] = page_filtered_msg.st_time
                        postData_json['read_num'] = page_filtered_msg.read_num
                        postData_json['comm_num'] = page_filtered_msg.comm_num
                        postData_json['img_url'] = page_filtered_msg.img_url
                        postData_json['repost_num'] = page_filtered_msg.repost_num
                        postData_json['lan_type'] = page_filtered_msg.lan_type
                        postData_json['repost_pt_id'] = page_filtered_msg.repost_pt_id
                        postData_json['text_type'] = page_filtered_msg.text_type
                        postData_json['poster'] = {}
                        postData_json['ip_addr'] = page_filtered_msg.ip_addr
                        postData_json['qq_num'] = page_filtered_msg.qq_num
                        postData_json['phone_num'] = page_filtered_msg.phone_num
                        postData_json['is_report'] = page_filtered_msg.is_report
                        postData_json['title'] = page_filtered_msg.title            
                        postData_json['poster']['home_url'] = page_filtered_msg.poster.home_url
                        postData_json['poster']['img_url'] = page_filtered_msg.poster.img_url
                        postData_json['poster']['id'] = page_filtered_msg.poster.id
                        postData_json['poster']['name'] = page_filtered_msg.poster.name
                        postData_json['poster']['authentication'] = page_filtered_msg.poster.authentication
                        postData_json['poster']['birthday'] = page_filtered_msg.poster.birthday
                        postData_json['poster']['following'] = page_filtered_msg.poster.following
                        postData_json['poster']['follows'] = page_filtered_msg.poster.follows
                        postData_json['poster']['intro'] = page_filtered_msg.poster.intro
                        postData_json['poster']['level'] = page_filtered_msg.poster.level
                        postData_json['poster']['location'] = page_filtered_msg.poster.location
                        postData_json['poster']['post_num'] = page_filtered_msg.poster.post_num
                        postData_json['senwords'] = page_filtered_msg.sen_words
                        postData_json['reporter_id'] = page_filtered_msg.reporter_id
                        postData_json['reporter_account'] = page_filtered_msg.reporter_account
                        postData_json['reporter_group_id'] = page_filtered_msg.reporter_group_id

                        postData.append(postData_json)

                data['postData'] = postData

                json_out['success'] = True
                json_out['code'] = 0
                json_out['data'] = data

                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
            except:
                print traceback.print_exc()
                json_out['success'] = False
                json_out['code'] = 1
                json_out['data'] = []
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else:
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
#列表元数据信息功能
class showRawMsg(APIView):
    @csrf_exempt
    def get(self,request,format=None):
        # user_id = int(request.GET['userId'])
        post_id = request.GET['id']
        json_out = {}
        a = ObjectId(post_id)
        print a
        print type(a)
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
                data_msg = {}
                #从post表取出
                post_msg = Sen_message.objects(_id=a).first()
                print '11111'
                # for post_msg in post_msgs:
                print post_msg.url
                print post_msg.title
                print post_msg.html.grid_id
                data_msg['id'] = str(a)
                data_msg['url'] = post_msg.url
                print '333'
                data_msg['title'] = post_msg.title
                data_msg['content'] = post_msg.content
                data_msg['pt_time'] = post_msg.pt_time
                data_msg['dataType'] = post_msg.data_type
                data_msg['board'] = post_msg.board
                data_msg['st_time'] = post_msg.st_time
                data_msg['is_report'] = ''
                data_msg['qq_num'] = post_msg.qq_num
                data_msg['cellphone'] = ''
                data_msg['Ip'] = ''
                data_msg['poster'] = {}
                data_msg['site_id'] = post_msg.site_id
                data_msg['site_name'] = post_msg.site_name
                data_msg['topic_id'] = post_msg.topic_id
                data_msg['html'] = str(post_msg.html.grid_id)
                data_msg['st_time'] = post_msg.st_time
                data_msg['read_num'] = post_msg.read_num
                data_msg['comm_num'] = post_msg.comm_num
                data_msg['img_url'] = post_msg.img_url
                data_msg['repost_num'] = post_msg.repost_num
                data_msg['lan_type'] = post_msg.lan_type
                data_msg['repost_pt_id'] = post_msg.repost_pt_id
                data_msg['text_type'] = post_msg.text_type
                data_msg['senwords'] = post_msg.sen_words
                data_msg['poster']['home_url'] = post_msg.poster.home_url
                data_msg['poster']['img_url'] = post_msg.poster.img_url
                data_msg['poster']['id'] = post_msg.poster.id
                data_msg['poster']['name'] = post_msg.poster.name
                data_msg['poster']['authentication'] = post_msg.poster.authentication
                data_msg['poster']['birthday'] = post_msg.poster.birthday
                data_msg['poster']['following'] = post_msg.poster.following
                data_msg['poster']['follows'] = post_msg.poster.follows
                data_msg['poster']['intro'] = post_msg.poster.intro
                data_msg['poster']['level'] = post_msg.poster.level
                data_msg['poster']['location'] = post_msg.poster.location
                data_msg['poster']['post_num'] = post_msg.poster.post_num
                print '2222'

                data.append(data_msg)

                json_out['success'] = True
                json_out['code'] = 0
                json_out['data'] = data

                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
            except:
                print traceback.print_exc()
                json_out['success'] = False
                json_out['code'] = 1
                json_out['data'] = []
                return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else:
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")

class Mesg_delete(APIView):
    @csrf_exempt
    def post(self, request, format=None):
        json_data=request.data
        # userid=int(json_data['userId'])
        listid=json_data['postLists']
        json_out={}
        data={}
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']
            try:
                for smesgid in listid:
                    mesgid=ObjectId(smesgid)
                    mesg=Sen_message.objects(Q(_id=mesgid)).first()
                    if len(mesg.user_id_list)==1:
                        mesg.delete()
                        post_obj = Post.objects(_id=mesgid).first()
                        post_obj.is_read = 0
                        post_obj.save()
                    else:
                        temp=mesg.user_id_list.remove(user_id)
                        mesg.user_id_list=temp
                        mesg.save()
                data['message']=u'删除成功！'
                json_out['code']=0
                json_out['success']=True
                json_out['data']=data
            except:
                traceback.print_exc()
                json_out['code']=1
                json_out['success']=False
                data['message']=u'删除失败！'
                json_out['data']={}

            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else:
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")


class Mesg_mark_report(APIView):
    @csrf_exempt
    def post(self, request, format=None):
        json_data=request.data
        # userid=int(json_data['userId'])
        listid=json_data['postLists']
        json_out={}
        data={}
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']
            try:
                for smesgid in listid:
                    mesgid=ObjectId(smesgid)
                    mesg=Sen_message.objects(Q(_id=mesgid)).first()
                    mesg.is_report=1
                    mesg.save()
                data['message']=u'标记成功！'
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
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")


class Mesg_mark_handle(APIView):
    @csrf_exempt
    def post(self, request, format=None):
        json_data=request.data
        # userid=int(json_data['userId'])
        listid=json_data['postLists']
        json_out={}
        data={}
        tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
        time_stamp = tokens[-13:-3]

        if abs(int(time_stamp)-int(time.time())) < 60:

            tokens = re.sub(r'#.*#.*','',tokens)
            # tokens = json_data['userid']
            pld = Auth.decode_auth_token(tokens)

            user_id = pld['data']['id']
            login_time = pld['data']['login_time']
            try:
                for smesgid in listid:
                    mesgid=ObjectId(smesgid)
                    mesg=Sen_message.objects(Q(_id=mesgid)).first()
                    mesg.is_report=2
                    mesg.save()
                data['message']=u'标记成功！'
                json_out['code']=0
                json_out['success']=True
                json_out['data']=data
            except:
                traceback.print_exc()
                json_out['code']=1
                json_out['success']=True
                json_out['data']={}

            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
        else:
            json_out['code'] = 1
            json_out['success'] = False
            json_out['data'] = '认证失败'
            return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
















