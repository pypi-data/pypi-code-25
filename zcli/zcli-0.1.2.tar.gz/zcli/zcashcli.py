import subprocess
import logging
import time
from decimal import Decimal
from pathlib2 import Path
from zcli import saferjson


MINCONF = 6


class ZcashCLI (object):
    def __init__(self, datadir, network='mainnet'):
        assert isinstance(datadir, Path), repr(datadir)
        assert network in {'mainnet', 'testnet', 'regtest'}, repr(network)

        self._execname = 'zcash-cli'
        self._datadir = datadir
        self._network = network
        self._log = logging.getLogger('ZcashCLI')

    def __getattr__(self, method):
        return ZcashCLIMethod(
            method,
            self._execname,
            self._datadir,
            self._network,
            self._log,
        )


class ZcashCLIMethod (object):
    def __init__(self, method, execname, datadir, network, log):
        self._method = method
        self._execname = execname
        self._datadir = datadir
        self._network = network
        self._log = log

    def __call__(self, *args, **kwargs):
        result = self._call_raw_result(*args, **kwargs)
        if result.startswith('{') or result.startswith('['):
            result = saferjson.loads(result)
        return result

    def _call_raw_result(self, *args, **kwargs):
        prefixopts = kwargs.pop('prefixopts', [])
        assert not kwargs, ('unexpected key word args', kwargs)

        fullargs = [
            self._execname,
            '-datadir={}'.format(self._datadir),
        ]

        fullargs.extend({
            'mainnet': [],
            'testnet': ['-testnet'],
            'regtest': ['-regtest'],
        }[self._network])

        fullargs.extend(prefixopts)

        fullargs.append(self._method)
        fullargs.extend(map(saferjson.encode_param, args))

        self._log.debug('Running: %r', fullargs)
        return subprocess.check_output(fullargs).rstrip()


class ComposedZcashCLI (ZcashCLI):
    """Extends ZcashCli with useful call compositions as methods."""

    def iter_blocks(self, blockhash=None):
        if blockhash is None:
            blockhash = self.getblockhash(1)

        while blockhash is not None:
            block = self.getblock(blockhash)
            yield block
            blockhash = block.get('nextblockhash').encode('utf8')

    def iter_transactions(self, startblockhash=None):
        for block in self.iter_blocks(startblockhash):
            for txidu in block['tx']:
                txid = txidu.encode('utf8')
                yield (block, self.getrawtransaction(txid, 1))

    def get_taddr_balances(self):
        balances = {}
        for unspent in self.listunspent():
            addr = unspent['address']
            amount = unspent['amount']
            balances[addr] = amount + balances.get(addr, Decimal(0))
        return balances

    def wait_on_opids(self, opids, confirmations=MINCONF):
        assert isinstance(opids, list) or isinstance(opids, set), opids
        opids = set(opids)
        txids = []

        somefailed = False
        while len(opids) > 0:
            logging.debug('Waiting for completions:')
            completes = []
            for opinfo in self.z_getoperationstatus(list(opids)):
                opid = opinfo['id']
                status = opinfo['status']
                logging.debug('  %s - %s', opid, status)

                if status not in {'queued', 'executing'}:
                    opids.remove(opid)
                    completes.append(opid)

            if completes:
                for opinfo in self.z_getoperationresult(completes):
                    if opinfo['status'] == 'success':
                        opid = opinfo['id']
                        txid = opinfo['result']['txid'].encode('utf8')
                        txids.append((opid, txid))
                    else:
                        somefailed = True
                        logging.warn('FAILED OPERATION: %r', opinfo)

            logging.debug('')
            if len(opids) > 0:
                time.sleep(13)

        while txids:
            logging.debug('Waiting for confirmations:')
            newtxids = []
            for (opid, txid) in txids:
                txinfo = self.gettransaction(txid, True)
                confs = txinfo['confirmations']
                logging.debug(
                    '  %s - txid: %s - confirmations: %s',
                    opid,
                    txid,
                    confs,
                )
                if confs < 0:
                    logging.warn('FAILED TO CONFIRM: %r', txinfo)
                elif confs < confirmations:
                    newtxids.append((opid, txid))
            txids = newtxids

            logging.debug('')
            if len(txids) > 0:
                time.sleep(77)

        return not somefailed
