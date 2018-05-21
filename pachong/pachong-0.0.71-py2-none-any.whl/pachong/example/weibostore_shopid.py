#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/22/18
# @File  : [pachong] weibostore_shopid.py


from __future__ import absolute_import
from __future__ import unicode_literals

from pachong.crawler.taobao import Taobao
from pachong.database.mongodb import MongoDB
from pachong.fetcher import Requests
import sys

# i_file = int(sys.argv[1])

project = 'wanghong'
# project = 'test'
input_ = 'taobaodianzhu'
fetcher = Requests()
# crawler = Taobao(project, input_, fetcher=fetcher, Database=MongoDB).import_input('wu{}.json'.format(i_file), is_json=True)
crawler = Taobao(project, input_, fetcher=fetcher, Database=MongoDB)
crawler.crawl('shopid_from_weibostore')
