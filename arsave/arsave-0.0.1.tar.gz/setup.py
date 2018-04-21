#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# On import la lib
import arsave

# Ceci n'est qu'un appel de fonction. Mais il est très long et comporte beaucoup de paramètres
setup(

    # le nom de notre bibliothèque, tel qu'il apparaitra sur pypi
    name='arsave',

    # la version du code
    version=arsave.__version__,

    # Liste les packages à insérer dans la distribution plutôt que de le faire à la main, on utilise la foncton
    # find_packages() de setuptools qui va cherche tous les packages python recursivement dans le dossier courant.
    # C'est pour cette raison que l'on a tout mis dans un seul dossier: on peut ainsi utiliser cette fonction facilement
    #packages=find_packages(),

    packages = ['arsave'],

    # Notre nom
    author='ClementTr',

    # Notre email, sachant qu'il sera publiquement visible
    author_email='clement.tailleur@gmail.com',

    # Une description courte
    description='My own package',

    # Une description longue, sera affichée pour présenter la lib. Généralement on dump le README ici
    long_description=open('README.md').read(),

    # On peut rajouter une liste de dépendances pour notre lib et même préciser une version.
    #install_requires = ['numpy==1.12.1', 'matplotlib==1.5.3', 'networkx==1.11'],


    # Une url qui pointe vers la page officielle de votre lib
    #url='http://github.com/ClementTr/arsave',

    # Il est d'usage de mettre quelques metadata à propos de sa lib pour que les robots puissent facilement la classer.
    # La liste des marqueurs autorisées est longue: https://pypi.python.org/pypi?%3Aaction=list_classifiers.
    # Il n'y a pas vraiment de règle pour le contenu. Chacun fait un peu comme il le sent. Il y en a qui ne mettent rien.
    classifiers=[
        'Programming Language :: Python',
    	'Development Status :: 1 - Planning',
        'License :: OSI Approved',
        'Natural Language :: French',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Sociology',
    ],

    test_suite = 'tests',

    # C'est un système de plugin, mais on s'en sert presque exclusivement pour créer des commandes, comme 'django-admin'.
    # Par exemple, on peut créer commande 'run-introduction', qui pointe vers introduction().
    # La syntaxe est 'nom-de-commande-a-creer = package.module:fonction'.
    entry_points = {
        'console_scripts': [
            'arsave-run = arsave.introduction:introduction',
        ],
    },

    # A fournir uniquement si notre licence n'est pas listée dans 'classifiers' ce qui est notre cas là
    license='WTFPL'

    # Il y a encore beaucoup de paramètres possibles, mais avec ça on couvre 90% des besoins

)
