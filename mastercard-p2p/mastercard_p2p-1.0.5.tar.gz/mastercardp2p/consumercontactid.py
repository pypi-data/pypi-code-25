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

class ConsumerContactID(BaseObject):
	"""
	
	"""

	__config = {
		
		"327d6215-ca40-4b53-ab9e-ecc44d218bb4" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/contact_ids", "create", [], []),
		
		"6c488124-70dc-4ced-b4e7-25ed90d9c0ea" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/contact_ids/{contactId}", "delete", [], []),
		
		"f1dcbdff-9637-402e-8c15-e19a6ca0bd93" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/contact_ids/{contactId}", "read", [], []),
		
		"0c4ecc26-4d9c-4627-a153-4abbce548974" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/contact_ids", "query", [], []),
		
		"d6f89baf-7440-44a2-a86d-fd1d6a655e69" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/contact_ids/{contactId}", "update", [], []),
		
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
		Creates object of type ConsumerContactID

		@param Dict mapObj, containing the required parameters to create a new object
		@return ConsumerContactID of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("327d6215-ca40-4b53-ab9e-ecc44d218bb4", ConsumerContactID(mapObj))









	@classmethod
	def deleteById(cls,id,map=None):
		"""
		Delete object of type ConsumerContactID by id

		@param str id
		@return ConsumerContactID of the response of the deleted instance.
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

		return BaseObject.execute("6c488124-70dc-4ced-b4e7-25ed90d9c0ea", ConsumerContactID(mapObj))

	def delete(self):
		"""
		Delete object of type ConsumerContactID

		@return ConsumerContactID of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("6c488124-70dc-4ced-b4e7-25ed90d9c0ea", self)







	@classmethod
	def read(cls,id,criteria=None):
		"""
		Returns objects of type ConsumerContactID by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of ConsumerContactID
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

		return BaseObject.execute("f1dcbdff-9637-402e-8c15-e19a6ca0bd93", ConsumerContactID(mapObj))







	@classmethod
	def listAll(cls,criteria):
		"""
		Query objects of type ConsumerContactID by id and optional criteria
		@param type criteria
		@return ConsumerContactID object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("0c4ecc26-4d9c-4627-a153-4abbce548974", ConsumerContactID(criteria))


	def update(self):
		"""
		Updates an object of type ConsumerContactID

		@return ConsumerContactID object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("d6f89baf-7440-44a2-a86d-fd1d6a655e69", self)






