""" Ce module définit l'interface principale utilisée par la CLI et la GUI.
Les méthodes utilisées ici devront être les seules appelables de l'exterieur.
"""
import time
import os

import galaxies.src.core.parser as parser
import galaxies.src.core.database_tools as database_tools
import galaxies.src.core.graphe_galaxies as graphe_galaxies
import galaxies.src.core.extraction_galaxies as extraction_galaxies
from galaxies.src.common.file import delete_existing_files


def create_reuses_database(*, database_src: str, path_file_galaxies: str,
                           path_file_list_galaxies: str,
                           path_file_adjacency_graph: str,
                           path_file_adjacency_graph_transposed: str,
                           path_dir_dest: str,
                           max_book_to_add: int, delimiter: str,
                           encoding_src: str, remove_header: bool,
                           index_src_author: int,
                           index_src_title: int, index_src_date: int,
                           index_src_text_matched: int,
                           index_src_start_byte: int, index_src_end_byte: int,
                           index_dest_author: int, index_dest_title: int,
                           index_dest_date: int, index_dest_text_matched: int,
                           index_dest_start_byte: int,
                           index_dest_end_byte: int,
                           step_nodes_time: int,
                           step_galaxies_time: int,
                           step_number_of_nodes_galaxie: int):
    """ Create the SQLite3 database containing only the useful information the
    software needs to process the graph.
    :param database_src: The path to the database containing all the reuses'.
    This database must be in the TSV, TAB or CSV format.
    :param path_file_galaxies: The path to the SQLite3 which is gonna be created.
    :param path_file_list_galaxies: The path to the file containing the list of
    all galaxies.
    :param path_file_adjacency_graph: The path of the pickle file containing the
    adjacency graph.
    :param path_file_adjacency_graph_transposed: The path of the pickle file
    containing the transposed of the adjacency graph.
    :param path_dir_dest: The directory containing all the files which'll be
    created by the software.
    :param max_book_to_add: The maximal number of books to add in the SQLite3
    database. If negative, all the books possible are added.
    :param delimiter: The delimiter of the source database containing all the
    reuses'.
    :param encoding_src: The encoding of the source database containing all the
    reuses'.
    :param remove_header: Remove the header present in the source database
    contaning all the reuses'.
    :param index_src_author: The index in the source database matching a column
    containing the author of a source reuse.
    :param index_src_title: The index in the source database matching a column
    containing the title of a source reuse.
    :param index_src_date: The index in the source database matching a column
    containing the date of a source reuse.
    :param index_src_text_matched: The index in the source database matching a
    column containing the text matched of a source reuse.
    :param index_src_start_byte: The index in the source database matching a
    column containing the start byte of a source reuse.
    :param index_src_end_byte: The index in the source database matching a
    column containing the end byte of a source reuse.
    :param index_dest_author: The index in the source database matching a column
    containing the author of a destination (or target) reuse.
    :param index_dest_title: The index in the source database matching a column
    containing the title of a destination (or target) reuse.
    :param index_dest_date: The index in the source database matching a column
    containing the date of a destination (or target) reuse.
    :param index_dest_text_matched: The index in the source database matching a
    column containing the text matched of a destination (or target) reuse.
    :param index_dest_start_byte: The index in the source database matching a
    column containing the start byte of a destination (or target) reuse.
    :param index_dest_end_byte: The index in the source database matching a
    column containing the end byte of a destination (or target) reuse.
    :param step_nodes_time: Print the building time every amount of
    step_nodes_time nodes processed.
    """
    # Delete all existing databases to prevent unwanted errors
    delete_existing_files(path_file_galaxies,
                          path_file_list_galaxies,
                          path_file_adjacency_graph,
                          path_file_adjacency_graph_transposed)

    # Create result dir if it doesn't exists
    os.makedirs(path_dir_dest, exist_ok=True)

    # Creation de la structure de la base
    t1 = time.clock()
    database_tools.create_database(database_path=path_file_galaxies)
    t2 = time.clock()
    print("Temps de construction de la base de données :", t2 - t1, "sec.")

    # Remplissage de la base avec les livres contenus dans le fichier passé en
    # paramètre
    t1 = time.clock()
    parser.parse_reuse_file(database_source=database_src,
                            database_dest=path_file_galaxies,
                            max_book_to_add=max_book_to_add,
                            delimiter=delimiter,
                            encoding=encoding_src,
                            header=remove_header,
                            index_src_author=index_src_author,
                            index_src_title=index_src_title,
                            index_src_date=index_src_date,
                            index_src_text_matched=index_src_text_matched,
                            index_src_start_byte=index_src_start_byte,
                            index_src_end_byte=index_src_end_byte,
                            index_dest_author=index_dest_author,
                            index_dest_title=index_dest_title,
                            index_dest_date=index_dest_date,
                            index_dest_text_matched=index_dest_text_matched,
                            index_dest_start_byte=index_dest_start_byte,
                            index_dest_end_byte=index_dest_end_byte)
    t2 = time.clock()
    print("Temps de lecture du fichier source : " + str(t2 - t1) + "sec.")

    # Création des galaxies
    t1 = time.clock()
    maxNoeud = graphe_galaxies.construction_graphe(database_path=path_file_galaxies,
                                                   step_time=step_nodes_time)
    t2 = time.clock()
    print("Temps de construction du graphe: " + str(t2 - t1) + " secondes")

    # Sauvegarde du graphe
    t1 = time.clock()
    graphe_galaxies.sauvegarde_graphe(database_path=path_file_galaxies,
                                      step_time=step_nodes_time)
    t2 = time.clock()
    print("Temps de sauvegarde du graphe: " + str(t2 - t1) + " secondes")

    if maxNoeud == 0:
        maxNoeud = database_tools.max_nodes(path_file_galaxies)

    # Extraction des composantes connexes
    t1 = time.clock()
    extraction_galaxies.extraction_composantes_connexes_(path_file_galaxies=path_file_galaxies,
                                                         path_file_list_galaxies=path_file_list_galaxies,
                                                         maxNoeud=maxNoeud,
                                                         step_number_of_nodes_galaxie=step_number_of_nodes_galaxie)
    t2 = time.clock()
    print("Temps total d'extraction des composantes connexes:", t2 - t1, "sec.")


# TODO: Supprimer toutes les methodes ci-dessous 
def impressionTexteGUI(n, p, path):
    path_list_galaxies = os.path.join(os.path.dirname(path), "list_galaxies")
    res = "Composante " + n + ":\n\n"
    q = int(p)
    L = extraction_galaxies.textes_galaxie(n, path, path_list_galaxies)
    while L != set() and (q > 0 or p == 0):
        E = L.pop()
        res += "- " + str(E) + "\n"
        q -= 1
    return res


def extractionComposantes():
    maxNoeud = database_tools.max_nodes()
    t1 = time.clock()
    extraction_galaxies.extraction_composantes_connexes_(maxNoeud)
    t2 = time.clock()
    print("Temps total d'extraction des composantes connexes: " +
          str(t2 - t1) + "sec.")


def impressionTexte(numero_composante, p):
    q = p
    L = extraction_galaxies.textes_galaxie(numero_composante)

    while L != set() and (q > 0 or p == 0):
        E = L.pop()
        print("- " + str(E))
        q -= 1


def impressionTexteLongueur(numero_composante, p):
    q = p
    L = sorted(extraction_galaxies.textes_galaxie(numero_composante),
               key=lambda reference: len(reference))

    while L != [] and (q > 0 or p == 0):
        E = L.pop()
        print("- " + str(E))
        q -= 1


def impressionTexteEtReferenceLongueur(numero_composante, p):
    q = p
    L = sorted(extraction_galaxies.textes_et_references_galaxie(numero_composante),
               key=lambda reference: len(reference[0]))

    while L != [] and (q > 0 or p == 0):
        E = L.pop()
        print("- " + str(E[0]) + " références: " + str(E[1]))
        q -= 1


def impressionTexteEtReference(numero_composante, p):
    q = p
    L = extraction_galaxies.textes_et_references_galaxie(numero_composante)

    while L != set() and (q > 0 or p == 0):
        E = L.pop()
        print("- " + str(E[0]) + " références: " + str(E[1]))
        q -= 1


def impressionTexteEtReferenceAnciennete(numero_composante, p):
    q = p
    L = sorted(extraction_galaxies.textes_et_references_galaxie(numero_composante),
               key=lambda reference: str(reference[1][2]))

    while L != [] and (q > 0 or p == 0):
        E = L[0]
        L = L[1:]
        print("- " + str(E[0]) + " références: " + str(E[1]))
        q -= 1


if __name__ == '__main__':
    pass
