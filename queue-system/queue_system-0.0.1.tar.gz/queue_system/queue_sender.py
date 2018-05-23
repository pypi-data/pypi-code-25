import pika


class QueueSender:
    def __init__(self, queue_name, host, port):
        self.parameters = pika.ConnectionParameters(host=host, port=port)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.queue_name = queue_name
        self.channel.queue_declare(queue=queue_name, durable=True)
    
    def sendMessage(self, message):
        self.channel.basic_publish(exchange='',
                      routing_key=self.queue_name,
                      body=message,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))                                  
    
    def terminateConnection(self):
        self.connection.close()
