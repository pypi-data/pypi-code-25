from pathlib import Path
import click
import pickle
import exceptions as e
from config import CONFIG
from functions import Payouts
from dpostools.constants import ARK
from pprint import pprint
from encryption import Crypt
import constants as c
from raven.handlers.logging import SentryHandler
import logging
import db as i
from pid import PidFile
import os
import subprocess


def load_config(ctx, network):
    """
    Some boilerplate code for obtaining configuration dict from ctx.
    :return: config dict
    """
    config = ctx.obj['config']
    setting = config[network]
    if network not in CONFIG:
        if click.confirm("Unfamiliar with that network. Do you wish to set it now?", abort=True):
            set_config(ctx)

    printer = ctx.obj['printer']
    return setting, printer


class Verbose:
    def __init__(self, level, dsn=None):
        self.level = level
        self.logger = logging.getLogger(__name__)
        if dsn:
            self.handler = SentryHandler(dsn)
            self.handler.setLevel(level)

    def debug(self, text, color=None):
        if self.level <= 10:
            self.logger.debug(text)
            click.echo(message=text, color=color)

    def info(self, text, color=None):
        if self.level <= 20:
            self.logger.info(text)
            click.echo(message=text, color=color)

    def log(self, text, color=None):
        self.logger.log(2.5, text)
        if self.level <= 30:
            click.echo(message=text, color=color)

    def warn(self, text, color=None):
        self.logger.error(text)
        if self.level <= 40:
            click.echo(message=text, color=color)


@click.group()
@click.option(
    '--config-file', '-c',
    type=click.Path(),
    default='/tmp/.dpos-CLI.cfg',
    help="persistent configuration file path.")
@click.option(
    '--password', '-p',
    type=click.STRING,
    default="default_password",
    help="Set a password to ensure your keys are not stored unencrypted.")
@click.option(
    '--verbose', '-v',
    type=click.Choice(["0", "10", "20", "30", "40", "50"]),
    default="20",
    help="Verbosity level")
@click.pass_context
def main(ctx, config_file, password, verbose):
    """
    Command line tool for delegates

    Currently supports:
        Ark
        DArk
        Kapu
        Test-Persona
    """
    printer = Verbose(level=int(verbose))

    filename = os.path.expanduser(config_file)
    config = CONFIG

    if os.path.exists(filename):
        with open(filename, 'rb') as config_file:
            config = pickle.load(config_file)

        for network in config:
            if network == "virgin":
                continue
            try:
                if config[network]["delegate_passphrase"][1]:
                    printer.info("Decrypting primary passhrase")
                    config[network]["delegate_passphrase"][0] = Crypt().decrypt(crypt=config[network]["delegate_passphrase"][0],
                                                                             password=password)
                    config[network]["delegate_passphrase"][1] = False
                    printer.info("Decrypted!")
                if config[network]["delegate_second_passphrase"][1]:
                    printer.info("Decrypting secondary passphrase")
                    config[network]["delegate_second_passphrase"][0] = Crypt().decrypt(
                        crypt=config[network]["delegate_second_passphrase"][0], password=password)
                    config[network]["delegate_second_passphrase"][1] = False
                    printer.info("decrypted!")
            except KeyError:
                pass

    ctx.obj = {
        'config': config,
        'printer': printer,

    }

@main.command()
@click.pass_context
def enable_autocomplete(ctx):
    printer = ctx.obj['printer']

    current_dir = os.path.dirname(os.path.realpath(__file__))
    home = str(Path.home())
    Path('{}/.bashrc'.format(home)).touch()

    # check if we already appended the script command.
    with open("{}/.bashrc".format(home), "r") as bashrc:
        lines = bashrc.readlines()
        for line in lines:
            if "{c_dir}/deputy-complete.sh".format(c_dir=current_dir) in line:
                printer.warn("Already edited .bashrc!")
                return

    with open("{}/.bashrc".format(home), "a") as bashrc:
        printer.info("Editing .bashrc")
        bashrc.write(". {c_dir}/deputy-complete.sh".format(c_dir=current_dir))
        printer.info("Success!")

    printer.info("Running some commands.")
    subprocess.run("_DEPUTY_COMPLETE=source {c_dir}/deputy > {c_dir}/deputy-complete.sh".format(c_dir=current_dir), shell=True)
    subprocess.run("chmod u+x {c_dir}/deputy-complete.sh".format(c_dir=current_dir), shell=True)
    subprocess.run("bash {c_dir}/deputy-complete.sh".format(c_dir=current_dir), shell=True)
    printer.info("Done!")



@main.command()
@click.option(
    '--network', '-n',
    type=click.Choice(list(CONFIG.keys())[1:]),
    default=None,
    help="Network you wish to set.")
@click.option(
    '--setting', '-s',
    type=click.STRING,
    nargs=2,
    help="Setting name + value you wish to specifically set.")
@click.option(
    '--password', '-p',
    type=click.STRING,
    default="default_password",
    help="Set a password to ensure your keys are not stored unencrypted")
@click.pass_context
def set_config(ctx, network, password, setting):
    """
    Store configuration values in a file, e.g. the API key for OpenWeatherMap.
    """
    config = ctx.obj['config']
    printer = ctx.obj['printer']

    if not config["virgin"]:
        if not click.confirm("Override or add to previously set settings?", abort=True):
            return

    if not network:
        network = click.prompt("Please enter the network you wish to set")
        if network not in CONFIG:
            network = click.prompt("Invalid network, select from {}".format(list(CONFIG.keys())[1:]))
            if network not in CONFIG:
                raise e.InvalidNetwork("invalid network entered, exiting.")

        config["virgin"] = False

        config[network]["db_name"] = click.prompt("Please enter the name of the postgres database hosting the network")
        config[network]["db_host"] = click.prompt("Please enter the host of the database (probably localhost)")
        config[network]["db_user"] = click.prompt("Please enter the name of the postgres user")
        config[network]["db_password"] = click.prompt("Please enter the password of the postgres user")

        config[network]["delegate_address"] = click.prompt("Please enter your delegate address")
        config[network]["delegate_pubkey"] = click.prompt("Please enter your delegate pubkey")
        # passphrases are a list: passphrase, encryption status (True means encrypted)
        if click.confirm("Do want to store your passphrase?"):
            config[network]["delegate_passphrase"] = [click.prompt("Please enter your delegate passphrase"), False]
        else:
            config[network]["delegate_passphrase"] = None, None

        if click.confirm("Do want to store your second passphrase?"):
            config[network]["delegate_second_passphrase"] = [click.prompt("Please enter your delegate second passphrase"), False]
        else:
            config[network]["delegate_second_passphrase"] = None, None

        config[network]["share"] = click.prompt("Please enter your share percentage as a ratio (100% = 1, 50% = 0.5)", type=float)
        if config[network]["share"] > 1:
            config[network]["share"] = click.prompt("MAKE SURE YOUR SHARE IS LESS THAN 1. Please enter your share percentage as a ratio (100% = 1, 50% = 0.5)", type=float)

            config[network]["max_voter_balance"] = ARK * click.prompt("Please enter the max balance that a voter may have in Ark (not arktoshi), "
                                                           "use 'inf' if you do not want to set a maximum (remaining staking reward gets distributed over other voters", type=float)
        if click.confirm("Do you wish to cover transaction fees for your voters?"):
            config[network]["cover_fees"] = True
        else:
            config[network]["cover_fees"] = False

        config[network]["message"] = click.prompt("Enter a message to send to your voters on payouts (if you don't want to send a message, leave it empty)")

        if click.confirm("Do you wish to blacklist voters?"):
            want_blacklist = True
            blacklist = []
            while want_blacklist:
                blacklist.append(click.prompt("enter an address to add to the blacklist"))
                if click.confirm("Do you wish to blacklist more voters?"):
                    want_blacklist = True
                else:
                    want_blacklist = False
        if click.confirm("Do you wish to enable raven logging?"):
            config[network]["raven_dsn"] = click.prompt("Enter your raven DSN")
        else:
            config[network]["raven_dsn"] = None

        if click.confirm("Do you want to setup a database for logging purposes?"):
            config[network]["db_name_{}_admin.".format(network)] = click.prompt("Please enter the name of the (non-existant) postgres database hosting the administration")
            config[network]["db_host_{}_admin".format(network)] = click.prompt("Please enter the host of the database (probably localhost)")
            config[network]["db_user_{}_admin".format(network)] = click.prompt("Please enter the name of the postgres user")
            config[network]["db_password_{}_admin".format(network)] = click.prompt("Please enter the password of the postgres user")


    # Incase we are setting a value specifically through the CLI as a shortcut
    else:
        printer.info("Setting {nw}:{key} to {val}".format(nw=network, key=setting[0], val=setting[1]))
        config[network][setting[0]] = setting[1]

    # Encrypting the passphrases.
    if not config[network]["delegate_passphrase"][1] and config[network]["delegate_passphrase"][0]:
        printer.info("encrypting primary passhrase")
        config[network]["delegate_passphrase"][0] = Crypt().encrypt(string=config[network]["delegate_passphrase"][0], password=password)
        config[network]["delegate_passphrase"][1] = True
        printer.info("encrypted!")
    if not config[network]["delegate_second_passphrase"][1] and config[network]["delegate_second_passphrase"][0]:
        printer.info("encrypting secondary passphrase")
        config[network]["delegate_second_passphrase"][0] = Crypt().encrypt(string=config[network]["delegate_second_passphrase"][0], password=password)
        config[network]["delegate_second_passphrase"][1] = True
        printer.info("encrypted!")

    printer.info("Saving your settings...")
    pickle.dump(config, open("/tmp/.dpos-CLI.cfg", "wb"))
    printer.info("Saved!")
    return config


@main.command()
@click.option(
    '--show_secret', '-sh',
    type=click.BOOL,
    default=False,
    help="Show the passphrase.")
@click.option(
    '--password', '-p',
    type=click.STRING,
    default="default_password",
    help="Set a password to ensure your keys are not stored unencrypted")
@click.pass_context
def inspect_config(ctx, sh, password):
    """
    Check my previously set configurations.
    """
    config = ctx.obj['config']
    printer = ctx.obj['printer']
    for network in config:
        if type(config[network]) == dict:
            printer.info(network.upper())
            for i in config[network]:
                if "passphrase" in i and not sh:
                    print("----", i, "---", "CENSORED PASSPHRASE")
                else:
                    print("----", i, "---", config[network][i])
        else:
            print(network.upper(), ":", config[network])


@main.command()
@click.option(
    '--cover_fees', '-cf',
    type=click.BOOL,
    default=False,
    help="Cover the fees of each payout transaction.")
@click.option(
    '--max_weight', '-mw',
    type=click.FLOAT,
    default=float("inf"),
    help="Maximum allowed voter balance.",)
@click.option(
    '--share', '-s',
    type=click.FLOAT,
    default=None,
    help="Percentage the voters receive (95 means the delegate keep 5%)")
@click.option(
    '--network', '-n',
    type=click.Choice(list(CONFIG.keys())[1:]),
    default='dark',
    help="Network you wish to connect to.")
@click.option(
    '--store', '-st',
    type=click.BOOL,
    default=False,
    help="Store the current pending balances of the voters in the DB.")
@click.option(
    '--print', '-p',
    type=click.BOOL,
    default=True,
    help="Print the current pending balances of the voters in the DB.")
@click.pass_context
def calculate_payouts(ctx, network, cover_fees, max_weight, share, store, print):
    """
    Calculate the pending payouts at this moment.
    """
    setting, printer = load_config(ctx, network)
    if store:
        try:
            db = i.DB(
                dbname=setting["db_name_{}_admin.".format(network)],
                host=setting["db_host_{}_admin".format(network)],
                user_name=setting["db_user_{}_admin".format(network)],
                password=setting["db_password_{}_admin".format(network)],
            )
        except KeyError:
            if click.confirm("Administration DB not set. Want to set it now?"):
                password = click.prompt("please enter your password")

                config = ctx.obj['config']
                config[network]["db_name_{}_admin.".format(network)] = click.prompt(
                    "Please enter the name of the (non-existant) postgres database hosting the administration")
                config[network]["db_host_{}_admin".format(network)] = click.prompt(
                    "Please enter the host of the database (probably localhost)")
                config[network]["db_user_{}_admin".format(network)] = click.prompt(
                    "Please enter the name of the postgres user")
                config[network]["db_password_{}_admin".format(network)] = click.prompt(
                    "Please enter the password of the postgres user")
                try:
                    # Encrypting the passphrases.
                    if not config[network]["delegate_passphrase"][1] and config[network]["delegate_passphrase"][0]:
                        printer.info("encrypting primary passhrase")
                        config[network]["delegate_passphrase"][0] = Crypt().encrypt(
                            string=config[network]["delegate_passphrase"][0], password=password)
                        config[network]["delegate_passphrase"][1] = True
                        printer.info("encrypted!")
                    if not config[network]["delegate_second_passphrase"][1] and \
                            config[network]["delegate_second_passphrase"][
                                0]:
                        printer.info("encrypting secondary passphrase")
                        config[network]["delegate_second_passphrase"][0] = Crypt().encrypt(
                            string=config[network]["delegate_second_passphrase"][0], password=password)
                        config[network]["delegate_second_passphrase"][1] = True
                        printer.info("encrypted!")
                except KeyError:
                    pass
            else:
                store = False

    if not share:
        share = float(setting["share"])

    calculator = Payouts(
        db_name=setting["db_name"],
        db_host=setting["db_host"],
        db_pw=setting["db_password"],
        db_user=setting["db_user"],
        network=network,
        delegate_address=setting["delegate_address"],
        pubkey=setting["delegate_pubkey"],
        arky_network_name=setting["arky"],
        printer=printer,
    )
    max_weight *= setting["coin_in_sat"]

    printer.info("Starting calculation...")
    payouts = calculator.calculate_payouts(
        cover_fees=cover_fees,
        max_weight=max_weight,
        share=share
    )

    if store:
        for y in payouts:
            db.store_payout(
                address=y,
                share=payouts[y]["share"],
                network=network,
                timestamp=payouts[y]["last_payout"]
            )

    for x in payouts:
        payouts[x]["share"] /= c.ARK
        payouts[x]["balance"] /= c.ARK

    if print:
        pprint(payouts)
        printer.info("Using the following configuration: \ncover_fees: {cf}\n max weight: {mw}\n share: {s}%\n".
               format(
                    cf=cover_fees,
                    mw="No max" if max_weight == float("inf") else max_weight,
                    s=share*100)
               )

@main.command()
@click.option(
    '--cover_fees', '-cf',
    type=click.BOOL,
    default=True)
@click.option(
    '--max_weight', '-mw',
    type=click.FLOAT,
    default=float("inf"))
@click.option(
    '--share', '-s',
    type=click.FLOAT,
    default=0)
@click.option(
    '--network', '-n',
    type=click.Choice(list(CONFIG.keys())[1:]),
    default='ark_mainnet',
    help="Network to connect to.")
@click.option(
    '--password', '-p',
    type=click.STRING,
    default="default_password",
    help="Set a password to ensure your keys are not stored unencrypted")
@click.pass_context
def payout_voters(ctx, network, cover_fees, max_weight, share):
    """
    Calculate and transmit payments to the voters.
    """
    with PidFile():
        setting, printer = load_config(ctx, network)

        printer.log("starting payment run")
        payer = Payouts(db_name=setting["db_name"], db_host=setting["db_host"], db_pw=setting["db_pw"],
                        db_user=setting["db_user"], network=network, delegate_address=setting["delegate_address"],
                        pubkey=setting["delegate_pubkey"], rewardswallet=setting["rewardswallet"], passphrase=setting["delegate_passphrase"],
                        second_passphrase=setting["delegate_second_passphrase"] if setting["delegate_second_passphrase"] else None,
                        printer=printer, arky_network_name=setting["arky"])
        max_weight *= setting["coin_in_sat"]

        printer.info("Calculating payments")
        payouts = payer.calculate_payouts(
                cover_fees=cover_fees,
                max_weight=max_weight,
                share=setting["share"])

        printer.info("transmitting payments")
        payer.transmit_payments(
                payouts,
                message=setting["message"])
        printer.log("Payment run done!")


@main.command()
@click.option(
    '--covered_fees', '-cf',
    type=click.BOOL,
    default=True,
    help="Were payout fees covered during the previous payment runs? (in between delegate reward payouts)",)
@click.option(
    '--shared_percentage', '-s',
    type=click.FLOAT,
    default=0,
    help="Shared percentage used during the previous runs (in between delegate reward payouts)")
@click.option(
    '--network', '-n',
    type=click.Choice(list(CONFIG.keys())[1:]),
    default='ark_mainnet',
    help="Network to connect to.")
@click.pass_context
def check_delegate_reward(ctx, network, covered_fees, shared_percentage):
    """
    Calculate the pending delegate reward.
    """
    setting, printer = load_config(ctx, network)

    calculator = Payouts(db_name=setting["db_name"], db_host=setting["db_host"], db_pw=setting["db_pw"],
                         db_user=setting["db_user"], network=network, delegate_address=setting["delegate_address"],
                         pubkey=setting["delegate_pubkey"], arky_network_name=setting["arky"],
                         printer=printer)

    delegate_share = calculator.calculate_delegate_share(
        covered_fees=covered_fees,
        shared_percentage=shared_percentage
    )
    printer.info("The built up share for the delegate is: {}".format(delegate_share/ARK))


@main.command()
@click.option(
    '--network', '-n',
    type=click.Choice(list(CONFIG.keys())[1:]),
    default='ark_mainnet',
    help="Network to connect to.")
@click.option(
    '--covered_fees', '-cf',
    type=click.BOOL,
    default=True,
    help="Were payout fees covered during the previous payment runs? (in between delegate reward payouts)",)
@click.option(
    '--shared_percentage', '-s',
    type=click.FLOAT,
    default=0,
    help="Shared percentage used during the previous runs (in between delegate reward payouts)")
@click.option(
    '--password', '-p',
    type=click.STRING,
    default="default_password",
    help="Set a password to ensure your keys are not stored unencrypted")
@click.option(
    '--tip', '-t',
    type=click.BOOL,
    default=True,
    help="Send a tip to Charles for developing this CLI and maintaining it.")
@click.pass_context
def pay_rewardswallet(ctx, network, covered_fees, shared_percentage, tip):
    """
    Calculate and pay the current pending delegate reward share and transmit to the rewardwallet
    """
    with PidFile():
        setting, printer = load_config(ctx, network)

        printer.log("Calculating delegate reward")
        payer = Payouts(db_name=setting["db_name"], db_host=setting["db_host"], db_pw=setting["db_pw"],
                        db_user=setting["db_user"], network=network, delegate_address=setting["delegate_address"],
                        pubkey=setting["delegate_pubkey"], arky_network_name=setting["arky"],
                        printer=printer)

        printer.log("Sending payment to delegate rewardswallet")
        payer.pay_rewardswallet(covered_fees=covered_fees, shared_percentage=shared_percentage)
        printer.log("Payment successfull.")

        if tip and not setting["testnet"]:
            payer.tip()


@main.command()
@click.option(
    '--network', '-n',
    type=click.Choice(list(CONFIG.keys())[1:]),
    default='ark_mainnet',
    help="Network to connect to.")
@click.pass_context
def setup_postgres_db(ctx, network):
    """
    Setup a database for administrative purposes.
    """
    setting, printer = load_config(ctx, network)
    try:
        db = i.DB(
            dbname=setting["db_name_{}_admin.".format(network)],
            host=setting["db_host_{}_admin".format(network)],
            user_name=setting["db_user_{}_admin".format(network)],
            password=setting["db_password_{}_admin".format(network)],
        )
    except KeyError:
        if click.confirm("Administration DB not set. Want to set it now?"):
            password = click.prompt("please enter your password")

            config = ctx.obj['config']
            config[network]["db_name_{}_admin.".format(network)] = click.prompt(
                "Please enter the name of the (non-existant) postgres database hosting the administration")
            config[network]["db_host_{}_admin".format(network)] = click.prompt(
                "Please enter the host of the database (probably localhost)")
            config[network]["db_user_{}_admin".format(network)] = click.prompt(
                "Please enter the name of the postgres user")
            config[network]["db_password_{}_admin".format(network)] = click.prompt(
                "Please enter the password of the postgres user")
            try:
                # Encrypting the passphrases.
                if not config[network]["delegate_passphrase"][1] and config[network]["delegate_passphrase"][0]:
                    printer.info("encrypting primary passhrase")
                    config[network]["delegate_passphrase"][0] = Crypt().encrypt(
                        string=config[network]["delegate_passphrase"][0], password=password)
                    config[network]["delegate_passphrase"][1] = True
                    printer.info("encrypted!")
                if not config[network]["delegate_second_passphrase"][1] and config[network]["delegate_second_passphrase"][
                    0]:
                    printer.info("encrypting secondary passphrase")
                    config[network]["delegate_second_passphrase"][0] = Crypt().encrypt(
                        string=config[network]["delegate_second_passphrase"][0], password=password)
                    config[network]["delegate_second_passphrase"][1] = True
                    printer.info("encrypted!")
            except KeyError:
                pass

            printer.info("Saving your settings...")
            pickle.dump(config, open("/tmp/.dpos-CLI.cfg", "wb"))
            printer.info("Saved!")

            db = i.DB(
                dbname=setting["db_name_{}_admin.".format(network)],
                host=setting["db_host_{}_admin".format(network)],
                user_name=setting["db_user_{}_admin".format(network)],
                password=setting["db_password_{}_admin".format(network)],
            )
    printer.info("creating database {}".format(setting["db_name_{}_admin.".format(network)]))
    db.create_db()
    printer.info("setting up tables")
    db.create_table_users_payouts()


if __name__ == "__main__":
    main()