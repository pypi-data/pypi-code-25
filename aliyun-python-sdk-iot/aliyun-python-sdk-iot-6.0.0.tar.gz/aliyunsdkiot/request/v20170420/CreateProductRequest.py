# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from aliyunsdkcore.request import RpcRequest
class CreateProductRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'Iot', '2017-04-20', 'CreateProduct')

	def get_CatId(self):
		return self.get_query_params().get('CatId')

	def set_CatId(self,CatId):
		self.add_query_param('CatId',CatId)

	def get_NodeType(self):
		return self.get_query_params().get('NodeType')

	def set_NodeType(self,NodeType):
		self.add_query_param('NodeType',NodeType)

	def get_Id2(self):
		return self.get_query_params().get('Id2')

	def set_Id2(self,Id2):
		self.add_query_param('Id2',Id2)

	def get_Name(self):
		return self.get_query_params().get('Name')

	def set_Name(self,Name):
		self.add_query_param('Name',Name)

	def get_ExtProps(self):
		return self.get_query_params().get('ExtProps')

	def set_ExtProps(self,ExtProps):
		self.add_query_param('ExtProps',ExtProps)

	def get_SecurityPolicy(self):
		return self.get_query_params().get('SecurityPolicy')

	def set_SecurityPolicy(self,SecurityPolicy):
		self.add_query_param('SecurityPolicy',SecurityPolicy)

	def get_PayType(self):
		return self.get_query_params().get('PayType')

	def set_PayType(self,PayType):
		self.add_query_param('PayType',PayType)

	def get_Desc(self):
		return self.get_query_params().get('Desc')

	def set_Desc(self,Desc):
		self.add_query_param('Desc',Desc)