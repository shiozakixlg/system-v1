# -*-coding:utf-8 -*-

#https://github.com/django-json-api/django-rest-framework-json-api/blob/develop/rest_framework_json_api/views.py
#http://django-rest-framework-json-api.readthedocs.io/en/stable/getting-started.html#running-the-example-app

from yqdata.models import Post, Topic, Site_topic
from serializers import PostSerializer
from rest_framework.views import APIView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from mongoengine import *
from mongoengine.queryset.visitor import Q

import json
import traceback
import base64,re
from yqdata.Auths import *
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


# connect('yuqing', alias='default', host='117.32.155.62', port=10005, username='yuqing', password='yuqing')
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
		post_content= re.sub(r'n{2,}t{2,}|t{1,}n{1,}t{1,}|n{1,}t{2,}n{1,}', '', post_content)
	post_dict['content'] = post_content.decode('utf-8')[:50].encode('utf-8')
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




class Search(APIView):
	@csrf_exempt
	def post(self, request, format=None):
		json_out = {}
		try:
			data_list = []
			self.get_posts(data_list)

			json_out['data'] = data_list
			json_out['code'] = 0
			json_out['success'] = True
		except:
			traceback.print_exc()
			json_out['code'] = 1
			json_out['data'] = []
			json_out['success'] = False

		return HttpResponse(json.dumps(json_out, cls=MyEncoder), content_type="application/json")



	def get_posts(self, data_list):
		posts_ = Post.objects(topic_id=9)[:10]
		count = posts_.count()
		if count > 0:
			for post in posts_:
				post_dict = {}
				PostDict(post_dict, post)
				data_list.append(post_dict)
		else:
			data_list = []

