#!/usr/bin/env python
# Script to sync db and/or data from remote host
#
# Brainstorm S.n.c - http://brainstorm.it
# author: Mario Orlandi, 2017

from __future__ import absolute_import

import os
import sys
import argparse
import logging
import datetime
import traceback

# from six.moves import configparser
# from six.moves import input

try:
    from configparser import ConfigParser
except:
    from ConfigParser import ConfigParser

try:
    # this raw_input is not converted by 2to3
    term_input = raw_input
except NameError:
    term_input = input


def get_version():
    try:
        import sitesync
        return sitesync.__version__
    except:
        return '???'


logger = logging.getLogger(__name__)
args = None
config = None


def conf(section, item):
    """
    Retrieve item from parsed config file
    """
    return config.get(section, item).strip()


default_config = """
[general]
# app_type = django|wordpress
app_type={app_type}
# db_type = postgresql|mysql
db_type={db_type}
use_gzip=True

[ssh]
host={project}.it
user={project}
options=-p 22
sudo=True
sudo_user={sudo_user}

[remote]
url=http://{project}.it

[remote_db]
name={project}
user={project}
#search_1=SEARCH_STRING
#replace_1=REPLACE_STRING
#search_2=SEARCH_STRING
#replace_2=REPLACE_STRING
#...

[remote_data]
owner={project}
data_folder=/home/{project}/{data_folder}
exclude=CACHE/

[local]
url=http://{project}.local
dump_folder={cwd}/dumps

[local_db]
name={project}
user={project}

[local_data]
data_folder={cwd}/{data_folder}
"""


def create_default_config_file(config_filename):

    cwd = os.getcwd()
    project = os.path.split(cwd)[-1]

    # Guess app type:
    # if cwd contains a folder named 'www', assume 'wordpress';
    # otherwise, assume 'django'
    app_type = 'django'
    if os.path.isdir(os.path.join(cwd, 'www')):
        app_type = 'wordpress'

    # Guess db type:
    # for wordpress app, assume 'mysql';
    # otherwise, assume 'postgresql'
    if app_type == 'wordpress':
        db_type = 'mysql'
        sudo_user = 'root'
        data_folder = 'www/wordpress'
    else:
        db_type = 'postgresql'
        sudo_user = 'postgres'
        data_folder = 'public/media'

    text = default_config.format(
        project=project,
        cwd=cwd,
        app_type=app_type,
        db_type=db_type,
        sudo_user=sudo_user,
        data_folder=data_folder,
    )

    with open(config_filename, 'w') as configfile:
        configfile.write(text)


def setup_logger(verbosity):
    """
    Set logger level based on verbosity option
    """
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(module)s| %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if verbosity == 0:
        logger.setLevel(logging.WARN)
    elif verbosity == 1:  # default
        logger.setLevel(logging.INFO)
    elif verbosity > 1:
        logger.setLevel(logging.DEBUG)

    # verbosity 3: also enable all logging statements that reach the root logger
    if verbosity > 2:
        logging.getLogger().setLevel(logging.DEBUG)


def assure_path_exists(path):
    if not os.path.exists(path):
        logger.info('Creating folder "%s"' % path)
        os.makedirs(path)


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = term_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


def is_true(str_flag):
    str_flag = str_flag.strip()
    if str_flag is None:
        return False
    return str_flag.lower() in ['true', '1', 't', 'y', 'yes', ]


def run_command(command):
    dry_run = args.dry_run
    interactive = not args.quiet
    if dry_run:
        print("\x1b[1;37;40m# " + command + "\x1b[0m")
    else:
        print("\x1b[1;37;40m" + command + "\x1b[0m")

        if interactive and not query_yes_no("Proceed ?"):
            raise Exception("Interrupted by user")

        rc = os.system(command)
        if rc != 0:
            raise Exception(command)


def build_ssh_command(command):
    user = conf('ssh', 'user')
    host = conf('ssh', 'host')
    options = conf('ssh', 'options')

    # start with "ssh user@host"
    ssh_command = "ssh "
    if options:
        ssh_command += options + " "
    if user:
        ssh_command += user + '@'
    ssh_command += host

    sudo = conf('ssh', 'sudo')
    if is_true(sudo):
        # command --> "sudo -u sudo_user command"
        command = "sudo -u %s %s" % (conf('ssh', 'sudo_user'), command)

    # "ssh user@host command"
    return '%s "%s"' % (ssh_command, command)


def collect_search_replace_specs(section):
    """
    Scan specified config section for items as:

        search_N=xxx
        replace_N=yyy

    and return:

        [
            ('xxx', 'yyy'),
            ...
        ]
    """
    sr = []

    # Example:
    # ['search_2', 'search_1', 'search_3']
    search_options = [item for item in config.options(section) if item.startswith('search_')]

    # Example:
    # [1, 2, 3]
    search_indexes = [int(option[7:]) for option in search_options]
    search_indexes.sort()

    # Collect search/replace tuples
    for index in search_indexes:
        sr.append(
            (
                conf(section, 'search_' + str(index)),
                conf(section, 'replace_' + str(index)),
            )
        )

    return sr


def local_dumps_target_folder():
    """
    Return the local target folder for all dumps.

    If base folder does not exist, abort;
    else, make sure that target folder exists, then return it.
    """

    base_folder = os.path.join(conf('local', 'dump_folder'))
    if not os.path.exists(base_folder):
        raise Exception('Base folder "%s" does not exists' % base_folder)

    # Example:
    # target_folder = '/Users/morlandi/src2/brainstorm/brainstorm/brainweb/dumps/brainstorm.it'
    if args.localhost:
        target_folder = os.path.join(base_folder, 'localhost')
    else:
        target_folder = os.path.join(base_folder, conf('ssh', 'host'))
    assure_path_exists(target_folder)

    return target_folder


def download_dbdump_command():
    """
    Prepare command to download remote db dump via ssh

    With Postgresql: fix table owner
    With Mysql: fix absolute ursl (for Wordpress)
    """

    use_postgresql = conf('general', 'db_type') == 'postgresql'
    use_mysql = conf('general', 'db_type') == 'mysql'

    if use_postgresql:

        # Example: command = "pg_dump --dbname=brainweb"
        command = "pg_dump --dbname=%s" % (
            conf('remote_db', 'name'),
        )

        # Fix db owner
        remote_db_user = conf('remote_db', 'user')
        local_db_user = conf('local_db', 'user')
        if remote_db_user != local_db_user:
            search = 'OWNER TO %s;$' % remote_db_user
            replace = 'OWNER TO %s;' % local_db_user
            command += " | sed -e 's/%s/%s/g'" % (search, replace)

    elif use_mysql:

        # Example: command = "mysqldump brainweb"
        command = "mysqldump %s" % (
            conf('remote_db', 'name'),
        )

        if conf('general', 'app_type') == 'wordpress':
            # Fix absolute urls
            search = conf('remote', 'url').replace('/', '\\/')
            replace = conf('local', 'url').replace('/', '\\/')
            if search != replace:
                command += " | sed -e 's/%s/%s/g'" % (search, replace)

    else:

        raise Exception('Unkwnown database type')

    # Apply search & replace specs:
    for search, replace in collect_search_replace_specs("remote_db"):
        command += " | sed -e 's/%s/%s/g'" % (search.replace('/', '\\/'), replace.replace('/', '\\/'))

    if is_true(conf('general', 'use_gzip')):
        command += " | gzip"

    command = build_ssh_command(command)

    # Example:
    # >  ssh brainstorm.it "sudo -u postgres pg_dump --dbname=brainweb | sed -e 's/OWNER TO brainweb;$/OWNER TO brainweb0;/' | gzip"
    return command


def dump_db(prefix):
    logger.info('dump_db() ...')

    target_folder = local_dumps_target_folder()

    # Example: dump_filepath = "./dumps/brainstorm.it/2017-11-06_00.21.25_brainweb.sql"
    use_postgresql = conf('general', 'db_type') == 'postgresql'
    dump_filename = prefix + conf('local_db', 'name') + (".sql" if use_postgresql else ".mysql")
    dump_filepath = os.path.join(target_folder, dump_filename)
    if is_true(conf('general', 'use_gzip')):
        dump_filepath += ".gz"
    logger.info('dump_filepath: "%s"' % dump_filepath)

    # Prepare command to download remote db dump via ssh
    command = download_dbdump_command()

    # Example:
    # >  ssh brainstorm.it "..." > ./dumps/brainstorm.it/2017-11-06_00.46.16_brainweb.sql.gz
    command += ' > "%s"' % dump_filepath

    run_command(command)


def dump_local_db(prefix):
    logger.info('dump_local_db() ...')

    use_postgresql = conf('general', 'db_type') == 'postgresql'
    use_mysql = conf('general', 'db_type') == 'mysql'
    target_folder = local_dumps_target_folder()

    # Example: dump_filepath = "./dumps/localhost/2017-11-06_00.21.25_brainweb.sql"
    use_postgresql = conf('general', 'db_type') == 'postgresql'
    dump_filename = prefix + conf('local_db', 'name') + (".sql" if use_postgresql else ".mysql")
    dump_filepath = os.path.join(target_folder, dump_filename)
    if is_true(conf('general', 'use_gzip')):
        dump_filepath += ".gz"
    logger.info('dump_filepath: "%s"' % dump_filepath)

    # Prepare command to dump local db
    command = ''
    if use_postgresql:
        command = "pg_dump --dbname=%s" % (
            conf('local_db', 'name'),
        )
    elif use_mysql:
        command = "mysqldump %s" % (
            conf('local_db', 'name'),
        )

    if is_true(conf('general', 'use_gzip')):
        command += " | gzip"

    # Example:
    # >  ssh brainstorm.it "..." > ./dumps/brainstorm.it/2017-11-06_00.46.16_brainweb.sql.gz
    command += ' > "%s"' % dump_filepath

    run_command(command)


def sync_db():
    logger.info('sync_db() ...')

    use_postgresql = conf('general', 'db_type') == 'postgresql'
    use_mysql = conf('general', 'db_type') == 'mysql'

    # Prepare command to download remote db dump via ssh
    dbdump_command = download_dbdump_command()

    if use_postgresql:

        # Drop local db
        command = 'psql --dbname="template1" --command="drop database if exists %s"' % (
            conf('local_db', 'name')
        )
        run_command(command)

        # Create empty local db
        command = 'psql --dbname="template1" --command="create database %s owner %s"' % (
            conf('local_db', 'name'),
            conf('local_db', 'user'),
        )
        run_command(command)

        # Dump remote db and feed local one
        command = dbdump_command
        if conf('general', 'use_gzip'):
            command += " | gunzip"
        command += " | psql %s" % conf('local_db', 'name')
        run_command(command)

        # Post-dump local db adjustments
        # SQL="update django_site set domain='`hostname`.`hostname -d`' where id=1"
        # echo $SQL
        # psql -d $LOCAL_DBNAME -c "$SQL"
        # psql $LOCAL_DBNAME --command="select * from django_site"

    elif use_mysql:

        # Drop local db
        command = 'mysql --execute="drop database if exists %s"' % (
            conf('local_db', 'name')
        )
        run_command(command)

        # Create empty local db
        command = 'mysql --execute="create database {name}; GRANT ALL ON {name}.* TO \'{user}\'@\'localhost\';"'.format(
            name=conf('local_db', 'name'),
            user=conf('local_db', 'user'),
        )
        run_command(command)

        # Dump remote db and feed local one
        command = dbdump_command
        if conf('general', 'use_gzip'):
            command += " | gunzip"
        command += " | mysql %s" % conf('local_db', 'name')
        run_command(command)

    else:
        raise Exception('Unkwnown database type')


def rsync_data(rsync_source, rsync_target):

    user = conf('ssh', 'user')
    host = conf('ssh', 'host')
    options = conf('ssh', 'options')
    exclude = conf('remote_data', 'exclude')

    # start with "ssh user@host"
    ssh_command = "ssh"
    if options:
        ssh_command += " " + options

    # Example:
    # rsync -avz -e "ssh" --delete --progress --partial --exclude="CACHE/" ...
    #    "brainstorm.it:/home/brainweb/public/media/" ...
    #    "/Users/morlandi/src2/brainstorm/brainstorm/brainweb/dumps/brainstorm.it/media/"
    command = 'rsync -avz -e "%s"' % ssh_command

    # Remote copy of files that need owner access
    # See:
    # https://askubuntu.com/questions/208378/how-do-i-copy-files-that-need-root-access-with-scp#849657
    owner = conf('remote_data', 'owner')
    if owner:
        command += ' --rsync-path="sudo -u %s rsync"' % owner

    # more rsync options
    command += ' --delete --progress --partial'
    if exclude:
        command += ' --exclude="%s"' % exclude

    # build source url
    rsync_source_url = ""
    if user:
        rsync_source_url += user + '@'
    rsync_source_url += host + ':'
    rsync_source_url += rsync_source

    command += ' "%s/" "%s/"' % (rsync_source_url, rsync_target)
    run_command(command)


def dump_data(prefix):
    logger.info('dump_data() ...')

    app_type = conf('general', 'app_type')
    target_folder = local_dumps_target_folder()

    data = 'media' if (app_type == 'django') else 'wordpress'

    # Example: rsync_source = "/home/brainweb/public/media"
    rsync_source = conf('remote_data', 'data_folder')
    logger.info('rsync_source: "%s"' % rsync_source)

    # Example: rsync_target = "./dumps/brainstorm.it/media"
    rsync_target = os.path.join(target_folder, data)
    logger.info('rsync_target: "%s"' % rsync_target)

    # Sync data from remote host onto rsync_target
    rsync_data(rsync_source, rsync_target)

    # Example: dump_filepath = "./dumps/brainstorm.it/2017-11-06_00.21.25_brainweb.media.tar"
    dump_filename = "%s%s.%s.tar" % (prefix, conf('local_db', 'name'), data)
    dump_filepath = os.path.join(target_folder, dump_filename)
    logger.info('dump_filepath: "%s"' % dump_filepath)

    # Example:
    # tar -C "/Users/morlandi/src2/brainstorm/brainstorm/brainweb/dumps/brainstorm.it"
    #     -zcvf "/Users/morlandi/src2/brainstorm/brainstorm/brainweb/dumps/brainstorm.it/2017-11-06_23.01.41_brainweb.media.tar.gz"
    #     "media"
    options = "cvf"
    if is_true(conf('general', 'use_gzip')):
        options = "z" + options
        dump_filepath += ".gz"
    command = 'tar -C "%s" -%s "%s" "%s"' % (target_folder, options, dump_filepath, data)
    run_command(command)


def dump_local_data(prefix):
    logger.info('dump_local_data() ...')

    app_type = conf('general', 'app_type')
    target_folder = local_dumps_target_folder()

    data = 'media' if (app_type == 'django') else 'wordpress'

    # Example: dump_filepath = "./dumps/brainstorm.it/2017-11-06_00.21.25_brainweb.media.tar"
    dump_filename = "%s%s.%s.tar" % (prefix, conf('local_db', 'name'), data)
    dump_filepath = os.path.join(target_folder, dump_filename)
    logger.info('dump_filepath: "%s"' % dump_filepath)

    # Example:
    # tar -C "/Users/morlandi/src2/brainstorm/brainstorm/brainweb/public"
    #     -zcvf "/Users/morlandi/src2/brainstorm/brainstorm/brainweb/dumps/localhost/2017-11-06_23.01.41_brainweb.media.tar.gz"
    #     "media"
    options = "cvf"
    if is_true(conf('general', 'use_gzip')):
        options = "z" + options
        dump_filepath += ".gz"

    # use "media" parent as source folder
    source_folder = os.path.abspath(os.path.join(conf('local_data', 'data_folder'), '..'))

    command = 'tar -C "%s" -%s "%s" "%s"' % (source_folder, options, dump_filepath, data)
    run_command(command)


def sync_data():
    logger.info('sync_data() ...')

    # Example: rsync_source = "/home/brainweb/public/media"
    rsync_source = conf('remote_data', 'data_folder')
    logger.info('rsync_source: "%s"' % rsync_source)

    # Example: rsync_target = "./public/media"
    rsync_target = conf('local_data', 'data_folder')
    logger.info('rsync_target: "%s"' % rsync_target)

    # Sync data from remote host onto rsync_target
    rsync_data(rsync_source, rsync_target)


class MyParser(argparse.ArgumentParser):

    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def main():

    global config
    global args

    #
    # Parse command line
    #

    default_config_filename = './%s%sconf' % (os.path.splitext(os.path.basename(__file__))[0], os.path.extsep)

    # See: https://docs.python.org/2/library/argparse.html
    parser = MyParser(
        description='Dump remote db and/or data, or Sync local db and/or data from remote instance',
        formatter_class=argparse.RawTextHelpFormatter,
#         epilog="""Examples:
# """,
    )
    parser.add_argument('action', metavar='action', choices=('sync', 'dump'), help="choices: sync, dump")
    parser.add_argument('target', metavar='target', choices=('db', 'data', 'all'), help="choices: db, data, all")
    parser.add_argument('-c', '--config', metavar='config_filename', default=default_config_filename,
        help="config. filename (default = \"%s\")" % default_config_filename)
    parser.add_argument('-v', '--verbosity', type=int, choices=[0, 1, 2, 3], default=2, help="Verbosity level. (default: 2)")
    parser.add_argument('--dry-run', '-d', action='store_true', help="simulate actions")
    parser.add_argument('--quiet', '-q', action='store_true', help="do not require user confirmation before executing commands")
    parser.add_argument('--localhost', '-l', action='store_true', help="dump db and data from localhost into ./dumps/localhost")
    parser.add_argument('--version', action='version', version='%(prog)s ' + get_version())
    args = parser.parse_args()


    # Add complementary info to args
    vars(args)['interactive'] = not args.quiet
    logger.info('ARGS: ' + str(args))

    # Setup logger
    setup_logger(args.verbosity)

    try:
        # Read config. file
        #config_filename = os.path.splitext(sys.argv[0])[0] + os.path.extsep + "conf"
        # Example: "./manage_sync.conf"
        #config_filename = './%s%sconf' % (os.path.splitext(os.path.basename(__file__))[0], os.path.extsep)
        config_filename = args.config.strip()
        config = ConfigParser()
        success = len(config.read(config_filename)) > 0
        if success:
            logger.info('Using config file "%s"' % config_filename)
        else:
            # if not found, create a default config file and exit
            if not args.quiet and query_yes_no('Create default config file "%s" ?' % config_filename):
                create_default_config_file(config_filename)
                logger.warning('Default config file "%s" has been created; please revise' % config_filename)
                exit(-1)
            success = len(config.read(config_filename)) > 0
        # if still failing, give up
        if not success:
            raise Exception('Config. file "%s" not found' % (config_filename))

        # Process requested action
        prefix = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S_")
        if args.action == 'sync':
            if args.localhost:
                raise Exception('"sync" action not available with --locahost option; use "dump"')
            if args.target in ['db', 'all']:
                sync_db()
            if args.target in ['data', 'all']:
                sync_data()
        elif args.action == 'dump':
            if args.localhost:
                if args.target in ['db', 'all']:
                    dump_local_db(prefix)
                if args.target in ['data', 'all']:
                    dump_local_data(prefix)
            else:
                if args.target in ['db', 'all']:
                    dump_db(prefix)
                if args.target in ['data', 'all']:
                    dump_data(prefix)

    except Exception as e:
        logger.error(str(e))
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
