

import os
import sys
import argparse
#from contract_process import *
from pymongo import MongoClient
from pprint import pprint
import datetime
import click
import pandas as pd
from colorama import init, Fore, Back, Style
import re

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

init()

conn = MongoClient('localhost', port=14041)

class Config(object):
    def __init__(self):
        self.verbose = False


pass_config = click.make_pass_decorator(Config, ensure=True)

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def currency_sync():
    db = conn.workdb_test
    api = next(db.keys.find({"item":"currency_api"}))
    
    api1 = api['values']['api1']
    api2 = api['values']['api2']
    primary_currency = next(db.keys.find({"item":"primary_currency"}))['value']
    api_try = api1
    api_access_point = 'https://v3.exchangerate-api.com/bulk/{}/{}'

    try:
        response = requests_retry_session().get(api_access_point.format(api_try,primary_currency))
        if response.json()['result'] == "error" and response.json()['error'] == "quota-reached":
            api_try = api2
            response = requests_retry_session().get(api_access_point.format(api_try,primary_currency))
        elif response.json()['result'] == "error" and response.json()['error'] == "invalid-key":
            print(Fore.RED + "ERROR: Cannot retrieve latest currency exchange rates. Check API key credentials." + Style.RESET_ALL)
            return
        db.keys.find_and_modify(
            query={ 'item' : "currency_api"},
            update={'$set': {'last_updated': response.json()['timestamp']}},
            new=True 
            )
        db.latest_currency_rates.find_and_modify(
            query={'ref': "0"},
            update={'$set': {'rates':response.json()['rates']}},
            new=True
        )
        #print(datetime.datetime.fromtimestamp(int(response.json()['timestamp'])).strftime('%Y-%m-%d %H:%M:%S'))
    except:
            print(Fore.CYAN + "Warning: Cannot retrieve latest currency exchange rates. Check API end point or internet connection" + Style.RESET_ALL)



def currency_data(amount, from_currency, to_currency):
    db = conn.workdb_test
    from_currency_rate =  next(db.latest_currency_rates.find({},{"rates.{}".format(from_currency):1, "_id":0})).get('rates').get(from_currency)
    to_currency_rate =  next(db.latest_currency_rates.find({},{"rates.{}".format(to_currency):1, "_id":0})).get('rates').get(to_currency)
    rate = to_currency_rate/from_currency_rate
    converted_amount = amount*rate
    return converted_amount


def getNextSeqVal(db, sequence_name,opt):
    if opt == 1:
        next_seq = db.counters.find_and_modify(
            query={ '_id' : sequence_name },
            update={'$inc': {'sequence_value': 1}},
            #fields={'id': 1, '_id': 0},
            new=True 
        ).get('sequence_value')
        return next_seq
    else:
        next_seq = db.counters.find_and_modify(
            query={ '_id' : sequence_name },
            update={'$set': {'sequence_value': 1}},
            #fields={'id': 1, '_id': 0},
            new=True 
        ).get('sequence_value')
    return next_seq

def client_info(client):
    """This function is to operate on client database"""
    """

    Schema of client info database
    userid: int
    name: str
    email: str
    phone: str (countrycode-phonenumber)
    mode: str
    note: str
    country: str

    """

    clientID = re.findall(r'\d[0-9]*|\w[A-z]*', str(client))
    conn = MongoClient('localhost', port=14041)
    db = conn.workdb_test
    table = db.client_db
    record = db.country_codes
    
    try:
        clientID = int(clientID[0])
        print("Its an existing client")
        user_id = next(table.find({"userid":str(clientID)}))
        return user_id['_id']
    except:
        print("\nNEW CLIENT INFORMATION\n")
        choice = str(input('Do you wish to add the client details right now (y/n) ? [n]: ').upper() or 'n')
        if choice == 'Y':
            name = " ".join(x for x in clientID)
            userid = str(getNextSeqVal(db, "client_id",1))
            email = input('Enter e-mail ID : ')
            phone = input('Enter phone number with country code : ')
            mode = input('Enter nature of lead : ')
            if phone == '':
                country = input('Enter country name : ')
            else:
                dial_code = '+{}'.format(re.findall(r'(\d*)-(\d*)',phone)[0][0])
                country = input('Enter country name [{}]: '.format(next(record.find({"dial_code":dial_code}))['name']))
                if country == '':
                    country = next(record.find({"dial_code":dial_code}))['name']
            note = input('Enter any note on the client : ')
            verified = str(input('Are all the details verified (y/n) ? [n]: ') or 'n').upper()
            client_doc = {"name":name, "userid":userid, "email":email, "phone":phone, "mode":mode,"country":country,"note":note,"verified":verified}
            try:
                record_id = table.insert(client_doc)
                print('\nClient added successfully')
                return record_id
            except:
                print('Error in adding client to database - Assigned Uknown')
                user_id = next(table.find({"userid":str(0)}))
                return user_id['_id']
        else:
            name = " ".join(x for x in clientID)
            userid = str(getNextSeqVal(db, "client_id",1))
            email = ""
            phone = ""
            mode = ""
            country = ""
            note = ""
            verified = ""
            client_doc = {"name":name, "userid":userid, "email":email, "phone":phone, "mode":mode,"country":country,"note":note}
            try:
                record_id = table.insert(client_doc)
                print('\nClient added successfully')
                return record_id
            except:
                print('Error in adding client to database - Assigned Uknown')
                user_id = next(table.find({"userid":str(0)}))
                return user_id['_id']

def amt(am):
    ame = re.findall(r'([A-z]* |)(\d*.\d*)', str(am))
    amount = float(ame[0][1]);
    if ame[0][0] == '':
        curr = "USD"
    else:
        curr = ame[0][0].upper();
    return curr, amount

def time(referencetime, date):

    if type(date) == datetime.datetime:
        return date
    dateformatsign = re.findall(r'([+-])', date)
    dateformat = re.findall(r'(\d)([dhm])', date)

    weeks = 0
    days = 0
    hours = 0
    minutes = 0
    if dateformatsign:
        if dateformatsign[0] == '+':
            shift = 1;
        elif dateformatsign[0] == '-':
            shift =-1;
        for x in dateformat:
            if x[1] == 'w':
                weeks = shift*int(x[0])
            elif x[1] == 'd':
                days = shift*int(x[0])
            elif x[1] == 'h':
                hours = shift*int(x[0])
            elif x[1] == 'm':
                minutes = shift*int(x[0])
            Calc_Date = referencetime + datetime.timedelta(weeks = weeks, days = days, hours = hours, minutes = minutes)
            return Calc_Date
    elif date == 'today':
        Calc_Date = referencetime + datetime.timedelta(weeks = weeks, days = days, hours = hours, minutes = minutes)
        return Calc_Date
    else:
        return 'error'

@click.group()
@click.option('-u','-update', is_flag=True)
def cli(update):
    if update:
        #click.echo("updated")
        currency_sync()

@cli.command()
def client():
    """This function operates on the client database"""
    """
    Functions:
    - View client database
    - Add new client information
    - Edit existing client information
    - Delete existing client information
    """
    pass

@cli.command()
def settings():
    """This function operates on all the settings for the app"""
    '''
    - API settings
    - Primary Currency

    '''
    pass



@cli.command()
@click.option('-t','--title',type=str,default='No title', help="Title of project")
@click.option('-a','--amount',type=float,default=0.0, help="Price of project")
@click.option('-c','--client',type=str,default='0', help="Title of project")
@click.option('-m','--mode',type=str,default='upwork', help="Mode of payment for project lead")
@click.option('-mu','--modeupwork',is_flag=True, help="Mode of payment for project lead [UpWork]")
@click.option('-mf','--modefreelancer',is_flag=True, help="Mode of payment for project lead [Freelancer]")
@click.option('-mp','--modepaypal',is_flag=True, help="Mode of payment for project lead [PayPal]")
@click.option('-mb','--modebank',is_flag=True, help="Mode of payment for project lead [Bank]")
@click.option('-tag',type=str,default='', help="Tags for the project")
@click.option('-n','--note',type=str,default='', help="Note for the project")
@click.option('-s','--startdate',default=datetime.datetime.now(), help="Date of project lead arrival")
@click.option('-e','--enddate',default='+7d', help="Expected date of closing project contract process")
@click.option('-ed','--est_duration',type=int,default=2, help="Estimated duration of project")
@click.argument('action_type',type=str,default='view', required=False)
def cud(
    action_type, 
    title, 
    amount, 
    client, 
    mode, 
    modeupwork, 
    modefreelancer,
    modepaypal,
    modebank,
    tag,
    note,
    startdate,
    enddate,
    est_duration):
    """This function operates on contracts under deliberation"""

    db = conn.workdb_test
    cuddb = db.cud_db
    
    if action_type == "add":

        if modeupwork:
            mode = 'upwork'
        elif modefreelancer:
            mode = 'freelancer'
        elif modepaypal:
            mode = 'paypal'
        elif modebank:
            mode = 'bank'
        curr, amount = amt(amount)
        estimated_amount_INR = currency_data(amount, curr, "INR")
        response = cuddb.insert([{
            "title" : title,
            "amount" : amount,
            "client" : client,
            "mode" : mode,
            "note" : note,
            "tag" : tag,
            "start_date" : time(startdate, startdate),
            "end_date" : time(startdate, enddate),
            "estimated_duration": est_duration,
            "estimated_amount_INR": estimated_amount_INR
            }])
        print("\n Added successfully!")
    elif action_type == "edit":
        pass
    elif action_type == "del":
        pass
    elif action_type == "view":
        cud_data = []
        for document in cuddb.find():
            cud_data.append(document)
        df = pd.DataFrame(cud_data)
        print(Fore.RED + Back.YELLOW + '\n\n Contract Under Deliberation: View\n' + Style.RESET_ALL)
        print(Fore.GREEN + ' INFO' + Style.RESET_ALL)
        print('------')
        print(df[['title','amount',"client", "mode", "start_date", "end_date", "estimated_duration", "estimated_amount_INR"]])
        print('\n SUMMARY')
        print('---------')
    else:
        print("No action")

@cli.command()
@click.option('-s','--string', default='World', help='This is the thing that is greeted.')
@click.option('-r','--repeat', default=1, help='How many types you wish to repeat the greetings?')
@click.argument('out', type=click.File('w'), default='-', required=False)
def co(string, repeat, out):
    """This function operates on ongoing contracts"""
    pass


@cli.command()
@click.option('-s','--string', default='World', help='This is the thing that is greeted.')
@click.option('-r','--repeat', default=1, help='How many types you wish to repeat the greetings?')
@click.argument('out', type=click.File('w'), default='-', required=False)
def cpt(string, repeat, out):
    """This function operates on contracts pending transfer of due amount"""
    pass

@cli.command()
@click.option('-s','--string', default='World', help='This is the thing that is greeted.')
@click.option('-r','--repeat', default=1, help='How many types you wish to repeat the greetings?')
@click.argument('out', type=click.File('w'), default='-', required=False)
def cat(string, repeat, out):
    """This function operates on contract payment is in transit"""
    pass

@cli.command()
@click.option('-s','--string', nargs=+1, default='World', help='This is the thing that is greeted.')
@click.argument('out', type=str, default='No title', required=False)
def caa(out, string):
    """This function operates on contracts for which payment has arrived"""
    print(out)
    print(string)


if __name__ == '__main__':
    
    cli()