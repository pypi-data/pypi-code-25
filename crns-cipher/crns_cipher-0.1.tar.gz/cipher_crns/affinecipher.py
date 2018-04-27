# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 14:48:59 2018

@author: Nirav
"""
class affine:
    def inv(key1):
        for i in range(1,26):
            if(key1*i)%26 == 1:
                return i
        
    
    def encrypt(text,key1,key2):
        encrypt_text = ""
        for i in text:
            if(i.isupper()):
                encrypt_text += chr((((ord(i) - ord('A'))*key1 + key2)%26)+ord('A'))
            elif(i.islower()):
                encrypt_text += chr((((ord(i) - ord('a'))*key1 + key2)%26)+ord('a'))
            else:
                encrypt_text += i
            
        return encrypt_text
    
    def decrypt(text,key1,key2):
        decrypt_text = ""
        key1_inv = inv(key1)
        for i in text:
            if(i.isupper()):
                decrypt_text += chr((((ord(i) - ord('A')- key2)*key1_inv)%26)+ord('A'))
            elif(i.islower()):
                decrypt_text += chr((((ord(i) - ord('a')- key2)*key1_inv)%26)+ord('a'))
            else:
                decrypt_text += i
            
        return decrypt_text