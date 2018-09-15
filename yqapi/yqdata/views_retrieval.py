# -*-coding:utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from yqdata.models import Poster, Post, Topic, Site_topic, Site, Datatype_name, Sen_message, User
from datetime import date, timedelta
import datetime
from rest_framework.views import APIView
import traceback
import time
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
import random
from mongoengine import *
import json
import logging
from datetime import datetime
from elasticsearch import Elasticsearch
import base64,re
from yqdata.Auths import *
class search():
	def __init__(self,elastic,page,sort,page_num):
		self.es = Elasticsearch(["114.215.47.173"])
		self._query = {
		"query":elastic,
		"highlight": {
		  	"pre_tags": ["<em class=\"hlt1\">"],
		  	"post_tags": ["</em>"],
		  	"fields": {
		    "title": {},
		    "board": {}
		  	}
		},
		"from":0 + page*10,
		"size":page_num,
		"sort":[{sort:{"order":"desc"}}]
		}
		self.index = 'test-index'

	def searchByquery(self):
		_searched = self.es.search(index=self.index, doc_type='post', body=self._query)
		results = []
		for hit in _searched['hits']['hits']:
			results.append(hit['_source'])
		total = _searched['hits']['total']
		return results,total

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

class Advanced_Retrieval(APIView):
	@csrf_exempt    
	def post(self, request, format=None):
		json_out = {}
		json_data = request.data
		tokens = decode_base64(request.META.get('HTTP_AUTHORIZATION'))
		time_stamp = tokens[-13:-3]
		sortname = ["pt_time","pt_time","site_id","topic_id","name"]

		if abs(int(time_stamp)-int(time.time())) < 60:
			try:
				tokens = re.sub(r'#.*#.*','',tokens)
				# tokens = json_data['userid']
				pld = Auth.decode_auth_token(tokens)
				userid = int(pld['data']['id'])
				login_time = pld['data']['login_time']
				
				elastic = json_data["elastic"]
				page = json_data["page"]
				page_num = json_data["page_num"]
				sort = int(json_data["sort"])
				# userId = json_data["userId"]
				elastic = elastic.replace('\r\n', '')
				elastic = elastic.replace('board_id','data_type')
				user_es  = ',{"terms":{"user_id_list":[' + str(userid) + ']}}'
				elastic = elastic[:-3]
				elastic = elastic + user_es + ']}}'
				print elastic
				elastic = json.JSONDecoder().decode(elastic)
				s = search(elastic,page-1,sortname[sort],page_num)
				results,total = s.searchByquery()
				json_out['code'] = 0
				json_out['success'] = True
				result = {'post_count':total,'post_data':results}
				json_out['data'] = result
			except:
				traceback.print_exc()
				json_out['code']=1
				json_out['success']=False
				json_out['data']={}
			return HttpResponse(json.dumps(json_out),content_type="application/json")

		else:
		    json_out['code'] = 1
		    json_out['data'] = {}
		    json_out['success'] = False
		    return HttpResponse(json.dumps(json_out, cls=MyEncoder),content_type="application/json")
