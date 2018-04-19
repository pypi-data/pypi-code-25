import gi
import sqlite3 
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from graph_tool.all import *


def get_father_son(path):
	connection = sqlite3.connect(path)
	cursor = connection.cursor()
	cursor.execute("SELECT max(idNoeudPere) FROM grapheGalaxies")
	maxi = cursor.fetchone()
	cursor.execute("SELECT * FROM grapheGalaxies")
	rows = cursor.fetchall()
	connection.close()
	return maxi, rows


def get_authors_date(path):
	connection = sqlite3.connect(path)
	cursor = connection.cursor()
	cursor.execute("SELECT DISTINCT auteur FROM livres")
	authors = cursor.fetchall()
	cursor.execute("SELECT DISTINCT date FROM livres")
	date = cursor.fetchall()
	connection.close()
	return authors, date


def get_filtre(path, choix, inverse, filtre ):
	pass
