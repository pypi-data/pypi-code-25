# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 13:00:14 2018

@author: i
"""
from sympy import Matrix
import numpy as np

def encrypt(text,key):
    block_size = len(key)
    
    encrypt_text = ""
    
    if(len(text)%block_size != 0):
        for i in range(len(text)%block_size):
            text+='z'
    i=0
    while(i <= len(text)-1):
        block=[]
        for j in range(block_size):     
            l = [(ord(text[i+j])-ord('a'))%26]
            block.append(l)
        i = i + block_size
        #print(i)
        encrypt_block = np.dot(key, block) % 26
        for e in encrypt_block:
            encrypt_text += chr(e + ord('a'))
    return encrypt_text

def decrypt(text,key):
    block_size = len(key)
    i=0
    decrypt_text = ""
    key_inv = Matrix(key).inv_mod(26)
    key_inv = np.array(key_inv)
    while(i <= len(text)-1):
        block=[]
        for j in range(block_size):     
            l = [(ord(text[i+j])-ord('a'))%26]
            block.append(l)
        i = i + block_size
        #print(i)
        decrypt_block = np.dot(key_inv, block) % 26
        for e in decrypt_block:
            decrypt_text += chr(e + ord('a'))
    return decrypt_text

