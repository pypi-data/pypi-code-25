import sqlite3 
import numpy as np

def get_father_son(path):
	connection = sqlite3.connect(path)
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM grapheGalaxies")
	rows = cursor.fetchall()
	connection.close()
	return rows
	
def get_authors_date(path):
	connection = sqlite3.connect(path)
	cursor = connection.cursor()
	cursor.execute("SELECT DISTINCT auteur FROM livres")
	authors = cursor.fetchall()
	cursor.execute("SELECT DISTINCT date FROM livres")
	date = cursor.fetchall()
	connection.close()
	return authors, date
	
def get_node_info(path, father, son):
	connection = sqlite3.connect(path)
	cursor = connection.cursor()
	cursor.execute("SELECT DISTINCT l1.titre, l1.auteur, l1.date, l2.titre, l2.auteur, l2.date \
					FROM grapheReutilisations r, grapheGalaxiesSource s, grapheGalaxiesCible c, livres l1, livres l2\
					WHERE s.idReutilisation = r.rowid and c.idReutilisation = r.rowid and r.idRefSource = l1.rowid and \
						  r.idRefCible = l2.rowid and s.idNoeud = " + str(father) + " and c.idNoeud = " + str(son))
	res = cursor.fetchall()
	connection.close()
	return res[0]

def get_filtre(path, choix, inverse, filtre ):
	###Seulement pere filtré pour le moment
	inv = ""
	connection = sqlite3.connect(path)
	cursor = connection.cursor()

	if inverse:
		inv = "!"

	if choix == "année":
		cursor.execute("SELECT DISTINCT gg.idNoeudPere, gg.idNoeudFils FROM grapheReutilisations gr, grapheGalaxiesSource s, grapheGalaxiesCible c, grapheGalaxies gg, livres l\
								WHERE l.rowid = gr.idRefSource and gr.rowid = s.idReutilisation and  s.idNoeud = gg.idNoeudPere and l.date"+ inv + "= " + str(filtre))
	elif choix == "auteur":
		filtre = "'" + filtre + "'"
		cursor.execute("SELECT DISTINCT gg.idNoeudPere, gg.idNoeudFils FROM grapheReutilisations gr, grapheGalaxiesSource s, grapheGalaxiesCible c, grapheGalaxies gg, livres l\
								WHERE l.rowid = gr.idRefSource and gr.rowid = s.idReutilisation and  s.idNoeud = gg.idNoeudPere and l.auteur" + inv + "= " + filtre)
	rows = cursor.fetchall()
	connection.close()
	
	return rows

def get_text(path, father, son):
	connection = sqlite3.connect(path)
	cursor = connection.cursor()
	cursor.execute("SELECT DISTINCT r.texteSource, r.texteCible FROM grapheReutilisations r, grapheGalaxiesSource s, grapheGalaxiesCible c WHERE s.idReutilisation = c.idReutilisation and s.idReutilisation = r.rowid and s.idNoeud = " + str(father) + " and c.idNoeud = " + str(son))
	text = cursor.fetchall()
	if text == []:
		cursor.execute("SELECT DISTINCT r.texteSource, r.texteCible FROM grapheReutilisations r, grapheGalaxiesSource s, grapheGalaxiesCible c WHERE s.idReutilisation = c.idReutilisation and s.idReutilisation = r.rowid and s.idNoeud = " + str(son) + " and c.idNoeud = " + str(father))
		text = cursor.fetchall()
	return text[0]

def intersection(L):
	new_list = L[0]
	for i in range(1, len(L)):
		t = []
		for e in new_list:
			if e in L[i]:
				t.append(e) 
		new_list = t
	return new_list

if __name__ == '__main__':
	print(get_node_info("small_galaxies.db", 171, 59))



