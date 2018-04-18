from queue import Queue
from threading import Thread
import re
import requests

class Scanner:

  def verifySocks(self, sock: str, q: None or object,  out:str = 'validSocks.txt', url: str = "http://icanhazip.com/"):
      proxies = {
      'http': "socks5://{}".format(sock.strip()),
      'https': "socks5://{}".format(sock.strip()),
      }

      try:
        src = requests.get(url, proxies=proxies, timeout = 5).text
      except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        q.task_done()
        return False

      q.task_done()
      
      print("[+] {} Socks is Working [+]".format(sock))

      # store them
      self.store(out, "{}\n".format(sock))
      return True

  def store(self, file: str, content: str):
    with open(file, 'a') as out:
      out.write(content)

  def checkSocks(self, file: str, threads: int, outfile: str):
      socks = []
      with open(file, 'r') as out:
        socks = [k.strip() for k in out.read().split('\n') if k != '']

      if len(socks) < threads:
          stop = len(socks)
      else:
          stop = threads

      i = 1
      q = Queue(maxsize=0)
      j = 1
      while j <= len(socks):
        sock = socks[j - 1]
        print('[+] Starting Worker No.', j, '[+]')
        worker = Thread(target = self.verifySocks, args = (sock, q, outfile))

        worker.setDaemon(True)
        worker.start()

        if i >= stop:
            print('[+] Waiting for workers to done their work! [+]')
            q.join()
            i = 1

        # put queue
        q.put(i)
        i += 1
        j += 1
      q.join()