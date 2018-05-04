from p2p_python.tool.utils import AsyncCommunication

"""
AsyncCommunication example program

>> ac1.send_cmd('msg', 'hello world', 'user1')
user1 user1 hello world
{'cmd': 'msg', 'data': 'received! from user1', 'from': 'user1', 'to': 'user1', 'type': 'reply', 'uuid': 2851361868}
"""


def receive_msg(ac, from_name, data):
    print(ac.name, from_name, data)
    return 'received! from {}'.format(from_name)

ac0 = AsyncCommunication(name='user0')
ac1 = AsyncCommunication(name='user1')
ac2 = AsyncCommunication(name='user2')
ac0.share_que(ac1)
ac1.share_que(ac2)
ac0.add_event('msg', receive_msg)
ac1.add_event('msg', receive_msg)
ac2.add_event('msg', receive_msg)
ac0.start()
ac1.start()
ac2.start()

while True:
    try:
        cmd = input('>> ')
        exec('print(' + cmd + ')')
    except Exception as e:
        print("error", e)
