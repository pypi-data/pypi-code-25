import connect_db
import datetime
import json

def log(logstring, isError = False, isUserInput = False):
    db = connect_db.connectMongo()
    log_collection = db['log_collection1']
    logText = open("logs.txt", "a")
    time = datetime.datetime.utcnow()

    if(isError):
        logstring =  "Error : " + logstring
        print(logstring)

    if(isUserInput):
        post = {"Log_String": logstring, "author": "User", "date": time}
    else:
        post = {"Log_String": logstring, "author": "System", "date": time}



    logText.write(time.strftime('%m/%d/%Y/%H:%M'))
    logText.write(json.dumps(logstring))
    logText.write('\n')

    logText.close
    
    post_id = log_collection.insert_one(post).inserted_id
    # print ('succesfully logged')
    #getLogs()

def getLogs():
    print ("These are the logs avaliable on the server")
    db = connect_db.connectMongo()
    log_collection = db['log_collection1']
    message = log_collection.find()
    for data in message:
        print (data['Log_String'])


