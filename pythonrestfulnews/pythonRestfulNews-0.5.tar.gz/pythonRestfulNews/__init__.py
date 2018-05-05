import requests
import json

def create_user(email, password, name='unknown', picture=''):
    url = 'http://api.restfulnews.com/users'
    headers = {'content-type': 'application/json'}    
    data = dict(
        email=email,
        password=password,
        name=name,
        picture=picture
    )
    json_data = json.dumps(data)
    
    resp = requests.post(url=url, data=json_data, headers=headers)
    data = resp.json()
    
    return data

def search_news(token, topics, companyids, start_date, end_date):
    
    url =  'http://api.restfulnews.com/search'
    auth = 'Bearer ' + token
    
    headers = {'content-type': 'application/json', 'authorization': auth}  
    
    params = {"topics": topics, "companyids": companyids, "start_date": start_date, "end_date": end_date}
    
    resp = requests.get(url=url, params=params, headers=headers)
    data = resp.json()
    
    return data

def retrieve_token(email, password):
    url = 'http://api.restfulnews.com/auth'
    headers = {'Content-Type': 'application/json'}
    data = dict(
        email = email,
        password = password
    )
    payload = json.dumps(data)
    r = requests.post(url, headers=headers, data=payload)
    return r.json()