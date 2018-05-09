import asyncio
import socket
import pickle
import time
import random
import os, sys
from multiprocessing import Process
import multiprocessing
from seed.mrpackage.libs import loger
from contextlib import contextmanager
from seed.mrpackage.daemon import Daemon
from seed.mrpackage.udp import open_remote_endpoint as open_udp_connection

log = loger()

def _r():
    a = _AServer()
    a.run()

def start_local_socket_process():
    p = Process(target=_r)
    p.start()


class _AServer:

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        if self.loop.is_closed():
            self.loop = asyncio.new_event_loop()
        self.queue = asyncio.Queue(loop=self.loop)
        self.tcp_handlers = {}
        self.udp_handlers = {}

    async def _tcp(self, ip, port, timeout=7, **kwargs):
        waiter = asyncio.open_connection(ip, port, loop=self.loop)
        try:
            reader, writer = await asyncio.wait_for(waiter, timeout=timeout)
        except asyncio.TimeoutError as e:
            log.error("Timeout : {}:{}".format(ip, port))
            await self.queue.put("timeout :tcp: " + ip)
            return
        except socket.error as e:
            log.error(e)
            await self.queue.put(e)
            return

        id = self._create_id()
        self.tcp_handlers[id] = {'write': writer.write, 'read':reader.read, 'if_close': False, 'close':writer.close}
        return id

    def _create_id(self):
        id = str(int(time.time())) + str(random.randint(1,10))
        return id

    async def _udp(self, ip, port,msg=None,timeout=7, **kwargs):
        handler = await open_udp_connection(ip, port , loop=self.loop)
        data =None
        try:
            if msg:
                handler.send(msg)
                recive_waiter = handler.recive()
                data, addr = asyncio.wait_for(recive_waiter, timeout=timeout)

        except asyncio.TimeoutError:
            log.error("Timeout udp: {}:{}".format(ip, port))
            await self.queue.put("Timeout :udp: " +ip)
            return
        except socket.error as e:
            log.error(e)
            log.info("error")
            await self.queue.put(e)
            return

        id = self._create_id()
        self.udp_handlers[id] = {'write': handler.send, 'read':handler.receive, 'if_close': False, 'close': handler.close, 'data':data}
        return id

    async def commander(self,reader, writer):
        data = await reader.read(65535)
        log.info("recv from " + str(writer.get_extra_info('peername')))
        c = data[:2]
        msg = data[2:]
        if c == b'in':
            tp,ip,port = msg.split(b',')
            s = self._tcp
            if tp == b'udp':
                s = self._udp

            id = await s(ip, int(port))
            if not id:
                e = await self.queue.get()
                writer.write(pickle.dumps({'msg':'create failed:' + str(e)}))
                await writer.drain()
            else:
                log.info("create : " + id)
                writer.write(pickle.dumps({'msg':'create ok', 'id':id}))
                await writer.drain()


        elif c == b'rd':
            id = msg.decode()
            writer.write(pickle.dumps({'id': id , 'msg':'read command accept, get data by: da{id}'}))
            await writer.drain()
            await self.read(id)

        elif c == b'wt':
            id, data = msg.split(b',', 1)
            id = id.decode()
            await self.write(id, data)
            writer.write(pickle.dumps({'id':id, 'msg':'write to ' + id }))
            await writer.drain()

        elif c == b'da':
            id = msg.decode()
            h,tp = self.get_handler(id)
            if h:
                if 'data' in h:
                    writer.write(pickle.dumps({'id': id, 'data': h['data'], 'msg':'ok'}))
                    await writer.drain()
                else:
                    writer.write(pickle.dumps({'id': id, 'data': None, 'msg':'null'}))
                    await writer.drain()
            else:
                writer.write(pickle.dumps({'id':id, 'msg':'no id'}))
                await writer.drain()
        elif c == b'cl':
            id = msg.decode()
            await self.close(id)
            writer.write(pickle.dumps({'id':id, 'msg':'killed'}))
            await writer.drain()

        elif c == b'ls':
            id_t = list(self.tcp_handlers.keys())
            id_u = list(self.udp_handlers.keys())
            writer.write(pickle.dumps({'tcp':id_t, 'udp':id_u}))
            await writer.drain()

        elif c == b'lo':
            msg = await self.queue.get()
            writer.write(pickle.dumps({'msg':msg}))
            await writer.drain()
        elif c == b'ki':
            raise KeyboardInterrupt("Exit --")

    async def read(self, id):
        with self.deal(id) as hand:
            read = hand['read']
            log.info("wait read")
            try:
                st = 0
                while 1:
                    if st > 10:
                        raise asyncio.TimeoutError("socket seemd closed")

                    waiter = read()
                    data = await asyncio.wait_for(waiter, timeout=10)
                    if not data:
                      st += 1
                    log.info(id + " :got data ")
                    h,t = self.get_handler(id)
                    if h:
                        h['data'] = data
                        break
                    else:
                        raise socket.error("no session ")
            except asyncio.TimeoutError as e:
                await self.close(id)
                log.info("close id: " + id)
                await self.queue.put('Timeout and kill this session.')
                log.info("collect msg in queue")
            except socket.error as e:
                await self.close(id)
                log.info("close id: " + id)
                await self.queue.put(e)
                log.info("collect msg in queue")


    async def write(self,id ,data):
        with self.deal(id) as hand:
            write = hand['write']
            waiter = write(data)

    def run(self):
        coro = asyncio.start_server(self.commander, '127.0.0.1', 12888, loop=self.loop)
        server = self.loop.run_until_complete(coro)
        try:
            print("Run")
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass

        # Close the server
        server.close()
        self.loop.run_until_complete(server.wait_closed())
        self.loop.close()

    async def close(self, id):
        h,t = self.get_handler(id)
        if t == 'tcp':
            h['close']()
            del self.tcp_handlers[id]
        elif t == 'udp':
            h['close']()
            del self.udp_handlers[id]

    def get_handler(self,id ):
        if id in self.udp_handlers:
            return self.udp_handlers[id],'udp'
        elif id in self.tcp_handlers:
            return self.tcp_handlers[id],'tcp'
        else:
            return None,None

    @contextmanager
    def deal(self, id):
        try:
            h,p = self.get_handler(id)
            if not h:
                log.error("not found")
                raise Exception("session id is not found !")
            yield h
        finally:
            if  h and h['if_close']:
                if p == 'udp':
                    del self.udp_handlers[id]
                elif p == 'tcp':
                    del self.tcp_handlers[id]


def test_if_local_socket_open():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1', 12888))
        return True
    except Exception:
        return False

#if not test_if_local_socket_open():
#    start_local_socket_process()

class ConnectionCreateError(Exception):
    pass

class Connection:
    def __init__(self, ip='127.0.0.1', port=None, tp='tcp', id=None):
        if id:
            self.id = id
        else:
            self.tp = tp
            self.ip = ip
            self.port = int(port)
            tmp = self._write(b'in' + ",".join([tp, ip, str(port)]).encode())
            if 'id' in tmp:
                self.id = tmp['id']
            else:
                log.error(tmp)
                raise ConnectionCreateError(tmp['msg'])

    def _write(self,data, read=True):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(("127.0.0.1", 12888))
        except socket.error as e:
            raise e
            return None
        s.send(data)
        if read:
            d = s.recv(32767)
            return pickle.loads(d)

    def read(self, wait=False):
        id = self.id
        m = 'rd' + self.id
        msg = self._write(m.encode())
        if not wait:
            return msg
        return self.data(wait=True)

    def log(self):
        return self._write(b'lo')

    def data(self, wait=False):
        id = self.id
        m = 'da' + self.id
        d = self._write(m.encode(), read=True)
        if d['data']:
            log.debug(d['msg'])
            return d['data']
        else:
            if wait:
                timeout = 7
                if isinstance(wait, int):
                    timeout = int(wait)
                s = time.time()
                while 1:
                    if time.time() - s > timeout:
                        break
                    if d['data']:
                        log.debug(d['msg'])
                        return d['data']
                log.debug(d['msg'])
                return d['data']

    def close(self):
        return self._write(b'cl' + self.id.encode("utf8"))

    def write(self, data):
        id = self.id
        m = 'wt' + self.id
        m = m.encode()
        if isinstance(data, str):
            data = data.encode('utf8')
            m += b',' + data
        elif isinstance(data, bytes):
            m += b',' + data
        else:
            raise Exception("must str or bytes")

        return self._write(m)

    def ls(self):
        return self._write(b"ls")

    def inject(self, id):
        return Connection(id=id)

    @staticmethod
    def stop():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 12888))
        s.send(b'ki')



class DaemonSocket(Daemon):

     def run(self):
         serv = _AServer()
         log.info("Start local socket server!")
         serv.run()

def start_socket_service():
    if sys.argv[1] == 'start':
        d = DaemonSocket('/tmp/async_sockset.pid')
        d.start()
    elif sys.argv[1] == 'stop':
        d = DaemonSocket('/tmp/async_sockset.pid')
        d.stop()
    elif sys.argv[1] == 'restart':
        d = DaemonSocket('/tmp/async_sockset.pid')
        d.restart()
    log.info("Start service async socket")

#def shutdown():
 #   con = Connection.stop()
  #  del con
   # log.info("Bye ~")

#import atexit
#atexit.register(shutdown)
