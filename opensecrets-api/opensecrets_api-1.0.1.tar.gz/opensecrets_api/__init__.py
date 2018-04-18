import requests 

GET_LEGISLATORS = '&method=getLegislators'
GET_MEM_PFD_PROFILE = '&method=memPFDprofile'
GET_CANDIDATE_SUMMARY = '&method=candSummary'
GET_CANDIDATE_CONTRIBUTIONS = '&method=candContrib'
GET_CANDIDATE_INDUSTRIES = '&method=candIndustry'
GET_CANDIDATE_INDUSTRIES_BY_INDUSTRIES = '&method=CandIndByInd'
GET_CANDIDATE_SECTOR = '&method=candSector'
GET_CONGRESS_COMMITTEE_BY_INDUSTRY = '&method=congCmteIndus'
GET_ORGANIZATIONS = '&method=getOrgs'
GET_ORGANIZATION_SUMMARY = '&method=orgSummary'
GET_INDEPENDENT_EXPENDITURES = '&method=independentExpend'

class OpenSecrets():
	"""
	industry codes can be found at https://www.opensecrets.org/downloads/crp/CRP_Categories.txt
	committee id's can be found at https://www.opensecrets.org/downloads/crp/CRP_CongCmtes.txt
	"""
	 
	url = 'http://www.opensecrets.org/api/?output=json&apikey='

	def __init__(self, api_key):
		self.api_key = api_key
		self.url = self.url + api_key

	def make_request(self, r):
		try:
			return requests.get(self.url + r).json()
		except:
			print('Something went wrong, please check your api key or params')

	#members

	def get_legislators(self, id):
		"""
		Search for a list of legislators

		Returns information about legislators by id or state.

		Parameters
		----------
		id: str
			Legislator ID or 2 letter state code ('CA')

		Returns
		-------
		list[dict]
			A list of legislators 

		"""
		return self.make_request(GET_LEGISLATORS + '&id=' + str(id))['response']['legislator']

	def get_member_pfd_profile(self, cid, year=''):
		"""
		Summary of a members finnancial disclosure

		Returns the personal finnance information about a legislator by id

		Parameters
		----------
		cid: str
			Legislator ID
		year: int, str
			2013 - 2018

		Returns
		-------
		dict
			A legislator's information

		"""
		if year:
			year = '&year=' + str(year)
		ret = self.make_request(GET_MEM_PFD_PROFILE + '&cid=' + str(cid) + year)['response']['member_profile']
		return ret
	
	#candidates

	def get_candidate_summary(self, cid, cycle=''):
		"""
		Summary of a politician's fundraising information

		Parameters
		----------
		cid: str
			Candidate ID
		cycle: int, str
			2012, 2014, 2016, 2018; leave blank for latest cycle

		Returns
		-------
		dict
			A Candidate's fundraising information

		"""
		if cycle:
			cycle = '&cycle=' + str(cycle)
		return self.make_request(GET_CANDIDATE_SUMMARY + '&cid=' + str(cid) + cycle)['response']['summary']['@attributes']

	def get_candidate_contributors(self, cid, cycle=''):
		"""
		Returns top contributors to specified candidate for a House or Senate seat or member of Congress.

		These are 6-year numbers for senators/Senate candidates; 2-year numbers for representatives/House candidates.

		Parameters
		----------
		cid: str
			Candidate ID
		cycle: int, str
			2012, 2014, 2016, 2018; leave blank for latest cycle

		Returns
		-------
		list[dict]
			A list of the top contributors and the contribution information
		dict
			The candidate's information

		"""
		if cycle:
			cycle = '&cycle=' + str(cycle)
		ret = self.make_request(GET_CANDIDATE_CONTRIBUTIONS + '&cid=' + str(cid) + cycle)['response']['contributors']
		return ret['contributor'], ret['@attributes']

	def get_candidate_industries(self, cid, cycle=''):
		"""
		Provides the top ten industries contributing to a specified candidate for a House or Senate seat or member of Congress.

		These are 6-year numbers for Senators/Senate candidates; 2-year total for Representatives/House candidates.

		Parameters
		----------
		cid: str
			Candidate ID
		cycle: int, str
			2012, 2014, 2016, 2018; leave blank for latest cycle

		Returns
		-------
		list[dict]
			A list of the top contributing industries and the contribution information
		dict
			The candidate's information

		"""
		if cycle:
			cycle = '&cycle=' + str(cycle)
		ret = self.make_request(GET_CANDIDATE_INDUSTRIES + '&cid=' + str(cid) + cycle)['response']['industries']

		return ret['industry'], ret['@attributes']

	def get_candidate_total_by_industry(self, cid, industry_id, cycle=''):
		"""
		Provides total contributed to specified candidate from specified industry.

		Parameters
		----------
		cid: str
			Candidate ID
		industry_id: str
			3 letter industry code
		cycle: int, str
			2012, 2014, 2016, 2018; leave blank for latest cycle

		Returns
		-------
		dict
			The candidate's information by industry

		"""
		if cycle:
			cycle = '&cycle=' + str(cycle)
		return self.make_request(GET_CANDIDATE_INDUSTRIES_BY_INDUSTRIES + '&cid=' + str(cid) + '&ind=' + str(industry_id) + cycle)['response']['candIndus']['@attributes']

	def get_candidate_total_by_sector(self, cid, cycle=''):
		"""
		Provides sector total of specified politician's receipts

		Parameters
		----------
		cid: str
			Candidate ID
		cycle: int, str
			2012, 2014, 2016, 2018; leave blank for latest cycle

		Returns
		-------
		list[dict]
			A list of the top contributing sectors and the contribution information
		dict
			The candidate's information

		"""
		if cycle:
			cycle = '&cycle=' + str(cycle)
		ret = self.make_request(GET_CANDIDATE_SECTOR + '&cid=' + str(cid) + cycle)['response']['sectors']
		return ret['sector'], ret['@attributes']

	#congressional committees

	def get_congress_committee_by_industry(self, committee_id, industry_id, congress_number=''):
		"""
		Provides summary fundraising information for a specific committee, industry and congress number

		Parameters
		----------
		committee_id: str
			Committee ID in CQ format
		industry_id: str
			3 letter industry code
		congress_numer: str, int
			112: 2012, 113: 2014, 114: 2016, 115: 2018
	   	
		Returns
		-------
		list[dict]
			A list of the members in the committee
		dict
			The committee's information

		"""
		if congress_number:
			congress_number = '&congno=' + congress_number
		ret = self.make_request(GET_CONGRESS_COMMITTEE_BY_INDUSTRY + '&cmte=' + committee_id + '&indus=' + industry_id + congress_number)['response']['committee'] 
		return ret['member'], ret['@attributes'] 

	#organizations

	def get_organizations(self, organization_query):
		"""
		Provides a list of organizations and ids that match the term searched.

		Parameters
		----------
		organization_query: str
			A string to search
	   	
		Returns
		-------
		list[dict]
			A list of organizations that match the query
		"""
		return self.make_request(GET_ORGANIZATIONS + '&org=' + organization_query)['response']['organization']

	def get_organization_summary(self, organization_id):
		"""
		Provides the information of money spent by an organization

		Parameters
		----------
		organization_id: str
			The organization id, availabler via get_organizations(query)
	   	
		Returns
		-------
		dict
			A dict with information about the organization
		"""
		return self.make_request(GET_ORGANIZATION_SUMMARY + '&id=' + organization_id)['response']['organization']['@attributes']

	#independent expenditures

	def get_independent_expenditures(self):
		"""
		Method to access the latest 50 independent expenditure transactions reported. Updated 4 times a day.
	   	
		Returns
		-------
		list[dict]
			A list of the 50 most recent independent expenditures
		"""
		return self.make_request(GET_INDEPENDENT_EXPENDITURES)['response']['indexp']