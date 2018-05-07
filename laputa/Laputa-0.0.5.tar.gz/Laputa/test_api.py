#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re,yaml,random
import unittest
from requests import Request,Session
null=None
reponses={}
class interface(unittest.TestCase):

	#create china world
	def create_Unicode(self,num=None):
		if num!=None:
			return ''.join(chr(random.randint(0x4e00, 0x9fbf)) for _ in range(3))
		else:
			return ''.join(chr(random.randint(0x4e00, 0x9fbf)) for _ in range(int(num)))

	# create user_name
	def create_user_name(self):
		return ''.join(chr(random.choice(range(97, 122))) for _ in range(8))

	#create email
	def create_email(self):
		maillist = ["@qq.mmdminterface", "@gmail.mmdminterface", "@sina.mmdminterface"]
		return ''.join( chr(random.choice(range(97,122))) for _ in range(8))+random.choice(maillist)

	#create phone number
	def create_pn(self):
		pholist = ["130", "131", "132", "133", "134", "135", "136", "137", "138", "139", "147", "150", "151", "152",
				   "153", "155", "156", "157", "158", "159", "186", "187", "188"]
		return random.choice(pholist) +''.join( str(random.choice(range(10))) for _ in range(8))

	def save_params(self, text, rule):

		for i in rule.keys():
			rep = re.compile(rule[i])
			reponses[i] = rep.findall(text)[0]
		return reponses

	def read_yaml(self,file):
		with open(file, 'r', encoding='utf-8') as f:
			cont = f.read()
			self.urls = yaml.load(cont)['hostname']
			return yaml.load(cont)['users']



	def parse_params(self, value):
		value = str(value)
		reps = re.compile('\'(\$\{.*?\})\'')
		keys = reps.findall(value)
		for key in keys:
			value = value.replace(key, reponses[key[2:-1]])
		value = eval(value)
		return value

	def Session(self,method,url,user_id=None,params=None,json=None,url_id=None):
		if user_id==None:
			user_id=Session()
		if url_id==None:
			try:
				url=self.urls[0]+url
			except:
				url=url
		else:
			url=self.urls[url_id]+url
		if params==None and json==None:
			req=Request(method,url)
		elif params==None:
			req=Request(method,url,json=json)
		elif json==None:
			req=Request(method,url,params=params)
		else:
			req=Request(method,url,params=params,json=json)
		prepped = user_id.prepare_request(req)
		return user_id.send(prepped)
	def tearDown(self):
		pass