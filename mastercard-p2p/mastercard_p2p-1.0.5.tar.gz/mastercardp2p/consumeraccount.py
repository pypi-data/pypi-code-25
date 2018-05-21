#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2016 MasterCard International Incorporated
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list of
# conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of
# conditions and the following disclaimer in the documentation and/or other materials
# provided with the distribution.
# Neither the name of the MasterCard International Incorporated nor the names of its
# contributors may be used to endorse or promote products derived from this software
# without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#


from __future__ import absolute_import
from mastercardapicore import BaseObject
from mastercardapicore import RequestMap
from mastercardapicore import OperationConfig
from mastercardapicore import OperationMetadata
from mastercardp2p import ResourceConfig

class ConsumerAccount(BaseObject):
	"""
	
	"""

	__config = {
		
		"cb113dbb-8e56-442e-915b-71afb35ce554" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/accounts", "create", [], []),
		
		"b4bf9c64-6286-4d43-9562-07486d1f2fee" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/accounts/{accountId}", "delete", [], []),
		
		"95f1f7a2-9440-40de-a06b-ad3f298520fc" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/accounts/{accountId}", "read", [], []),
		
		"8e057c8e-a164-4909-ae3d-14b99c061c02" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/accounts", "query", [], ["ref"]),
		
		"c27d6418-691c-412c-85e1-24ecc1571ea2" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/accounts/{accountId}", "update", [], []),
		
	}

	def getOperationConfig(self,operationUUID):
		if operationUUID not in self.__config:
			raise Exception("Invalid operationUUID: "+operationUUID)

		return self.__config[operationUUID]

	def getOperationMetadata(self):
		return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())


	@classmethod
	def create(cls,mapObj):
		"""
		Creates object of type ConsumerAccount

		@param Dict mapObj, containing the required parameters to create a new object
		@return ConsumerAccount of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("cb113dbb-8e56-442e-915b-71afb35ce554", ConsumerAccount(mapObj))









	@classmethod
	def deleteById(cls,id,map=None):
		"""
		Delete object of type ConsumerAccount by id

		@param str id
		@return ConsumerAccount of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""

		mapObj =  RequestMap()
		if id:
			mapObj.set("id", id)

		if map:
			if (isinstance(map,RequestMap)):
				mapObj.setAll(map.getObject())
			else:
				mapObj.setAll(map)

		return BaseObject.execute("b4bf9c64-6286-4d43-9562-07486d1f2fee", ConsumerAccount(mapObj))

	def delete(self):
		"""
		Delete object of type ConsumerAccount

		@return ConsumerAccount of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("b4bf9c64-6286-4d43-9562-07486d1f2fee", self)







	@classmethod
	def readByID(cls,id,criteria=None):
		"""
		Returns objects of type ConsumerAccount by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of ConsumerAccount
		@raise ApiException: raised an exception from the response status
		"""
		mapObj =  RequestMap()
		if id:
			mapObj.set("id", id)

		if criteria:
			if (isinstance(criteria,RequestMap)):
				mapObj.setAll(criteria.getObject())
			else:
				mapObj.setAll(criteria)

		return BaseObject.execute("95f1f7a2-9440-40de-a06b-ad3f298520fc", ConsumerAccount(mapObj))







	@classmethod
	def listAll(cls,criteria):
		"""
		Query objects of type ConsumerAccount by id and optional criteria
		@param type criteria
		@return ConsumerAccount object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("8e057c8e-a164-4909-ae3d-14b99c061c02", ConsumerAccount(criteria))


	def update(self):
		"""
		Updates an object of type ConsumerAccount

		@return ConsumerAccount object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("c27d6418-691c-412c-85e1-24ecc1571ea2", self)






