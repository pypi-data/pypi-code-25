#!/usr/bin/env python

import binascii         #https://docs.python.org/3/library/binascii.html
import hashlib          #https://docs.python.org/fr/3.6/library/hashlib.html
import lzma             #utilitaire de compression de données basé sur l'algorithme LZMA

from NimingCypher.BaseConverter import HexToBase, BaseToHex
from random import randint as rnd

__all__ = []    #utilisé pour n'autoriser l'accès à aucune fonctions
threshold = 10  #utilisé pour définir le nb d'occurrence minimale nécessaire pour l'utilisation dans la base

def chiffrer(Clear_tx, listes_globales=[]):
    if listes_globales==[]:
        Clear_tx,listes_globales = Clear_tx
    liste_char, liste_pos = listes_globales
    final_tx = ""
    pas_trouver = 0
    for ch in Clear_tx: #pour chaque caractères
        if ch in liste_char: #si le carctère est dans la liste des caractères
            idx = liste_char.index(ch)  #on trouve son index dans la liste
            #on récupère la liste de toute les occurences de ce caractère
            #qui possède le même index que la première liste
            lpos = liste_pos[idx]

            #on choisit une de ces occurence aléatoirement
            position = int(lpos[(rnd(0,len(lpos)-1))])

            #on converti la position en hexa et on l'ajoute
            final_tx += str(hex(position))[2:] + " "
        else: #si le caractère n'existe pas dans la liste
            pas_trouver += 1
            final_tx += "0000 "
    print(str(pas_trouver) + ' caractères non trouvés !')
    return(final_tx[:-1]) #retourne tout sauf le dernier caractère " "

def dechiffrer(Encrypted_tx, TextFromWeb):
    OutText = ""
    for ch in Encrypted_tx.split(" "): #pour chaque bloc hexa
        if ch != '': #vérifie que le bloc soit bien existant
            try:
                OutText+=str(TextFromWeb[int(ch,16)]) #retourne le caractère qui correspond à la position en hexa
            except:
                print("Erreur lors du déchiffrement ")
                OutText+= '?'
    return OutText

def GenSum(FileBytes): #génère un hash en sha256 pour la vérification des fichiers appelé sum
    return hashlib.sha256(FileBytes).hexdigest()

def FileToBase(chemin, alphabet, occurlist):
    file = open(chemin,"rb") # r --> read ; b --> byte
    byte_file = file.read() #stocke le fichier en bytes dans byte_file
    file.close()
    hx_file = binascii.hexlify(byte_file) #on transforme les bytes en hexa
    base_file = HexToBase(hx_file, alphabet, occurlist, threshold) #on utilise la base personnalisée pour économiser de l'espace
    return base_file

def BaseToFile(base_file , path, alphabet, occurlist):#inverse de FileToBase
    try:
        file = open(path,"wb+") # w --> write ; b --> byte ; + --> créer le fichier si inexistant
        hx_file = BaseToHex(base_file, alphabet, occurlist, threshold) #base perso vers hexa
        file.write(binascii.unhexlify(hx_file))#on écrit le fichier en bytes converti auparavant compressé
        file.close()
        return True #aucune erreure
    except:
        return False #une erreure est survenue

def Compress(data): #compression des données
    comp_data = lzma.compress(data)
    return comp_data

def Decompress(data): #décompression des données
    decomp_data = lzma.decompress(data)
    return decomp_data

def ChiffrFile(location, listes): #chiffre le fichier
    liste_char,liste_pos = listes #liste des caractères présents sur le site et toutes les occurences
    base_tx = FileToBase(location, liste_char, liste_pos) #lis le fichier et le converti en base personalisée
    chfr = chiffrer(base_tx, listes) #on chiffre la base (le texte)
    compr_tx = Compress(chfr.encode()) #on compresse le texte chiffré
    return compr_tx

def DeChiffrFile(textencrypted, textfromweb, listes, path): #dechiffre le fichier
    liste_char,liste_pos = listes #liste des caractères présents sur le site et toutes les occurences
    decompress_tx = Decompress(textencrypted).decode() #on décompresse et convertis les bytes en texte
    dechTx = dechiffrer(decompress_tx, textfromweb) #on déchiffre
    return(BaseToFile(dechTx, path, liste_char, liste_pos)) #on retourne la base transformée en texte
