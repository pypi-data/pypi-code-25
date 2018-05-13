from pushover import Client
import time

client = Client()

r = client.send_message("Hello!", title="Hello", priority=2, expire=120, timestamp=True, retry=60)
while r.poll():
    print r.acknowledged
    print r.expired
    print r.answer
    time.sleep(5)
