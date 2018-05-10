class Block(object):
    def __init__(self, **kwargs):
        # REQUIRED ARGUMENTS
        # Size of this block in bytes
        self.size = kwargs['size']

        # Block header
        header = kwargs['header']

        # Unpack the header
        for (key, val) in header.__dict__.iteritems():
            setattr(self, key, val)

        # List of block transactions
        self.tx = kwargs['tx']

        # OPTIONAL ARGUMENTS
        # Information about the blocks position in a dat file:
        self.dat = kwargs.get('dat')

        # Hash of the next block in the chain
        self.nextblockhash = kwargs.get('nextblockhash')

        # Position of the block in the chain
        self.height = kwargs.get('height')

        # Cumulative amount of work done to get to this block
        # Used to determine the best chain
        self.chainwork = kwargs.get('chainwork')

        # Index of the chain this block belongs to
        # (main chain or sidechain)
        self.chain = kwargs.get('chain')

        # Total amount in all transactions
        self.total = kwargs.get('total')

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.hash == other.hash and self.height == other.height
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "<gamecredits.entities.Block: hash=%s, height=%s>" % (self.hash, self.height)

    def __repr__(self):
        return "<gamecredits.entities.Block: hash=%s, height=%s>" % (self.hash, self.height)


class BlockHeader(object):
    def __init__(self, **kwargs):
        # Block hash (unique identifier)
        self.hash = kwargs['hash']

        # A version number to track software/protocol upgrades
        self.version = kwargs['version']

        # A reference to the hash of the previous (parent) block in the chain
        self.previousblockhash = kwargs['previousblockhash']

        # A hash of the root of the merkle tree of this blocks ParsedTransactions
        self.merkleroot = kwargs['merkleroot']

        # The approximate creation time of this block (seconds from Unix Epoch)
        self.time = kwargs['time']

        # Difficulty bits in hexadeximal format
        # This notation expresses the difficulty target as a coefficient/exponent format,
        # with the first two hexadecimal digits for the exponent
        # and the rest as the coefficient.
        self.bits = kwargs['bits']

        # Difficulty target
        self.target = kwargs['target']

        # Difficulty is calculated as a ratio between the maximum allowed difficulty
        # and the blocks difficulty target
        self.difficulty = kwargs['difficulty']

        # A counter used for the proof-of-work algorithm
        self.nonce = kwargs['nonce']

        # Block work
        self.work = kwargs['work']

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.hash == other.hash
        return False

    def __ne__(self, other):
        """Define a non-equality test"""
        return not self.__eq__(other)


class Transaction(object):
    def __init__(self, **kwargs):
        # A version number to track software/protocol upgrades
        self.version = kwargs.get('version')

        # Transaction inputs
        self.vin = kwargs.get('vin')

        # Transaction outputs
        self.vout = kwargs.get('vout')

        self.locktime = kwargs.get('locktime')

        # Transaction hash (unique identifier)
        self.txid = kwargs.get('txid')

        # Total value of all outputs
        self.total = kwargs.get('total')

        # Hash of the block this transaction belongs to
        self.blockhash = kwargs.get('blockhash')

        # Block mined time
        self.blocktime = kwargs.get('blocktime')

        # Transaction main/side chain
        self.main_chain = kwargs.get('main_chain')
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.txid == other.txid
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "<gamecredits.entities.Transaction: txid=%s, blockhash=%s>" % (self.txid, self.blockhash)

    def __repr__(self):
        return "<gamecredits.entities.Transaction: txid=%s, blockhash=%s>" % (self.txid, self.blockhash)


class Vin(object):
    def __init__(self, **kwargs):
        # Identifier of the parent transaction
        self.txid = kwargs.get('txid')

        # Identifier of the tr that holds the output to be spent
        self.prev_txid = kwargs.get('prev_txid')

        # Position of the output in previous transaction
        self.vout_index = kwargs.get('vout_index')

        # Spending script in hexadecimal format
        self.hex = kwargs.get('hex')

        # Sequence number
        self.sequence = kwargs.get('sequence')

        # Coinbase hex for generation transactions
        self.coinbase = kwargs.get('coinbase')

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.txid == other.txid and self.prev_txid == other.prev_txid \
                and other.vout_index == self.vout_index and other.hex == self.hex \
                and other.sequence == self.sequence and other.coinbase == self.coinbase
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "<gamecredits.entities.Vin: txid=%s, prev_txid=%s, vout_index=%s>" \
            % (self.txid, self.prev_txid, self.vout_index)

    def __repr__(self):
        return "<gamecredits.entities.Vin: txid=%s, prev_txid=%s, vout_index=%s" \
            % (self.txid, self.prev_txid, self.vout_index)


class Vout(object):
    def __init__(self, **kwargs):
        # Amount transfered
        self.value = kwargs.get('value')

        # Hexadecimal representation of the output script
        self.hex = kwargs.get('hex')

        self.asm = kwargs.get('asm')

        # Output addresses
        self.addresses = kwargs.get('addresses')

        # Output type
        self.type = kwargs.get('type')

        # Num signatures required to unlock the output
        self.reqSigs = kwargs.get('reqSigs')

        # Txid of the transaction containing this output
        self.txid = kwargs.get('txid')

        # Index of this output in the transaction
        self.index = kwargs.get('index')

        # Is this output spent?
        self.spent = kwargs.get('spent')

