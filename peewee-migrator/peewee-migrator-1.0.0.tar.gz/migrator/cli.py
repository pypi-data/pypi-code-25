import click
import datetime
import sys
import tabulate
import os

from migrator.config import Config
from migrator.executor import Executor

from migrator.fixtures import FixtureLoader


def choices_prompt(message, choices, default='0'):
    return click.prompt(
        '{}\n{}'.format(
            '\n'.join(['{} - {}'.format(k, v) for k, v in sorted(choices.items(), key=lambda x: x[0])]),
            message
        ),
        default=default, type=click.Choice(sorted(choices.keys())), show_default=True
    )


def halt(messgae):
    click.echo(messgae)
    sys.exit(1)


def get_one_revision(migrator, rev):
    revisions = migrator.get_migrations_by_hash(rev)
    if not revisions:
        halt(f'Revision {rev} not found.')
    if len(revisions) > 1:
        halt(f'Revision {rev} has too much matches ({len(revisions)}).')
    return revisions[0]


@click.group()
@click.option('-c', '--config', type=click.Path(), default='migrator.cfg')
@click.pass_context
def cli(ctx, config):
    config = os.path.realpath(config)
    cfg = Config()
    ctx.obj = ctx.obj or {}
    if os.path.exists(config):
        cfg.load(config)
        ctx.obj['config_path'] = config
    else:
        cfg.make_default()
        ctx.obj['config_path'] = None
    ctx.obj.update({'cfg': cfg})


@cli.command()
@click.option('--type', 'db_type_arg', default=None)
@click.option('--name', 'db_name_arg', default=None)
@click.option('--user', 'db_user_arg', default=None)
@click.option('--password', 'db_password_arg', default=None)
@click.option('--host', 'db_host_arg', default=None)
@click.option('--port', 'db_port_arg', default=None)
@click.option('--dir', 'migrations_dir_arg', default=None)
@click.option('--sys_path', 'sys_path_arg', default=None)
@click.option('--models', 'models_path_arg', default=None)
@click.option('--excluded', 'models_excluded_arg', default=None)
@click.option('--storage', 'migrations_storage', default=None)
@click.option('--force', default=False, is_flag=True)
@click.pass_context
def create_config(
        ctx, db_type_arg, db_name_arg, db_user_arg, db_password_arg, db_host_arg, db_port_arg,
        migrations_dir_arg, sys_path_arg, models_path_arg, models_excluded_arg, migrations_storage, force
):
    config_path = ctx.obj['config_path'] or 'migrator.cfg'
    ask_edit = all(
        x is None for x in (
            db_type_arg, db_name_arg, db_user_arg, db_password_arg, db_host_arg, db_port_arg,
            migrations_dir_arg, sys_path_arg, models_path_arg, models_excluded_arg
        )
    )
    if os.path.exists(config_path):
        if not force and not click.confirm('Config already exists. Overwrite?', default=False):
            return
    db_types = {'0': 'postgres', '1': 'sqlite', '2': 'mysql'}

    if db_type_arg is None:
        result = choices_prompt('Database type', db_types)
        db_type = db_types[result]
    else:
        db_type = db_type_arg
    click.echo(db_type)
    db_name = (
        click.prompt('Database', default='peewee{}'.format('.db' if db_type == 'sqlite' else ''))
        if db_name_arg is None else db_name_arg
    )
    if db_type == 'sqlite':
        db_url = 'sqlite:///{}'.format(db_name)
    else:
        user = click.prompt('User', default='peewee') if db_user_arg is None else db_user_arg
        password = click.prompt('Password', hide_input=True) if db_password_arg is None else db_password_arg
        host = click.prompt('Host', default='127.0.0.1') if db_host_arg is None else db_host_arg
        port = (
            click.prompt('Port', default='5432' if db_type == 'postgres' else '3306')
            if db_port_arg is None else db_port_arg
        )
        db_url = '{}://{}:{}@{}:{}/{}'.format(db_type, user, password, host, port, db_name)

    default_path = os.path.abspath('.')
    migrations_dir = (
        click.prompt(
            'Migrations directory', default=os.path.join(default_path, 'migrations'), type=click.Path(
                exists=True, file_okay=False, writable=True, readable=True, resolve_path=True
            )
        ) if migrations_dir_arg is None else migrations_dir_arg
    )
    sys_path = (
        click.prompt(
            'PYTHON_PATH for project (Use : as delimiter)', default=default_path, type=click.Path(
                exists=True, file_okay=False, writable=False, readable=True
            )
        ) if sys_path_arg is None else sys_path_arg
    )

    models_path = (
        click.prompt('Models path (Comma separated)', default='app.models')
        if models_path_arg is None else models_path_arg
    )

    excluded_models = (
        click.prompt('Excluded models by name (Comma separated)', default='')
        if models_excluded_arg is None else models_excluded_arg
    )

    storage_types = {'fs': 'File system', 'db': 'Database'}

    if migrations_storage not in storage_types:
        migrations_storage = choices_prompt('Applied migrations storage type', storage_types, default='fs')

    # Add to new config
    cfg = Config()
    cfg.update({
        cfg.BASE_SECTION: {
            cfg.MIGRATOR_DB_URL: db_url,
            cfg.MIGRATOR_SYS_PATH: sys_path,
            cfg.MIGRATOR_MIGRATIONS_DIR: migrations_dir,
            cfg.MIGRATOR_MODELS_PATH: models_path,
            cfg.MIGRATOR_EXCLUDED_MODELS: excluded_models,
            cfg.MIGRATOR_MIGRATIONS_STORAGE: migrations_storage
        }
    })

    config = cfg.to_string_io().getvalue()

    if ask_edit and click.confirm('Edit config?', default=True):
        edited = click.edit(config)
        if edited is not None:  # None - if edit canceled
            config = edited
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config)
    click.echo('Config successfully saved!')


@cli.command('make')
@click.option('--type', 'migration_type', default='from_db',
              type=click.Choice(['from_db', 'from_last', 'from_rev', 'empty', 'data']))
@click.option('--rev', default=None)
@click.option('--name', default=None)
@click.option('--models', default=None)
@click.option('--require', default=False, is_flag=True)
@click.pass_context
def make_migration(ctx, migration_type, rev, name, models, require):
    migrator = Executor(ctx.obj['cfg'])
    if rev is None and migration_type == 'rev':
        halt('--rev param required')
    migration_name = (click.prompt('Migration title') or None) if name is None else name
    revision = None

    if migration_type == 'empty':
        revision = migrator.make_empty_migration(migration_name=migration_name)
    elif migration_type == 'from_db':
        revision = migrator.migrate_from_db(migration_name=migration_name)
    elif migration_type == 'from_last':
        last = sorted(migrator.get_migrations(), key=lambda x: -x['time'])
        if not last:
            halt('There are no latest migration.')
        revision = migrator.migrate_from_migration(migration=last[0], migration_name=migration_name)
    elif migration_type == 'from_rev':
        revisions = migrator.get_migrations_by_hash(rev)
        if not revisions:
            click.echo(f'Revision {rev} not found.')
        if len(revisions) > 1:
            halt(f'Revision {rev} has too much matches ({len(revisions)}).')
        revision = migrator.migrate_from_migration(migration=revisions[0], migration_name=migration_name)
    elif migration_type == 'data':
        loader = FixtureLoader(ctx.obj['cfg'])
        revision = loader.make_data_migration(migration_name=migration_name, only_models=models)
    else:
        print(f'Unknown migration type {migration_type}')
    if require and revision is not None:
        migrator.make_required(revision)
        click.echo(f'Revision {revision} marked as required')


@cli.command('apply')
@click.option('--force', default=False, is_flag=True)
@click.option('--fake', default=False, is_flag=True)
@click.argument('rev')
@click.pass_context
def apply_migration(ctx, force, fake, rev):
    migrator = Executor(ctx.obj['cfg'])
    revision = get_one_revision(migrator, rev)
    if migrator.check_status(revision['hash']) == migrator.STATUS_APPLIED:
        if not force and not click.confirm('Migration already applied. Repeat?', default=False):
            halt('Abort')
    if not migrator.check_dependencies(revision):
        not_applied = [x for x in revision['dependencies'] if migrator.check_status(x) != migrator.STATUS_APPLIED]
        halt('Migration dependencies not applied: {}'.format(','.join(not_applied)))
    migrator.apply(revision, fake=fake)
    click.echo(f'Migration {revision["hash"]} applied successfully!')


@cli.command('revert')
@click.option('--force', default=False, is_flag=True)
@click.option('--fake', default=False, is_flag=True)
@click.argument('rev')
@click.pass_context
def revert_migration(ctx, force, fake, rev):
    migrator = Executor(ctx.obj['cfg'])
    revision = get_one_revision(migrator, rev)
    if migrator.check_status(revision['hash']) != migrator.STATUS_APPLIED:
        if not force and not click.confirm('Migration not applied. Revert?', default=False):
            halt('Abort')
    migrator.revert(revision, fake=fake)
    click.echo(f'Migration {revision["hash"]} reverted successfully!')


@cli.command('list')
@click.option('--sort', default='time', type=click.Choice(['name', 'time', 'hash', 'status']))
@click.option('--reverse', default=False, is_flag=True)
@click.pass_context
def migrations_list(ctx, sort, reverse):
    migrator = Executor(ctx.obj['cfg'])
    headers = ['Time', 'Title', 'Migration', 'Dependencies', 'Applied', 'Required']
    rows = []
    for migration in migrator.get_migrations():
        rows.append([
            datetime.datetime.fromtimestamp(migration['time']),
            migration['name'],
            migration['hash'],
            ', '.join(migration['dependencies']) if migration['dependencies'] else 'No',
            'Yes' if migration['status'] == migrator.STATUS_APPLIED else 'No',
            '{}, {}'.format('Yes', migration['required'] + 1) if migration['required'] is not None else 'No'
        ])
    sort_column = {'time': 0, 'name': 1, 'hash': 2, 'status': 4}[sort]
    rows = sorted(rows, key=lambda x: x[sort_column])
    if reverse:
        rows = reversed(rows)
    click.echo(tabulate.tabulate(rows, headers, tablefmt='psql'))


@cli.command('require')
@click.option('--after', default=None)
@click.argument('rev')
@click.pass_context
def mark_required(ctx, after, rev):
    migrator = Executor(ctx.obj['cfg'])
    revision = get_one_revision(migrator, rev)['hash']
    if after is not None:
        after = get_one_revision(migrator, after)['hash']
    migrator.make_required(revision, after=after)
    click.echo(f'Revision {revision} marked as required')


@cli.command('up')
@click.option('--fake', default=False, is_flag=True)
@click.pass_context
def up_required(ctx, fake):
    migrator = Executor(ctx.obj['cfg'])
    required = migrator.get_required()
    if not required:
        halt('There are no required migrations (Empty required.json)')

    to_apply = [rev for rev in required if migrator.check_status(rev) != migrator.STATUS_APPLIED]
    if not to_apply:
        halt('Project already up to date')
    for rev in to_apply:
        revision = get_one_revision(migrator, rev)
        if not migrator.check_dependencies(revision):
            not_applied = [x for x in revision['dependencies'] if migrator.check_status(x) != migrator.STATUS_APPLIED]
            halt('Migration dependencies not applied: {}'.format(','.join(not_applied)))
        migrator.apply(revision, fake=fake)
        click.echo(f'Migration {revision["hash"]} applied successfully!')


if __name__ == '__main__':
    cli()
