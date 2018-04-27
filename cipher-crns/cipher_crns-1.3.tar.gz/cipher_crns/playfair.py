# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 20:26:32 2018

@author: i
"""
import numpy as np

class playfair:
    def find_index(mat,element):
        for i in range(5):
            for j in range(5):
                if mat[i][j] == element:
                    return i,j
                
    def encrypt(key,secret_word):
        secret = list(secret_word)
        
        for i in range(len(secret)):
            if(i>0):
                if(secret[i] == secret[i-1]):
                    secret.insert(i,'X')
                    
        if(len(secret)%2!=0):
            secret.append('X')
        secret = np.split(np.array(secret),len(secret)/2)
        #print(secret)
        
        alphabets = ['A','B','C','D','E','F','G','H','I','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        
        key_to_list = list(key)
        
        unique_list=[]
        
        for i in key_to_list:
            if i not in unique_list:
                unique_list.append(i)
        
        for i in alphabets:
            if i not in unique_list:
                unique_list.append(i)
                
        final_mat = np.split(np.array(unique_list),5)
        #print(final_mat)
        
        encrypt_msg=""
        
        for i in secret:
            first = i[0]
            second = i[1]
            
            x1,y1 = find_index(final_mat,str(first))
            x2,y2 = find_index(final_mat,str(second))
            
            if(x1 == x2):
                encrypt_msg += final_mat[x1][(y1+1)%5]
                encrypt_msg += final_mat[x2][(y2+1)%5]
                #print(1)
                #print(encrypt_msg,final_mat[x1][y1],final_mat[x2][y2])
            elif(y1 == y2):
                print(2)
                encrypt_msg += final_mat[(x1+1)%5][y1]
                encrypt_msg += final_mat[(x2+1)%5][y2]
                #print(encrypt_msg,final_mat[x1][y1],final_mat[x2][y2])
            else:
                encrypt_msg += final_mat[x1][y2]
                encrypt_msg += final_mat[x2][y1]
                #print(encrypt_msg,final_mat[x1][y1],final_mat[x2][y2])
        
        return(encrypt_msg)
    
    
