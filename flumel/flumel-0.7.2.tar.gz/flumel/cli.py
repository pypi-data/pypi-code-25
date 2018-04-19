"""
Interface en ligne de commande pour flumel:
* config : création assistée du fichier de conf
* page : génération de la page dédiée de l’instance
* init : execute les 3 tâches précédentes à la suite

Pour un premier lancement, utiliser "init"
"""

import argparse


def user_input(label: str = 'Poursuivre (ctr+c pour annuler)',
               default: str = '') -> str:
    """
    Simplifie la récupération des variables pour la configuration

    Affiche : Question [valeur par défaut] ?
    Retourne : Valeur saisie par l’utilisateur OU valeur par défaut

    Utilisé sans paramètre permet de faire une pause dans l'affichage
    et demander à l'utilisateur de poursuivre
    """
    question = '{label} [{default}] ? '.format(label=label, default=default)
    return str(input(question) or default)


def main():
    """init | config | page"""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('command', help=main.__doc__)
    args = parser.parse_args()
    available_commands = {
        'init': init,
        'config': generate_config,
        'page': generate_page
    }
    try:
        available_commands[args.command]()
    except KeyError:
        print('⚠ Commande inconnue, cli.py --help pour afficher l’aide')


def init():
    """
    Initialisation de l'instance
    Execute generate_config & generate_page
    """
    print(init.__doc__)
    user_input()
    generate_config()
    generate_page()


def generate_config():
    """
    Génération du fichier de configuration de flumel

    * Format des questions: "Question [valeur par défaut] ?"
    * Quand il n’y a pas de valeur par défaut (crochets vides)
    il faut impérativement répondre quelque chose.
    * Une fois généré, le fichier flumel.cfg peut être modifié à la main.
    """
    import configparser
    config = configparser.ConfigParser(interpolation=None)
    config.read('flumel.cfg')
    print(generate_config.__doc__)
    user_input()

    print('# Réglages de l’instance')
    try:
        config.add_section('Instance')
    except configparser.DuplicateSectionError:
        pass
    config.set('Instance', 'Name', user_input('- Nom de l’instance', 'Flumel'))
    config.set('Instance', 'Url', user_input('- URL de l’instance'))
    config.set(
        'Instance', 'Baseline',
        user_input('- Slogan de l’instance',
                   'Encore un moyen de recevoir ses flux RSS par email'))

    print('# Réglages du bot')
    try:
        config.add_section('Bot')
    except configparser.DuplicateSectionError:
        pass
    config.set('Bot', 'Email', user_input('- Adresse email du bot'))

    print('# Réglages IMAP')
    try:
        config.add_section('IMAP')
    except configparser.DuplicateSectionError:
        pass
    config.set('IMAP', 'Host', user_input('- Adresse du serveur IMAP'))
    config.set('IMAP', 'Port',
               user_input('- Port (993 pour SSL, 143 pour StartTLS)', '465'))
    config.set('IMAP', 'Login', user_input('- Identifiant IMAP'))
    config.set('IMAP', 'Password', user_input('- Mot de passe IMAP'))

    print('# Réglages SMTP')
    try:
        config.add_section('SMTP')
    except configparser.DuplicateSectionError:
        pass
    config.set('SMTP', 'Host', user_input('- Adresse du serveur SMTP'))
    config.set('SMTP', 'Port',
               user_input('- Port (465 pour SSL, 587 pour StartTLS) ', '993'))
    config.set('SMTP', 'Login', user_input('- Identifiant SMTP'))
    config.set('SMTP', 'Password', user_input('- Mot de passe SMTP'))

    print('# Commandes')
    try:
        config.add_section('Keywords')
    except configparser.DuplicateSectionError:
        pass
    config.set('Keywords', 'Subscribe',
               user_input('- Pour s’abonner', 'Abonnement'))
    config.set('Keywords', 'Unsubscribe',
               user_input('- Pour se désabonner', 'Désabonnement'))

    print('# Base de données')
    try:
        config.add_section('DB')
    except configparser.DuplicateSectionError:
        pass
    config.set('DB', 'Path',
               user_input('- Nom et chemin de la base', 'flumel.sqlite'))
    config.set('DB', 'Debug', user_input('- Debug activé (yes, no)', 'no'))

    print('# Tâches')
    try:
        config.add_section('Queue')
    except configparser.DuplicateSectionError:
        pass
    config.set('Queue', 'Path',
               user_input('- Nom et chemin de la base', 'huey.sqlite'))
    config.set(
        'Queue', 'Management',
        user_input(
            '- Fréquence de vérification IMAP (*/n = toutes les n minutes)',
            '*/3'))
    config.set(
        'Queue', 'Subscriptions',
        user_input(
            '- Fréquence de vérification des flux (*/n = toutes les n heures)',
            '*/1'))

    print('# Journaux')
    try:
        config.add_section('Logging')
    except configparser.DuplicateSectionError:
        pass
    config.set('Logging', 'Path',
               user_input('- Nom et chemin du journal', 'flumel.log'))
    config.set('Logging', 'Level',
               user_input('- Niveau (DEBUG, INFO, WARN, ERROR, CRITICAL)',
                          'INFO'))

    with open('flumel.cfg', 'w') as fp_config:
        config.write(fp_config)
    print('✓ flumel.cfg généré !')


def generate_page():
    """
    Créer de la page dédiée de l’instance
    web/index.html
    """
    print(generate_page.__doc__)
    user_input()
    from .tasks import page
    page()
    print('✓ index.html créé !')


if __name__ == "__main__":
    main()
