class Apim:
	def __init__(self, apimBaseUrl, apimId, apimKey, pcfWebApiUrl):
			self.apimBaseUrl = apimBaseUrl
			self.apimId = apimId
			self.apimKey = apimKey
			self.pcfWebApiUrl = pcfWebApiUrl
			self.token = None
			self.apiVersion = "api-version=2016-07-07"