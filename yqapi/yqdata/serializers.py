#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2016 Baidu.com, Inc. All Rights Reserved
#
########################################################################

"""
File: serializers.py
Author: minus(minus@baidu.com)
Date: 2016/12/29 20:03:49
"""

from rest_framework_mongoengine.serializers import DocumentSerializer
from models import Post

class PostSerializer(DocumentSerializer):
    class Meta:
        model = Post
        fields = ('_id', 'url', 'site_id', 'site_name', 'topic_id', 'board', 'data_type', 'title', 'content', 'pt_time', 'st_time', 'read_num', 'comm_num', 'img_url', 'repost_num', 'lan_type', 'is_read', 'poster')
#        depth = 2

