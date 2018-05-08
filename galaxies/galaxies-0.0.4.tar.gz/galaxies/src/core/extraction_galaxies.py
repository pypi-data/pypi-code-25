# -*- coding: utf-8 -*-
import time
import shelve

import galaxies.src.core.database_tools as db


__author__ = 'Jean-Gabriel Ganascia'


class Galaxie:
    """ permet d'énumérer composantes connexes """
    def __init__(self, path_file_galaxies: str, path_file_list_galaxies: str,
                 step_time: int):
        self.val = 0
        self.compositionGalaxie = dict()
        self.tempsIni = time.clock()
        self.step_time = step_time
        self.path_file_galaxies = path_file_galaxies
        self.path_file_list_galaxies = path_file_list_galaxies[:-3]

    def nouvelle_valeur(self):
        self.val += 1
        if divmod(self.val, self.step_time)[1] == 0:
            self.temps = time.clock()
            print("Nombre galaxies: " + str(self.val) +"; temps de construction des " + str(self.step_time) + " dernières galaxies: " + str(self.temps - self.tempsIni))
            self.tempsIni = self.temps

    def noeuds_galaxie(self, n, L):
        self.compositionGalaxie[n] = L
        return len(L)

    def save(self):
        print(self.path_file_list_galaxies)
        dict = shelve.open(self.path_file_list_galaxies)
        x = 0
        while x < self.val:
            dict[str(x)] = self.compositionGalaxie[x]
            x += 1
        dict['nbreGalaxies'] = self.val
        dict.close()

    def rangement(self):
        tr = time.clock()
        print("         Extraction des galaxies terminées; opérations de rangement...")
        connexion = db.connexion(self.path_file_galaxies)
        curseur2 = connexion.cursor()
        curseur2.execute('''INSERT INTO nombreGalaxies values (?)''', (str(self.val),))
        print("Nombre de galaxies: "+str(self.val))
        i = 0
        while i < self.val:
            lnoeuds = self.compositionGalaxie[i]
            n = len(lnoeuds)
            longueur = 0
            for texte in texte_galaxie(i, curseur2, self.path_file_list_galaxies + '.db'):
                longueur += len(texte)
            curseur2.execute('''DELETE from degreGalaxies WHERE idGalaxie = ?''', (str(i),))
            curseur2.execute('''INSERT INTO degreGalaxies values (?,?,?,?)''', (str(i),str(n),str(longueur),str(int(longueur/n)),))
            i += 1
        connexion.commit()
        connexion.close()
        trf = time.clock()
        print("             ... fin des opérations de rangements. Durée: "+str(trf - tr)+" secondes.")


class NoeudMarques:
    def __init__(self, max):
        self.noeuds = dict()
        self.maxNoeud = max
        n = 0
        while n < max:
            self.noeuds[n] = 'non'
            n += 1

    def noeud_non_visite(self, noeudCourant):
        n = noeudCourant
        while n < self.maxNoeud:
            if self.noeuds[n] == 'non':
                return n
            else:
                n += 1
        return None

    def affectation_galaxie(self, n, g):
        if self.noeuds[n] != 'non':
            print("Erreur sur affectation galaxie au noeud " + str(n) + " - précédente affectation: " + str(self.noeuds[str(n)]))
            return 'erreur'
        else:
            self.noeuds[n] = g.val

    def galaxie(self, n):
        g = self.noeuds[n]
        if g == 'non':
            return 'erreur'
        else:
            return g


def extraction_composantes_connexes(path_file_galaxies: str,
                                    path_file_list_galaxies: str,
                                    path_file_adjacency_graph: str,
                                    path_file_adjacency_graph_transposed: str,
                                    maxNoeud: int,
                                    step_number_of_nodes_galaxie):
    graphe = shelve.open(path_file_adjacency_graph)
    graphe_t = shelve.open(path_file_adjacency_graph_transposed)
    noeuds = NoeudMarques(maxNoeud)
    galaxie = Galaxie(path_file_galaxies, path_file_list_galaxies, step_number_of_nodes_galaxie)
    nouveauNoeud = noeuds.noeud_non_visite(0)
    while nouveauNoeud != None:  # < maxNoeud:
        galaxie.noeuds_galaxie(galaxie.val, composante_connexe(nouveauNoeud, galaxie, graphe, graphe_t, noeuds))
        galaxie.nouvelle_valeur()
        nouveauNoeud = noeuds.noeud_non_visite(nouveauNoeud)
    graphe_t.close()
    graphe.close()
    galaxie.save()
    galaxie.rangement()
    return galaxie


def composante_connexe(N, g, graphe, graphe_t, noeuds):
    E_noeuds = set()
    E_noeuds.add(N)
    noeudsVisites = set()
    while E_noeuds.__len__() != 0 :
        E_noeuds = E_noeuds.difference(noeudsVisites)
        E = E_noeuds.pop()
        if not E in noeudsVisites:
            noeuds.affectation_galaxie(E, g)
            E_noeuds.update(fils(E, graphe, graphe_t))
            noeudsVisites.add(E)

        E_noeuds = E_noeuds.difference(noeudsVisites)
        if E_noeuds.intersection(noeudsVisites) != set():
            print("attention!! Noeud "+str(E))
    return noeudsVisites


def fils(X, graphe, graphe_t):
    return graphe[str(X)] + graphe_t[str(X)]


def extraction_composantes_connexes_(path_file_galaxies, path_file_list_galaxies, maxNoeud, step_number_of_nodes_galaxie):
    # Connexion to the database
    connexion = db.connexion(path_file_galaxies)
    cursor = connexion.cursor()

    noeuds = NoeudMarques(maxNoeud)
    galaxie = Galaxie(path_file_galaxies, path_file_list_galaxies , step_number_of_nodes_galaxie)
    tg1 = time.clock()
    nouveauNoeud = noeuds.noeud_non_visite(0)
    nbre_noeuds = 0
    nbre_noeuds_mod = 0

    while nouveauNoeud != None:  # < maxNoeud:
        nbre_noeuds = nbre_noeuds + galaxie.noeuds_galaxie(galaxie.val, composante_connexe_(nouveauNoeud, galaxie, cursor, noeuds))
        if divmod(nbre_noeuds, step_number_of_nodes_galaxie)[0] > nbre_noeuds_mod:
            nbre_noeuds_mod = divmod(nbre_noeuds, step_number_of_nodes_galaxie)[0]
            tg2 = time.clock()
            print("Nombre total de nœuds traités: "+str(nbre_noeuds)+" - Nombre de galaxies constuites: "+str(galaxie.val)+" - temps: "+str(tg2 - tg1)+ "sec.")
            tg1 = tg2
        galaxie.nouvelle_valeur()
        nouveauNoeud = noeuds.noeud_non_visite(nouveauNoeud)
    galaxie.save()
    galaxie.rangement()
    connexion.close()
    return galaxie


def composante_connexe_(N, g, curseur, noeuds):
    E_noeuds = set()
    E_noeuds.add(N)
    noeudsVisites = set()
    while E_noeuds.__len__() != 0 :
        E = E_noeuds.pop()
        if not E in noeudsVisites:
            noeuds.affectation_galaxie(E, g)
            E_noeuds.update(fils_(E, curseur))
            noeudsVisites.add(E)
    return noeudsVisites


def degre_galaxie(G, curseur):
    curseur.execute('''SELECT degreGalaxie FROM degreGalaxies WHERE idGalaxie = (?)''', (G,))
    return curseur.fetchone()[0]


def fils_(X, curseur):
    curseur.execute('''SELECT idNoeudFils FROM grapheGalaxies WHERE idNoeudPere = (?)''', (X,))
    L = []
    for X in curseur.fetchall():
        L.append(X[0])
    return L


def cible(arc, curseur):
    curseur.execute('''SELECT idNoeud FROM grapheGalaxiesCible WHERE idReutilisation = (?)''', (arc,))
    return curseur.fetchall()


def source(arc, curseur):
    curseur.execute('''SELECT idNoeud FROM grapheGalaxiesSource WHERE idReutilisation = (?)''', (arc,))
    return curseur.fetchall()


def composantes_extraites(galaxies_database_path):
    try:
        return shelve.open(galaxies_database_path)['nbreGalaxies']
    except Exception:
        return None


def textes_galaxie(numero, path, path_file_list_galaxies):
    # TODO: Il ne faut JAMAIS le .db dans le nom de fichier
    print("DEBUG", path_file_list_galaxies)
    dirGalaxies = shelve.open(path_file_list_galaxies)

    ListeNoeuds = dirGalaxies[str(numero)]
    dirGalaxies.close()
    connexion = db.connexion(path)
    curseur = connexion.cursor()
    reutilisations = set()
    for Noeud in ListeNoeuds:
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
    textes = set()
    for idReutilisation in reutilisations:
        curseur.execute('''SELECT texteSource, idRefSource FROM grapheReutilisations WHERE rowid = (?)''', (str(idReutilisation),))
        textes.add(curseur.fetchall()[0][0])
        curseur.execute('''SELECT texteCible, idRefCible FROM grapheReutilisations WHERE rowid = (?)''', (str(idReutilisation),))
        textes.add(curseur.fetchall()[0][0])
    connexion.close()
    return textes


def texte_galaxie(numero, curseur, path_file_list_galaxies):
    path_file_list_galaxies = path_file_list_galaxies[:-3] # TODO: Il ne faut JAMAIS le .db dans le nom de fichier
    dirGalaxies = shelve.open(path_file_list_galaxies)

    ListeNoeuds = dirGalaxies[str(numero)]
    dirGalaxies.close()
    reutilisations = set()
    for Noeud in ListeNoeuds:
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
    textes = set()
    for idReutilisation in reutilisations:
        curseur.execute('''SELECT texteSource, idRefSource FROM grapheReutilisations WHERE rowid = (?)''', (str(idReutilisation),))
        textes.add(curseur.fetchall()[0][0])
        curseur.execute('''SELECT texteCible, idRefCible FROM grapheReutilisations WHERE rowid = (?)''', (str(idReutilisation),))
        textes.add(curseur.fetchall()[0][0])
    return textes


def auteurs_galaxie(numero, path_file_galaxies, path_file_list_galaxies):
    path_file_list_galaxies = path_file_list_galaxies[:-3] # TODO: Il ne faut JAMAIS le .db dans le nom de fichier
    dirGalaxies = shelve.open(path_file_list_galaxies)

    ListeNoeuds = dirGalaxies[str(numero)]
    dirGalaxies.close()
    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()
    reutilisations = set()
    for Noeud in ListeNoeuds:
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
    auteurs = set()
    for idReutilisation in reutilisations:
        curseur.execute('''SELECT idRefSource FROM grapheReutilisations WHERE rowid = (?)''',
                        (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT auteur FROM livres WHERE rowid = (?)''', (t1[0],))
        auteurs.add(curseur.fetchall()[0][0])
        curseur.execute('''SELECT idRefCible FROM grapheReutilisations WHERE rowid = (?)''',
                        (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT auteur FROM livres WHERE rowid = (?)''', (t1[0],))
        auteurs.add(curseur.fetchall()[0][0])
    connexion.close()
    return auteurs


def presence_auteur_galaxie_liste_noeuds(auteur, listeNoeuds, path_file_galaxies):
    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()
    reutilisations = set()
    for Noeud in listeNoeuds:
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
    for idReutilisation in reutilisations:
        curseur.execute('''SELECT idRefSource FROM grapheReutilisations WHERE rowid = (?)''',
                        (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT auteur FROM livres WHERE rowid = (?)''', (t1[0],))
        if auteur in str.lower(curseur.fetchall()[0][0]):
            return auteur
        curseur.execute('''SELECT idRefCible FROM grapheReutilisations WHERE rowid = (?)''',
                        (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT auteur FROM livres WHERE rowid = (?)''', (t1[0],))
        if auteur in str.lower(curseur.fetchall()[0][0]):
            return auteur
    connexion.close()
    return ()


def presence_liste_nom_auteur_dans_galaxie_liste_noeuds(LAuteurs, listeNoeuds, path_file_galaxies):
    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()
    reutilisations = set()
    for Noeud in listeNoeuds:
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
    for idReutilisation in reutilisations:
        curseur.execute('''SELECT idRefSource FROM grapheReutilisations WHERE rowid = (?)''',
                        (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT auteur FROM livres WHERE rowid = (?)''', (t1[0],))
        if tout_dans(LAuteurs, str.lower(curseur.fetchall()[0][0])):
            return LAuteurs
        curseur.execute('''SELECT idRefCible FROM grapheReutilisations WHERE rowid = (?)''',
                        (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT auteur FROM livres WHERE rowid = (?)''', (t1[0],))
        if tout_dans(LAuteurs, str.lower(curseur.fetchall()[0][0])):
            return LAuteurs
    connexion.close()
    return ()


def tout_dans(L, F):
    for X in L:
        if X not in F:
            return ()
    return L


def galaxies_auteur(Auteur, path_file_galaxies, path_file_list_galaxies):
    nomAuteur = str.lower(Auteur)
    path_file_list_galaxies = path_file_list_galaxies[:-3] # TODO: Il ne faut JAMAIS le .db dans le nom de fichier
    dirGalaxies = shelve.open(path_file_list_galaxies)
    nbreGalaxies = dirGalaxies['nbreGalaxies']

    listeGalaxiesAuteur=[]
    for X in range(0, nbreGalaxies):
        if presence_auteur_galaxie_liste_noeuds(nomAuteur, dirGalaxies[str(X)], path_file_galaxies):
            listeGalaxiesAuteur.append(X)
    dirGalaxies.close()
    return listeGalaxiesAuteur


def galaxies_liste_noms_auteur(LNomsAuteur, path_file_galaxies, path_file_list_galaxies):
    LNomsAuteurMin = []
    for nomAuteur in LNomsAuteur:
        LNomsAuteurMin.append(str.lower(nomAuteur))
    path_file_list_galaxies = path_file_list_galaxies[:-3] # TODO: Il ne faut JAMAIS le .db dans le nom de fichier
    dirGalaxies = shelve.open(path_file_list_galaxies)
    nbreGalaxies = dirGalaxies['nbreGalaxies']
    listeGalaxiesAuteur=[]
    for X in range(0, nbreGalaxies):
        if presence_liste_nom_auteur_dans_galaxie_liste_noeuds(LNomsAuteurMin, dirGalaxies[str(X)], path_file_galaxies):
            listeGalaxiesAuteur.append(X)
    dirGalaxies.close()
    return listeGalaxiesAuteur


def galaxies_listes_noms_auteurs(LNomsAuteurs, path_file_galaxies, path_file_list_galaxies):
    """ ATTENTION, L'ARGUMENT EST UNE LISTE DE LISTES """
    LNomsAuteursMin = []
    for nomsAuteur in LNomsAuteurs:
        LNomsAuteurMin=[]
        for nomAuteur in nomsAuteur:
            LNomsAuteurMin.append(str.lower(nomAuteur))
        LNomsAuteursMin.append(LNomsAuteurMin)
    path_file_list_galaxies = path_file_list_galaxies[:-3] # TODO: Il ne faut JAMAIS le .db dans le nom de fichier
    dirGalaxies = shelve.open(path_file_list_galaxies)
    nbreGalaxies = dirGalaxies['nbreGalaxies']
    listeGalaxiesAuteur=[]
    for X in range(0, nbreGalaxies):
        LNoeuds = dirGalaxies[str(X)]
        if presence_auteurs_liste_noeuds(LNomsAuteursMin, LNoeuds, path_file_galaxies):
            listeGalaxiesAuteur.append(X)
    dirGalaxies.close()
    return listeGalaxiesAuteur


def presence_auteurs_liste_noeuds(LNomsAuteurs, LNoeuds, path_file_galaxies):
    for LNomsAuteurMin in LNomsAuteurs:
        if not presence_liste_nom_auteur_dans_galaxie_liste_noeuds(LNomsAuteurMin, LNoeuds, path_file_galaxies):
            return ()
    return True


def ordonner(LGalaxies, path_file_galaxies):
    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()
    L = sorted(LGalaxies, key=lambda Galaxie: -degre_galaxie(Galaxie, curseur))
    connexion.close()
    return L


def galaxies_auteur_ordonnees(Auteur, path_file_galaxies, path_file_list_galaxies):
    return ordonner(galaxies_auteur(Auteur, path_file_galaxies, path_file_list_galaxies), path_file_galaxies)


def galaxies_noms_auteur_ordonnees(LNomsAuteur, path_file_galaxies, path_file_list_galaxies):
    return ordonner(galaxies_liste_noms_auteur(LNomsAuteur, path_file_galaxies, path_file_list_galaxies), path_file_galaxies)


def galaxies_noms_auteurs_ordonnees(LNomsAuteurs, path_file_galaxies, path_file_list_galaxies):
    return ordonner(galaxies_listes_noms_auteurs(LNomsAuteurs, path_file_galaxies, path_file_list_galaxies), path_file_galaxies)


def presence_mot_titre_galaxie_liste_noeuds(Mot, listeNoeuds, path_file_galaxies):
    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()
    reutilisations = set()
    for Noeud in listeNoeuds:
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        # print("Noeud: " + str(Noeud[0]) + " - arcs: " + str(L))
        if L != []:
            reutilisations.add(L[0][0])
    # print("Ensemble des réutilisations: "+ str(reutilisations))
    for idReutilisation in reutilisations:
        curseur.execute('''SELECT idRefSource FROM grapheReutilisations WHERE rowid = (?)''',
                        (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT titre FROM livres WHERE rowid = (?)''', (t1[0],))
        if Mot in str.lower(curseur.fetchall()[0][0]):
            return Mot
        curseur.execute('''SELECT idRefCible FROM grapheReutilisations WHERE rowid = (?)''',
                        (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT titre FROM livres WHERE rowid = (?)''', (t1[0],))
        if Mot in str.lower(curseur.fetchall()[0][0]):
            return Mot
    connexion.close()
    return ()


def galaxies_titre_mot(Mot, path_file_galaxies, path_file_list_galaxies):
    nomMot = str.lower(Mot)
    path_file_list_galaxies = path_file_list_galaxies[:-3] # TODO: Il ne faut JAMAIS le .db dans le nom de fichier
    dirGalaxies = shelve.open(path_file_list_galaxies)
    nbreGalaxies = dirGalaxies['nbreGalaxies']

    listeGalaxiesMot=[]
    for X in range(0, nbreGalaxies):
        if presence_mot_titre_galaxie_liste_noeuds(nomMot, dirGalaxies[str(X)], path_file_galaxies):
            listeGalaxiesMot.append(X)
    dirGalaxies.close()
    return listeGalaxiesMot


def presenceAuteurGalaxie(nom, Galaxie, path_file_galaxies, path_file_list_galaxies):
    S = auteurs_galaxie(Galaxie, path_file_galaxies, path_file_list_galaxies)
    for X in S:
        if nom in str.lower(X):
            return nom
    return ()


def textes_et_references_galaxie(numero, path_file_galaxies, path_file_list_galaxies):
    path_file_list_galaxies = path_file_list_galaxies[:-3] # TODO: Il ne faut JAMAIS le .db dans le nom de fichier
    dirGalaxies = shelve.open(path_file_list_galaxies)

    ListeNoeuds = dirGalaxies[str(numero)]
    dirGalaxies.close()
    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()
    reutilisations = set()
    for Noeud in ListeNoeuds:
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
    textes = set()
    for idReutilisation in reutilisations:
        curseur.execute('''SELECT texteSource, idRefSource FROM grapheReutilisations WHERE rowid = (?)''', (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT auteur, titre, date FROM livres WHERE rowid = (?)''', (t1[1],))
        textes.add((t1[0],curseur.fetchall()[0]))
        curseur.execute('''SELECT texteCible, idRefCible FROM grapheReutilisations WHERE rowid = (?)''', (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT auteur, titre, date FROM livres WHERE rowid = (?)''', (t1[1],))
        textes.add((t1[0], curseur.fetchall()[0]))
    connexion.close()
    return textes


def textes_liste_noeuds(ListeNoeuds, path_file_galaxies):
    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()
    reutilisations = set()
    for noeud in ListeNoeuds:
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
    textes = set()
    for id_reutilisation in reutilisations:
        curseur.execute('''SELECT texteSource, idRefSource FROM grapheReutilisations WHERE rowid = (?)''', (str(id_reutilisation),))
        textes.add(curseur.fetchall()[0][0])
        curseur.execute('''SELECT texteCible, idRefCible FROM grapheReutilisations WHERE rowid = (?)''', (str(id_reutilisation),))
        textes.add(curseur.fetchall()[0][0])
    connexion.close()
    return textes


def textes_et_references_liste_noeuds(ListeNoeuds, path_file_galaxies):
    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()
    reutilisations = set()
    for Noeud in ListeNoeuds:
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
    textes = set()
    for idReutilisation in reutilisations:
        curseur.execute('''SELECT texteSource, idRefSource FROM grapheReutilisations WHERE rowid = (?)''', (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT auteur, titre, date FROM livres WHERE rowid = (?)''', (t1[1],))
        textes.add((t1[0],curseur.fetchall()[0]))
        curseur.execute('''SELECT texteCible, idRefCible FROM grapheReutilisations WHERE rowid = (?)''', (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT auteur, titre, date FROM livres WHERE rowid = (?)''', (t1[1],))
        textes.add((t1[0], curseur.fetchall()[0]))
    connexion.close()
    return textes


def textes_et_references_liste_noeuds_avec_noeuds(ListeNoeuds, path_file_galaxies):
    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()
    reutilisations = set()
    for Noeud in ListeNoeuds:
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add((L[0][0],Noeud))
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add((L[0][0], Noeud))
    textes = set()
    for idReutilisation in reutilisations:
        curseur.execute('''SELECT texteSource, idRefSource FROM grapheReutilisations WHERE rowid = (?)''', (str(idReutilisation[0]),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT auteur, titre, date FROM livres WHERE rowid = (?)''', (t1[1],))
        textes.add((t1[0],curseur.fetchall()[0], idReutilisation[1]))
        curseur.execute('''SELECT texteCible, idRefCible FROM grapheReutilisations WHERE rowid = (?)''', (str(idReutilisation[0]),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT auteur, titre, date FROM livres WHERE rowid = (?)''', (t1[1],))
        textes.add((t1[0], curseur.fetchall()[0], idReutilisation[1]))
    connexion.close()
    return textes


if __name__ == '__main__':
    pass
