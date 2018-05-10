import unittest
import simplejson
from factories import BlockFactory

class BlockFactoryTestCase(unittest.TestCase):
    def test_from_stream(self):
        stream = open('test_data/blk00001.dat', 'r')
        block = BlockFactory.from_stream(stream)

        self.assertIsNotNone(block)
        self.assertIsNotNone(block.bits)
        self.assertIsNone(block.chain)
        self.assertIsNone(block.chainwork)
        self.assertIsNotNone(block.dat)
        self.assertIsNotNone(block.difficulty)
        self.assertIsNotNone(block.hash)
        self.assertIsNone(block.height)
        self.assertIsNotNone(block.merkleroot)
        self.assertIsNone(block.nextblockhash)
        self.assertIsNotNone(block.nonce)
        self.assertIsNotNone(block.previousblockhash)
        self.assertIsNotNone(block.size)
        self.assertIsNotNone(block.target)
        self.assertIsNotNone(block.time)
        self.assertIsNotNone(block.total)
        self.assertIsNotNone(block.tx)
        self.assertIsNotNone(block.version)
        self.assertIsNotNone(block.work)

        for tr in block.tx:
            self._check_transaction(tr)
            for vin in tr.vin:
                self._check_vin(vin)

            for vout in tr.vout:
                self._check_vout(vout)

    def test_from_rpc(self):
        with open('test_data/rpc_data.json') as json_data:
            data = simplejson.load(json_data)
            block = BlockFactory.from_rpc(data['block'], data['transactions'])
            self.assertIsNotNone(block)
            self.assertIsNotNone(block.bits)
            self.assertIsNone(block.chain)
            self.assertIsNotNone(block.chainwork)
            self.assertIsNone(block.dat)
            self.assertIsNotNone(block.difficulty)
            self.assertIsNotNone(block.hash)
            self.assertIsNotNone(block.height)
            self.assertIsNotNone(block.merkleroot)
            self.assertIsNotNone(block.nextblockhash)
            self.assertIsNotNone(block.nonce)
            self.assertIsNotNone(block.previousblockhash)
            self.assertIsNotNone(block.size)
            self.assertIsNotNone(block.target)
            self.assertIsNotNone(block.time)
            self.assertIsNotNone(block.total)
            self.assertIsNotNone(block.tx)
            self.assertIsNotNone(block.version)
            self.assertIsNotNone(block.work)

            for tr in block.tx:
                self._check_transaction(tr)
                for vin in tr.vin:
                    self._check_vin(vin)

                for vout in tr.vout:
                    self._check_vout(vout)

    def _check_transaction(self, tr):
        self.assertIsNotNone(tr.blockhash)
        self.assertIsNotNone(tr.blocktime)
        self.assertIsNotNone(tr.locktime)
        self.assertIsNotNone(tr.total)
        self.assertIsNotNone(tr.txid)
        self.assertIsNotNone(tr.version)
        self.assertIsNotNone(tr.vin)
        self.assertIsNotNone(tr.vout)

    def _check_vin(self, vin):
        if vin.coinbase is None:
            self.assertIsNotNone(vin.prev_txid)
            self.assertIsNotNone(vin.vout_index)
            self.assertIsNotNone(vin.hex)
        else:
            self.assertIsNone(vin.prev_txid)
            self.assertIsNone(vin.vout_index)
            self.assertIsNone(vin.hex)

    def _check_vout(self, vout):
        pass


if __name__ == "__main__":
    unittest.main()
