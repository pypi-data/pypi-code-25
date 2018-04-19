'''
Module for handle posts.
'''
import threading, asyncio, time

class EnqueueError(Exception):
    pass

class HandleError(Exception):
    pass

class PostQueue:
    '''
    A queue to handle posts.
    '''
    def __init__(self,ratiolimit,handle,mode='parallel'):
        self.__posts = []
        self.ratio = int(ratiolimit)
        self.mode=mode
        assert callable(handle), 'handle must be callable'
        self.__handle = handle(self)
        self.running = False

    @property
    def size(self):
        return len(self.__posts)

    def put(self,post):
        '''
        Add a post at the end of the queue
 
        Raises EnqueueError
        '''
        if self.size >= self.ratio:
            raise EnqueueError('ratio limit reached')
        else:
            self.__posts.append(post)

    def get(self):
        '''
        Get the first element of the queue
        '''
        return self.__posts.pop(0)

    def start(self):
        '''
        Start in a new thread the post handler
        
        Raises HandleError
        '''
        if self.running:
            raise HandleError("handler is already running")
        self.running = True
        if self.mode.startswith('async'):
            loop = asyncio.new_event_loop()
            threading.Thread(target=loop.run_until_complete, args=(self.__handle(self),), daemon=True).start()
        elif self.mode == 'parallel':
            threading.Thread(target=self.__handle, args=(self,), daemon=True).start()

    def stop(self):
        '''
        Stop executing the handler
        '''
        self.running = False

class PostHandler:
    '''
    Decorator to make post handler's.

    Usage:
        >>> @PostHandler()
        ... def handler(post):
        ...     #do something
        ...     pass
        ... 
        >>> queue = PostQueue(10,handler)
    '''
    def __init__(self):
        pass    

    def __call__(self,handler):
        def generator(queue):
            if queue.mode == 'parallel':
               def new_handler(queue):
                    while queue.running:
                        if queue.size:
                            handler(queue.get())
            elif queue.mode == 'async':
                async def new_handler(queue):
                    while queue.running:
                        if queue.size:
                            await handler(queue.get())
            else:
                raise HandleError("'%s' mode not sopported" % queue.mode)
            return new_handler
        return generator

