import dpostools.legacy as legacy
from constants import ARK
import arky.rest
import exceptions as e
import time
from config import CONFIG


class Payouts:

    def __init__(self, network, delegate_address, pubkey, db_host, db_user, db_name,
                 db_pw, arky_network_name, printer, passphrase=None, second_passphrase=None,
                 rewardswallet=None):

        self.network = network
        self.delegate_address = delegate_address
        self.delegate_pubkey = pubkey
        self.delegate_passphrase = passphrase
        self.delegate_second_passphrase = second_passphrase
        self.db_host = db_host
        self.db_name = db_name
        self.db_user = db_user
        self.db_pw = db_pw
        self.rewardswallet = rewardswallet
        self.printer = printer

    def calculate_raw_payouts(self, max_weight, blacklist):
        legacy.set_connection(
            host=self.db_host,
            database=self.db_name,
            user=self.db_user,
            password=self.db_pw
        )

        legacy.set_delegate(
            address=self.delegate_address,
            pubkey=self.delegate_pubkey,
        )
        self.printer.debug("Starting trueshare calculation")
        return legacy.Delegate.trueshare(max_weight=max_weight, blacklist=blacklist)

    def format_raw_payouts(self, payouts_dict, cover_fees, share):
        if float(share) > 1:
            raise e.ShareTooHigh("A share higher than 1 will result in insufficient funds when paying the voters.")

        self.printer.debug("formatting raw payouts")
        for i in payouts_dict:
            if not cover_fees:
                payouts_dict[i]["share"] -= 0.1 * ARK
            payouts_dict[i]["share"] *= share
            self.printer.debug(payouts_dict[i])
        return payouts_dict

    def calculate_payouts(self, max_weight, cover_fees, share, blacklist=None):
        raw = self.calculate_raw_payouts(max_weight, blacklist)[0]
        return self.format_raw_payouts(raw, cover_fees=cover_fees, share=share)

    def transmit_payments(self, payouts, message):
        self.printer.debug("connecting to network: {}".format(self.network))
        arky.rest.use(self.network)
        for ark_address in payouts:
            res = arky.core.sendToken(payouts[ark_address]["share"], ark_address, self.delegate_passphrase,
                                secondSecret=self.delegate_second_passphrase if self.delegate_second_passphrase else None,
                                vendorField=message)
            if res["success"]:
                self.printer.debug(res)
            else:
                self.printer.warn(res)

    def pay_voters(self, cover_fees, max_weight, share, message=None):
        self.printer.debug("calculating voter payouts")
        payouts = self.calculate_payouts(
            cover_fees=cover_fees,
            max_weight=max_weight,
            share=share)
        self.printer.debug("starting payment transmission")
        self.transmit_payments(
            payouts,
            message=message)
        self.printer.debug("transmission successful")

    def calculate_delegate_share(self, covered_fees, shared_percentage):
        legacy.set_connection(
            host=self.db_host,
            database=self.db_name,
            user=self.db_user,
            password=self.db_pw)

        payouts = legacy.Address.transactions(self.delegate_address)
        blocks = legacy.Delegate.blocks(self.delegate_pubkey)

        last_reward_payout = legacy.DbCursor().execute_and_fetchone("""
                SELECT transactions."timestamp"
                FROM transactions
                WHERE transactions."recipientId" = '{rewardwallet}'
                AND transactions."senderId" = '{delegateaddress}'
                ORDER BY transactions."timestamp" DESC 
                LIMIT 1
            """.format(
            rewardwallet=self.rewardswallet,
            delegateaddress=self.delegate_address
        ))[0]

        delegate_share = 0

        if covered_fees:
            txfee = 0.1 * ARK
        else:
            txfee = 0

        for i in payouts:
            if i.recipientId == self.rewardswallet:
                del i
            else:
                if i.timestamp > last_reward_payout:
                    total_send_amount = (i.amount + txfee) / shared_percentage
                    delegate_share += total_send_amount - (
                                total_send_amount * shared_percentage + txfee)

        for b in blocks:
            if b.timestamp > last_reward_payout:
                delegate_share += b.totalFee

        return delegate_share

    def pay_rewardswallet(self, covered_fees, shared_percentage, message=None):
        share = self.calculate_delegate_share(
            covered_fees=covered_fees,
            shared_percentage=shared_percentage)

        arky.core.sendToken(
            share,
            self.rewardswallet,
            self.delegate_passphrase,
            # defaults to None if not initialized.
            secondSecret=self.delegate_second_passphrase,
            vendorField=message if message else "Delegate's reward share.")

    def tip(self):
        arky.core.sendToken(
            CONFIG[self.network]['tip'],
            CONFIG[self.network]['tipping_address'],
            self.delegate_passphrase,
            # defaults to None if not initialized.
            secondSecret=self.delegate_second_passphrase,
            )


