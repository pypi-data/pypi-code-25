from buglib import BugHook

a = BugHook()
a.start()


while 1:
    print(3)

    try:




        0/1
        0/1
    except BaseException as e:
        print(e)

    1/0
    print(12)


while 1:
    print(a.post_thread.is_null())

