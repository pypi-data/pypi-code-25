# -*- coding: utf-8 -*-
import time

import galaxies.src.core.database_tools as db


class Noeud:
    """ Permet d'énumérer les noeuds du graphe """
    def __init__(self, step_time):
        self.val = 0
        self.step_time = step_time
        self.tempsIni = time.clock()

    def nouvelle_valeur(self):
        self.val += 1

        # Affichage du temps de construction
        if divmod(self.val, self.step_time)[1] == 0:
            self.temps = time.clock()
            print("Nombre noeuds du graphe: " + str(self.val) +"; temps de construction du graphe pour les " + str(self.step_time) + " derniers noeuds: " + str(self.temps - self.tempsIni))
            self.tempsIni = self.temps


def construction_graphe(database_path: str, step_time: int):
    # Connexion to the database
    connexion = db.connexion(database_path)
    cursor = connexion.cursor()

    # Retrieve all the books and stack them in a node
    node = Noeud(step_time=step_time)
    cursor.execute('''SELECT rowid FROM livres''')
    for id_reference in cursor:
        fusion_sources_cibles(id_reference, connexion, node)

    # Store
    cursor.execute('''INSERT INTO maxNoeud values (?)''', (node.val,))
    connexion.commit()
    connexion.close()
    return node.val


def fusion_sources_cibles(id_ref, connexion, node):
    curseur_source = connexion.cursor()
    curseur_cible = connexion.cursor()
    curseur_source.execute("""
        SELECT ordonneeSource, empanSource, rowid
        FROM grapheReutilisations
        WHERE idRefSource = ?""", id_ref)
    curseur_cible.execute("""
        SELECT ordonneeCible, empanCible, rowid
        FROM grapheReutilisations
        WHERE idRefCible = ?""", id_ref)

    liste_reutilisation_source = curseur_source.fetchall()
    liste_reutilisation_cible = curseur_cible.fetchall()

    liste_reutilisation_marquee = [(X[0], X[1], -X[2]) for X in liste_reutilisation_cible] + liste_reutilisation_source
    liste_reutilisation_marquee.sort()
    resultat = fusion(liste_reutilisation_marquee, node)
    if resultat:
        node.nouvelle_valeur()
    for X in resultat:
        id_reutilisation, id_noeud = X[2], X[3]
        if X[-2] > 0:
            ajout_source(id_reutilisation, id_noeud, curseur_source)
        elif X[-2] < 0:
            ajout_cible(abs(id_reutilisation), id_noeud, curseur_cible)
        else:
            print("Attention, erreur fusion sur noeud", node.val, "avec X=", X)


def fusion(liste_reutilisation, node):
    if liste_reutilisation == []:
        return []
    elif len(liste_reutilisation) == 1:
        return [[liste_reutilisation[0][0], liste_reutilisation[0][1], liste_reutilisation[0][2], node.val]]
    else:
        tete, suivant, *entree = liste_reutilisation
        resultat = []

        while len(entree) >= 1:
            if tete[0] + tete[1] >= suivant[0]:
                nombre_reutilisations = [tete[0], max(tete[1], suivant[1] - tete[0] + suivant[0]), tete[2], node.val]
                resultat = resultat + [nombre_reutilisations]
                tete = [tete[0], max(tete[1], suivant[1] - tete[0] + suivant[0]), suivant[2]]
                suivant = entree.pop(0)
            else:
                nombre_reutilisations = [tete[0], tete[1], tete[2], node.val]
                resultat = resultat + [nombre_reutilisations]
                tete = suivant
                suivant = entree.pop(0)
                node.nouvelle_valeur()
        else:
            if tete[0] + tete[1] >= suivant[0]:
                nombre_reutilisations = [tete[0], max(tete[1], suivant[1] - tete[0] + suivant[0]), tete[2], node.val]
                resultat = resultat + [nombre_reutilisations]
                tete = [tete[0], max(tete[1], suivant[1] - tete[0] + suivant[0]), suivant[2]]
            else:
                nombre_reutilisations = [tete[0], tete[1], tete[2], node.val]
                resultat = resultat + [nombre_reutilisations]
                tete = suivant
                node.nouvelle_valeur()

        return resultat + [[tete[0], tete[1], tete[2], node.val]]


def ajout_source(id_reutilisation, id_noeud, cursor):
    cursor.execute('''INSERT INTO grapheGalaxiesSource values (?, ?)''',
                   (id_reutilisation, id_noeud))


def ajout_cible(id_reutilisation, id_noeud, cursor):
    cursor.execute('''INSERT INTO grapheGalaxiesCible values (?, ?)''',
                   (id_reutilisation, id_noeud))


def sauvegarde_graphe(database_path: str, step_time: int):
    connexion = db.connexion(database_path)
    curseur_arc = connexion.cursor()
    curseur_noeud = connexion.cursor()
    curseur_graphe = connexion.cursor()

    curseur_arc.execute('''SELECT * FROM maxNoeud''')
    maxNoeud = curseur_arc.fetchone()[0]
    n = Noeud(step_time=step_time)
    while n.val < maxNoeud:
        curseur_arc.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (n.val,))
        reutilisation = curseur_arc.fetchone()
        while reutilisation != None:
            curseur_noeud.execute('''SELECT idNoeud FROM grapheGalaxiesCible WHERE idReutilisation = (?)''', (reutilisation[0],))
            nouveau_noeud = curseur_noeud.fetchone()
            curseur_graphe.execute('''INSERT INTO grapheGalaxies values (?,?)''', (n.val, nouveau_noeud[0], ))
            reutilisation = curseur_arc.fetchone()
        n.nouvelle_valeur()
    n = Noeud(step_time=step_time)
    while n.val < maxNoeud:
        curseur_arc.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (n.val,))
        reutilisation = curseur_arc.fetchone()
        while reutilisation != None:
            curseur_noeud.execute('''SELECT idNoeud FROM grapheGalaxiesSource WHERE idReutilisation = (?)''', (reutilisation[0],))
            nouveau_noeud = curseur_noeud.fetchone()
            curseur_graphe.execute('''INSERT INTO grapheGalaxies values (?,?)''', (n.val, nouveau_noeud[0],))
            reutilisation = curseur_arc.fetchone()
        n.nouvelle_valeur()
    connexion.commit()
    connexion.close()


if __name__ == '__main__':
    pass
