import pika
import uuid
import json

# example message body for 2 billing accounts with a single asset subscription account each
# Each billing account has a months field to indicate the time period for which the data has to be extracted
# If the months field is empty then that billing account and asset account will use the root level months as period
body = {"months": 2,
        "accounts": [{
            "months": 1,
            "billing_account_number": "",
            "credentials": {"vserver": "", "username": "", "password": ""},
            "asset_accounts": [{
                "asset_account_number": "",
                "credentials": {}
            }]
        },
            {
                "months": 1,
                "billing_account_number": "",
                "credentials": {"api_key": ""},
                "asset_accounts": [{
                    "asset_account_number": "",
                    "credentials": {}
                }]
            }
        ]
        }


# example message body for 2 asset subscription accounts
body = {"months": 2,
        "accounts": [{
            "months": 1,
            "billing_account_number": "",
            "credentials": {"api_key": ""},
            "asset_accounts": [{
                "asset_account_number": "",
                "credentials": {"tenant_id": "", "application_id": "", "application_secret": ""}
            },{
                "asset_account_number": "",
                "credentials": {"tenant_id": "", "application_id": "", "application_secret": ""}
            }]
        },
            {
                "months": 1,
                "billing_account_number": "",
                "credentials": {"api_key": ""},
                "asset_accounts": [{
                    "asset_account_number": "",
                    "credentials": {"tenant_id": "", "application_id": "", "application_secret": ""}
                },
                {
                    "asset_account_number": "",
                    "credentials": {"tenant_id": "", "application_id": "", "application_secret": ""}
                }]
            }
        ]
        }


msgbody = json.dumps(body)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
channel = connection.channel()
result=channel.queue_declare(exclusive=True)
callback_queue= result.method.queue

def on_response(ch, method, props, body):
    if corr_id == props.correlation_id:
        response = body


channel.basic_consume(on_response, no_ack=True,
                                   queue=callback_queue)

response = None
corr_id=str(uuid.uuid4())


channel.basic_publish(exchange='',
    routing_key='vmware.extract',
    properties=pika.BasicProperties(reply_to=callback_queue,
                                    correlation_id = corr_id,),
                      body=msgbody)
while response is None:
    connection.process_data_events()


