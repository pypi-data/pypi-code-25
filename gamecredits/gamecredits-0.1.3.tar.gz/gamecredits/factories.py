from helpers import *
import binascii
import enum

from pybitcointools import bin_to_b58check, pubkey_to_address

from entities import Block, BlockHeader, Transaction, Vin, Vout
from helpers import calculate_target, calculate_work

import constants


# Operator types for output script parsing
class ScriptOperator(enum.Enum):
    OP_CHECKSIG = "ac"
    OP_DUP = "76"
    OP_HASH160 = "a9"
    OP_EQUAL = "87"
    OP_EQUALVERIFY = "88"
    OP_RETURN = "6a"
    OP_CHECKMULTISIG = 'ae'


class BlockFactory(object):
    @staticmethod
    def _parse_block_header(stream):
        # Calculate the block hash from the header
        header_bytes = stream.read(80)
        block_hash = double_sha(header_bytes, reverse=True)

        # Rewind 80 bytes back so I can parse stuff
        # OPTIMIZE: use io.BytesIO to pass bytes as a stream
        stream.seek(-80, 1)

        # A version number to track software/protocol upgrades
        version = uint4(stream)

        # A reference to the hash of the previous (parent) block in the chain
        previousblockhash = hash32(stream)

        # A hash of the root of the merkle tree of this blocks ParsedTransactions
        merkleroot = hash32(stream)[::-1]

        # The approximate creation time of this block (seconds from Unix Epoch)
        time = uint4(stream)

        # Difficulty bits in hexadeximal format
        # This notation expresses the difficulty target as a coefficient/exponent format,
        # with the first two hexadecimal digits for the exponent
        # and the rest as the coefficient.
        bits = hex(uint4(stream))

        target = calculate_target(bits)

        # Difficulty is calculated as a ratio between the maximum allowed difficulty
        # and the blocks difficulty target
        difficulty = round(float(constants.MAX_DIFFICULTY) / target, 8)

        # A counter used for the proof-of-work algorithm
        nonce = uint4(stream)

        # Block work is calculated as 2^256 / (target + 1)
        # rounded down to the nearest integer
        # See the GetBlockWork() function in the main.h file
        # https://github.com/gamecredits-project/GameCredits/blob/4c1844a3ffecfbd222ee68cbac1f1fc7ec2072e5/src/main.h
        work = calculate_work(target)

        return BlockHeader(
            hash=block_hash,
            version=version,
            previousblockhash=previousblockhash,
            merkleroot=merkleroot,
            time=time,
            bits=bits,
            target=target,
            difficulty=difficulty,
            nonce=nonce,
            work=work
        )

    @staticmethod
    def from_stream(stream):
        # Info about the dat file we parsed the block from
        dat = {
            "index": int(stream.name[-5:-4]),
            "start": stream.tell()
        }

        # Skip first 4 bytes bcs the contain the magic number
        # which is a protocol identifier and always the same
        stream.seek(4, 1)

        # Size of this block in bytes
        size = uint4(stream)

        # Parse the block header
        header = BlockFactory._parse_block_header(stream)

        # Number of ParsedTransactions in this block
        txcount = varint(stream)

        try:
            # First ParsedTransaction in a block is a "coinbase" transaction
            # that transfers newly generated coins to a miner
            # and has a slightly different input format
            tx = [TransactionFactory.from_stream(stream, header.hash, header.time, coinbase=True)]

            # Append other ParsedTransactions (if there are any)
            for i in range(1, txcount):
                tx.append(TransactionFactory.from_stream(stream, header.hash, header.time))
        except Exception:
            print "Problematic block: %s" % header.hash
            raise

        total = sum([tr.total for tr in tx])

        dat["end"] = stream.tell()

        return Block(
            size=size,
            header=header,
            tx=tx,
            dat=dat,
            total=total
        )

    @staticmethod
    def from_rpc(rpc_block, rpc_tx):
        bits = '0x' + rpc_block['bits']
        target = calculate_target(bits)
        work = calculate_work(target)
        tx = [TransactionFactory.from_rpc(tr) for tr in rpc_tx]
        total = sum([tr.total for tr in tx])

        header = BlockHeader(
            hash=rpc_block['hash'],
            version=rpc_block['version'],
            previousblockhash=rpc_block['previousblockhash'],
            merkleroot=rpc_block['merkleroot'],
            time=rpc_block['time'],
            bits=bits,  # We use 0x repr for hex strings
            difficulty=rpc_block['difficulty'],
            nonce=rpc_block['nonce'],
            target=target,
            work=work
        )

        return Block(
            size=rpc_block['size'],
            header=header,
            tx=tx,
            nextblockhash=rpc_block.get('nextblockhash'),
            height=rpc_block['height'],
            chainwork=int(rpc_block['chainwork'], 16),
            total=total
        )


class TransactionFactory(object):
    @staticmethod
    def from_stream(stream, blockhash, blocktime, coinbase=False):
        tr_start = stream.tell()

        # A version number to track software/protocol upgrades
        version = uint4(stream)

        # Number of inputs in this ParsedTransaction
        vin_count = varint(stream)

        skip = 0
        # Parse the coinbase input
        if coinbase:
            vin = [VinFactory.from_stream(stream, coinbase=True)]
            skip = 1
        else:
            vin = []

        # Parse other inputs (if they exist)
        for i in range(skip, vin_count):
            vin.append(VinFactory.from_stream(stream))

        # Number of outputs in this transction
        vout_count = varint(stream)

        # Parse the ParsedTransaction outputs
        vout = [VoutFactory.from_stream(stream) for index in range(0, vout_count)]

        # ParsedTransaction locktime
        locktime = uint4(stream)

        tr_end = stream.tell()

        # rewind so we can calculate the txid
        # OPTIMIZE: use io.BytesIO to pass bytes as a stream
        stream.seek(tr_start)
        tr_bytes = stream.read(tr_end - tr_start)
        txid = double_sha(tr_bytes, reverse=True)

        # Set the output indexes and parent txid
        for (i, v) in enumerate(vout):
            v.txid = txid
            v.index = i

        # Set the input parent txids
        for v in vin:
            v.txid = txid

        total = round(sum([v.value for v in vout]), 8)

        return Transaction(
            version=version,
            vin=vin,
            vout=vout,
            locktime=locktime,
            txid=txid,
            total=total,
            blockhash=blockhash,
            blocktime=blocktime
        )

    @staticmethod
    def from_rpc(rpc_tr):
        vin = [VinFactory.from_rpc(vin) for vin in rpc_tr['vin']]
        vout = [VoutFactory.from_rpc(vout) for vout in rpc_tr['vout']]
        total = sum([v.value for v in vout])

        return Transaction(
            version=rpc_tr['version'],
            vin=vin,
            vout=vout,
            locktime=rpc_tr['locktime'],
            txid=rpc_tr['txid'],
            total=total,
            blockhash=rpc_tr['blockhash'],
            blocktime=rpc_tr['blocktime']
        )


class VinFactory(object):
    @staticmethod
    def from_stream(stream, coinbase=False):
        if not coinbase:
            prev_txid = hash32(stream)
            vout_index = uint4(stream)
            script_len = varint(stream)
            script_hex = binascii.hexlify(stream.read(script_len))
            sequence = uint4(stream)

            return Vin(
                prev_txid=prev_txid,
                vout_index=vout_index,
                hex=script_hex,
                sequence=sequence,
            )
        else:
            # Throw away these values for coinbase ParsedTransactions
            _ = (hash32(stream), uint4(stream))

            script_len = varint(stream)
            coinbase = binascii.hexlify(stream.read(script_len))
            sequence = uint4(stream)

            return Vin(
                coinbase=coinbase,
                sequence=sequence
            )

    @staticmethod
    def from_rpc(rpc_vin):
        if 'coinbase' not in rpc_vin:
            return Vin(
                prev_txid=rpc_vin['txid'],
                vout_index=rpc_vin['vout'],
                hex=rpc_vin['scriptSig']['hex'],
                sequence=rpc_vin['sequence'],
            )
        else:
            return Vin(
                coinbase=rpc_vin['coinbase'],
                sequence=rpc_vin['sequence'],
            )


class VoutFactory(object):
    @staticmethod
    def parse_script(script):
        """
        Parses the bitcoin script - https://en.bitcoin.it/wiki/Script,
        currently supports only pay2pubkey and pay2pubkeyhash ParsedTransactions
        """
        if script[:4] == ScriptOperator.OP_DUP.value + ScriptOperator.OP_HASH160.value:
            # Pay to public key hash ParsedTransaction
            (pubkey, address) = VoutFactory.parse_pay2pubkey_hash(script)
            return {
                "asm": "OP_DUP OP_HASH160 %s OP_EQUALVERIFY OP_CHECKSIG" % pubkey,
                "reqSigs": 1,
                "type": "pubkeyhash",
                "addresses": [address]
            }
        elif script[-2:] == ScriptOperator.OP_CHECKSIG.value:
            # Pay to public key ParsedTransaction (deprecated)
            (pubkey, address) = VoutFactory.parse_pay2pubkey(script)
            return {
                "asm": "%s OP_CHECKSIG" % pubkey,
                "reqSigs": 1,
                "type": "pubkey",
                "addresses": [address]
            }
        elif script[:2] == ScriptOperator.OP_RETURN.value:
            # Nulldata ParsedTransaction - https://bitcoin.org/en/glossary/null-data-ParsedTransaction
            return {
                "asm": "OP_RETURN %s" % script[4:],
                "type": "nulldata"
            }
        elif script[:2] == ScriptOperator.OP_HASH160.value:
            # Pay to script hash ParsedTransaction - https://en.bitcoin.it/wiki/Pay_to_script_hash
            (pubkey, address) = VoutFactory.parse_pay2scripthash(script)
            return {
                "asm": "OP_HASH160 %s OP_EQUAL" % pubkey,
                "reqSigs": 1,
                "type": "scripthash",
                "addresses": [address]
            }
        elif script[-2:] == ScriptOperator.OP_CHECKMULTISIG.value:
            # Multisignature script - https://en.bitcoin.it/wiki/Multisignature
            (pubkeys, addresses, req_sigs, possible_sigs) = VoutFactory.parse_multisig(script)
            return {
                "asm": "%s %s %s OP_CHECKMULTISIG" % (req_sigs[0], " ".join([pubkey for pubkey in pubkeys]), possible_sigs[0]),
                "reqSigs": req_sigs[0],
                "type": "multisig",
                "addresses": addresses
            }
        else:
            raise Exception("[PARSE_SCRIPT] Unknown script format: %s" % script)

    @staticmethod
    def parse_pay2pubkey(script):
        # First 2 bytes is num bytes to be pushed to the stack
        # Last 2 are OP_CHECKSIG, pubkey is in the middle
        pubkey = script[2:-2]

        # Create address from public key (HASH160 + B58_CHECK)
        address = pubkey_to_address(pubkey, magicbyte=constants.PAY_TO_PUBKEY_VERSION_PREFIX)

        return (pubkey, address)

    @staticmethod
    def parse_pay2pubkey_hash(script):
        # Extract pubkey hash from script
        # First 2 bytes is OP_DUP, second 2 bytes is OP_HASH160
        # Then there are 2 bytes representing how much data is pushed to the stack (not important just skip them)
        # That's why we start at 6, last four bytes are OP_EQUALVERIFY and OP_CHECKSIG so we end at -4
        pubkey = script[6:-4]

        # Public Key Hash is equivalent to the GAME address,
        # it has been hashed twice but without the Base58Check encoding,
        # so we need only to encode it
        address = bin_to_b58check(binascii.unhexlify(pubkey), constants.PAY_TO_PUBKEY_VERSION_PREFIX)

        return (pubkey, address)

    @staticmethod
    def parse_pay2scripthash(script):
        # First 2 bytes is OP_HASH160
        # Second 2 bytes is num bytes to be pushed to the stack
        # Then comes the pubkey
        pubkey = script[4:-2]

        # P2SH addresses use the version prefix 5, which results in
        # Base58Check-encoded addresses that start with a 3
        address = bin_to_b58check(binascii.unhexlify(pubkey), constants.PAY_TO_SCRIPT_VERSION_PREFIX)

        return (pubkey, address)

    @staticmethod
    def remove_chars(pubs):
        # This is exclusively used for compressed public keys.
        # Start needs to be changed according to len of public keys
        # when uncopressed keys are implemented, start needs to be
        # method parameter.
        start = 66
        for index in range(len(pubs)):
            if index == start:
                pubs = pubs[:index] + pubs[start+2:]                
                start += 66
        return pubs    

    @staticmethod
    def get_pubs(pubs_list):
        # Returning all public keys as an array.
        # 66 number needs to be changed as soon as uncompressed keys 
        # are implemented
        pubs = VoutFactory.remove_chars(pubs_list)
        pubs = [pubs[i:i+66] for i in range(0, len(pubs), 66)]
        return pubs

    @staticmethod
    def get_addr_from_pub(pubkey):
        # Multisignature addresses have the same prefix as pay2pubkey addresses
        return pubkey_to_address(pubkey, magicbyte=constants.PAY_TO_PUBKEY_VERSION_PREFIX)

    @staticmethod
    def parse_multisig(script):
        # https://en.bitcoin.it/wiki/Script#Constants
        # Numbers of public keys possible to insert into script 2-16
        num_of_pubs = {
            "82": 2, "83": 3, "84": 4, "85": 5,
            "86": 6, "87": 7, "88": 8, "89": 9,
            "90": 10, "91": 11, "92": 12, "93": 13, 
            "94": 14, "95": 15, "96": 16
        }

        # Number of public keys found in multisig script
        req_sigs = [value for key, value in num_of_pubs.iteritems() if int('0x'+script[:2], 16) == int(key)]
        
        # Number of public keys that have been envolved in multisignature transaction
        possible_sigs = [value for key, value in num_of_pubs.iteritems() if int('0x'+script[-4:-2], 16) == int(key)]

        # Type of public key 02 is for compressed, 03 and 04 prefix is for uncompressed
        # Fix this ASAP, because this currently only supports compressed keys
        pubs = script[4:-4]
        if script[4:6] == '02':
            pubkeys = VoutFactory.get_pubs(pubs)
 
        # Get addresses from public keys
        addresses = [VoutFactory.get_addr_from_pub(pub) for pub in pubkeys]
        return (pubkeys, addresses, req_sigs, possible_sigs)



    @staticmethod
    def from_stream(stream):
        # Value in satoshi, convert it to GAME
        value = uint8(stream) * 10e-9

        # Length of the script after this in bytes
        script_len = varint(stream)

        # Read script of length script_len
        # REMEMBER: use binascii not the custom bin_to_hex function
        # because bin_to_hex ignored zeroes for some reason
        script_hex = binascii.hexlify(stream.read(script_len))

        # Parse the script to extract addresses
        parsed = VoutFactory.parse_script(script_hex)

        asm = parsed.get("asm")
        addresses = parsed.get("addresses")
        script_type = parsed.get("type")
        reqSigs = parsed.get("reqSigs")

        return Vout(
            value=value,
            hex=script_hex,
            asm=asm,
            type=script_type,
            addresses=addresses,
            reqSigs=reqSigs,
            spent=False
        )

    @staticmethod
    def from_rpc(rpc_vout):
        return Vout(
            value=float(rpc_vout['value']),
            hex=rpc_vout['scriptPubKey']['hex'],
            asm=rpc_vout['scriptPubKey']['asm'],
            type=rpc_vout['scriptPubKey']['type'],
            addresses=rpc_vout['scriptPubKey'].get('addresses'),
            reqSigs=rpc_vout['scriptPubKey'].get('reqSigs'),
            spent=False
        )
