# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 14:30:12 2018

@author: Nirav
"""
class caesar:
    def encrypt(text,key):
        encrypt_text = ""
        for i in text:
            if(i.isupper()):
                encrypt_text += chr(((ord(i) - ord('A')+ key+26)%26)+ord('A'))
            elif(i.islower()):
                encrypt_text += chr(((ord(i) - ord('a')+ key+26)%26)+ord('a'))
            else:
                encrypt_text += i
            
        return encrypt_text
    
    def decrypt(text,key):
        decrypt_text = ""
        for i in text:
            if(i.isupper()):
                decrypt_text += chr(((ord(i) - ord('A')- key+26)%26)+ord('A'))
            elif(i.islower()):
                decrypt_text += chr(((ord(i) - ord('a')- key+26)%26)+ord('a'))
            else:
                decrypt_text += i
            
        return decrypt_text