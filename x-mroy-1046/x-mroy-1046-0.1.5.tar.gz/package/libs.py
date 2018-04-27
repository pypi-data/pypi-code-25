import logging
import os
import rsa
import pickle
import time
import random

import json
import base64
import requests

def loger(level=logging.INFO):
    logging.basicConfig(level=level)
    return logging.getLogger(__file__)

def GetIp():
    return requests.get("http://ipecho.net/plain").text.strip()

pubip = GetIp()
pubip_rsa = None
if not os.path.exists(os.path.join(os.getenv("HOME"), "seed")):
    os.mkdir(os.path.join(os.getenv("HOME") , "seed"))
log = loger()
SEC_LEVEL = 2048
BLOCK_LEN = SEC_LEVEL // 8

class Rsa:
    def __init__(self, label, pub=None, pri=None):
        self.pub = None
        self.pri = None
        self.label = label
        home = os.path.join(os.getenv("HOME"), "seed")
        self.home = home
        if not os.path.exists(home):
            os.mkdir(home)

        if not self.pub:
            self.load()

        if not self.pub:
            self.generate()

    def generate(self):
        log.info("Generate :2048 key")
        self.pub, self.pri = rsa.newkeys(SEC_LEVEL)
        self.save()

    def en(self,msg):
        ml = len(msg)
        y = 0
        en_blocks = b''
        while 1:
            block = msg[y: y+64]
            if not block:break
            try:
                en_blocks += rsa.encrypt(block, self.pub)
            except Exception:
                return None
            y += 64
        return en_blocks

    def de(self, msg):
        de_blocks = b''
        y=0
        while 1:
            block = msg[y:y+BLOCK_LEN]
            if not block:break
            try:
                de_blocks += rsa.decrypt(block, self.pri)
            except Exception:
                log.error("decrypt break in y:%d " % y)
                return None
            y += BLOCK_LEN
        return de_blocks

    def load(self):
        home = self.home
        head = os.path.join(home, self.label)
        if not os.path.exists(os.path.join(home, self.label + ".pub")):
            return

        if os.path.exists(head + ".pri"):
            with open(head + ".pri", 'rb') as fp:
                self.pri = rsa.PrivateKey.load_pkcs1(fp.read())
        if os.path.exists(head + ".pub"):
            with open(head + ".pub", "rb") as fp:
                self.pub = rsa.PublicKey.load_pkcs1(fp.read())

    def save(self):
        home = self.home
        if self.pri:
            with open(os.path.join(home, self.label + ".pri"), 'wb') as fp:
                fp.write(self.pri.save_pkcs1())

        if self.pub:
            with open(os.path.join(home, self.label +  ".pub"), "wb") as fp:
                fp.write(self.pub.save_pkcs1())

    def import_key(self, bytes):
        id, pub = pickle.loads(bytes)
        log.info("try to load key:\n" + pub.decode("utf8"))
        with open(os.path.join(self.home, id + ".pub"), "wb") as fp:
            fp.write(pub)
        return id

    def export_key(self):
        id, pub = self.label, self.pub.save_pkcs1()
        e = pickle.dumps([id, pub])
        return e

    def encrypt(self, msg, label=None):
        """
        if not set label , will use self's key
        """
        if not label:
            label = self.label
        if not os.path.exists(os.path.join(self.home, label + ".pub")):
            log.info("can not encrypt , because lack \"{}\" key file".format(label))
            return None
        rsa = Rsa(label)
        log.info("load key from: " + label)
        return rsa.en(msg)

    def decrypt(self, msg, label=None):
        """
        if not set label , will use self's key
        """
        if not label:
            label = self.label
        if not os.path.exists(os.path.join(self.home, label + ".pri")):
            log.info("can not decrypt , because lack \"{}\" key file".format(label))
            return None
        rsa = Rsa(label)
        return rsa.de(msg)


def Format(msg,op='msg',id=None, decoder=None):
    """
    @msg
      if msg is instance of bytes , ok ,will add to tail of data,
      if msg is a str, will encrypt by rsa then add to tail of data.
    @id
      choose a id to use pub key to encrypt, only the id's pri key can decrypt.
    """
    if decoder == 'json' and isinstance(msg, dict):
        msg = json.dumps(msg)
    elif decoder == 'base64':
        if isinstance(msg, bytes):
            msg = base64.b64encode(msg)
        elif isinstance(msg, str):
            msg = base64.b64encode(msg.encode("utf8"))

    if isinstance(msg, str):
        log.info("msg need to encrypt: [key: %s] " % id)
        if isinstance(id, bytes):
            id = id.decode("utf8")
        msg = pubip_rsa.encrypt(msg.encode("utf8"), label=id)

    if not id:
        id = pubip_rsa.label
    if isinstance(op, str):
        op = op.encode('utf8')

    if not decoder:
        decoder = b''
    if isinstance(decoder, str):
        decoder = decoder.encode("utf8")


    if isinstance(id, str):
        id = id.encode("utf8")
    return id + b'--|--' + op + b'--|--' + pubip_rsa.label.encode("utf8") + b'--|--' + decoder + b'--|--'  + msg

def deFormat(bytes):
    Coders = {
        'base64': base64.b64decode,
        'json': lambda x: json.loads(x.decode('utf8')),
        'str': lambda x: x.decode('utf8'),
        'log': lambda x: x.decode("utf8").split("\n")
    }

    id, op, from_id, decoder, msg_ened = bytes.split(b'--|--', 5)
    id = id.decode('utf8','ignore')
    # try to decrypt
    #r = Rsa(id)

    msg = pubip_rsa.decrypt(msg_ened)
    if decoder.decode() in Coders:
        msg = Coders[decoder.decode()](msg)
    result = {
        'id': id,
        'op': op,
        'from_id': from_id,
        'msg': msg,
        'decoder': decoder.decode(),
        'if_rsa': True}
    if not msg:
        result['if_rsa'] = False
    return result

for f in os.listdir(os.path.join(os.getenv("HOME"), "seed")):
    if f.startswith(pubip) and '.pri' in f:
        pubip_rsa = Rsa(f.strip().split(".pri")[0])
        break

if not pubip_rsa:
    pubip_rsa = Rsa(GetIp() + "-" + ''.join([random.choice("abcdef0123456789") for i in range(8) ]))
