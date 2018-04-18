"""
A BIP0032-style hierarchical wallet.

Implement a BIP0032-style hierarchical wallet which can create public
or private wallet keys. Each key can create many child nodes. Each node
has a wallet key and a corresponding private & public key, which can
be used to generate Bitcoin addresses or WIF private keys.

At any stage, the private information can be stripped away, after which
descendants can only produce public keys.

Private keys can also generate "hardened" children, which cannot be
generated by the corresponding public keys. This is useful for generating
"change" addresses, for example, which there is no need to share with people
you give public keys to.
"""

import hashlib
import hmac
import struct

from ..encoding.b58 import b2a_hashed_base58
from ..encoding.bytes32 import from_bytes_32, to_bytes_32
from ..encoding.exceptions import EncodingError
from ..encoding.sec import public_pair_to_hash160_sec
from .Key import Key
from .bip32 import subkey_public_pair_chain_code_pair, subkey_secret_exponent_chain_code_pair
from .subpaths import subpaths_for_path_range


class PublicPrivateMismatchError(Exception):
    pass


class BIP32Node(Key):
    """
    This is a deterministic wallet that complies with BIP0032
    https://en.bitcoin.it/wiki/BIP_0032
    """

    @classmethod
    def from_master_secret(class_, generator, master_secret):
        """Generate a Wallet from a master password."""
        I64 = hmac.HMAC(key=b"Bitcoin seed", msg=master_secret, digestmod=hashlib.sha512).digest()
        return class_(generator=generator, chain_code=I64[32:], secret_exponent=from_bytes_32(I64[:32]))

    def __init__(self, generator, chain_code, depth=0, parent_fingerprint=b'\0\0\0\0', child_index=0,
                 secret_exponent=None, public_pair=None):
        """Don't use this. Use a classmethod to generate from a string instead."""

        if [secret_exponent, public_pair].count(None) != 1:
            raise ValueError("must include exactly one of public_pair and secret_exponent")

        super(BIP32Node, self).__init__(
            secret_exponent=secret_exponent, generator=generator, public_pair=public_pair,
            prefer_uncompressed=False, is_compressed=True, is_pay_to_script=False)

        if secret_exponent:
            self._secret_exponent_bytes = to_bytes_32(secret_exponent)

        if not isinstance(chain_code, bytes):
            raise TypeError("chain code must be bytes")
        if len(chain_code) != 32:
            raise ValueError("chain code wrong length")
        self._chain_code = chain_code
        self._depth = depth
        if len(parent_fingerprint) != 4:
            raise EncodingError("parent_fingerprint wrong length")
        self._parent_fingerprint = parent_fingerprint
        self._child_index = child_index
        self._prefer_uncompressed = False
        self._subkey_cache = dict()

    def chain_code(self):
        return self._chain_code

    def tree_depth(self):
        return self._depth

    def parent_fingerprint(self):
        return self._parent_fingerprint

    def child_index(self):
        return self._child_index

    def serialize(self, as_private=None, ui_context=None):
        """Yield a 78-byte binary blob corresponding to this node."""
        if as_private is None:
            as_private = self.secret_exponent() is not None
        if self.secret_exponent() is None and as_private:
            raise PublicPrivateMismatchError("public key has no private parts")

        ui_context = self._ui_context(ui_context)
        ba = bytearray()
        if as_private:
            ba.extend(ui_context.bip32_private_prefix())
        else:
            ba.extend(ui_context.bip32_public_prefix())
        ba.extend([self._depth])
        ba.extend(self._parent_fingerprint + struct.pack(">L", self._child_index) + self._chain_code)
        if as_private:
            ba += b'\0' + self._secret_exponent_bytes
        else:
            ba += self.sec(use_uncompressed=False)
        return bytes(ba)

    def fingerprint(self):
        return public_pair_to_hash160_sec(self.public_pair(), compressed=True)[:4]

    def hwif(self, as_private=False, ui_context=None):
        """Yield a 111-byte string corresponding to this node."""
        return b2a_hashed_base58(self.serialize(as_private=as_private, ui_context=ui_context))

    as_text = hwif
    wallet_key = hwif

    def public_copy(self):
        """Yield the corresponding public node for this node."""
        d = dict(generator=self._generator, chain_code=self._chain_code,
                 depth=self._depth, parent_fingerprint=self._parent_fingerprint,
                 child_index=self._child_index, public_pair=self.public_pair())
        return self.__class__(**d)

    def _subkey(self, i, is_hardened, as_private):
        if i < 0:
            raise ValueError("i can't be negative")
        if i >= 0x80000000:
            raise ValueError("subkey index 0x%x too large" % i)
        i &= 0x7fffffff
        if is_hardened:
            i |= 0x80000000

        d = dict(depth=self._depth+1, parent_fingerprint=self.fingerprint(), child_index=i)

        if self.secret_exponent() is None:
            if is_hardened:
                raise PublicPrivateMismatchError("can't derive a private key from a public key")
            d["public_pair"], chain_code = subkey_public_pair_chain_code_pair(
                self._generator, self.public_pair(), self._chain_code, i)
        else:
            d["secret_exponent"], chain_code = subkey_secret_exponent_chain_code_pair(
                self._generator, self.secret_exponent(), self._chain_code, i, is_hardened, self.public_pair())
        d["chain_code"] = chain_code
        d["generator"] = self._generator
        key = self.__class__(**d)
        if not as_private:
            key = key.public_copy()
        return key

    def __repr__(self):
        r = self.as_text(as_private=False)
        if self.secret_exponent():
            return "private_for <%s>" % r
        return "<%s>" % r

    def subkey(self, i=0, is_hardened=False, as_private=None):
        """Yield a child node for this node.

        i: the index for this node.
        is_hardened: use "hardened key derivation". That is, the public version
            of this node cannot calculate this child.
        as_private: set to True to get a private subkey."""
        if as_private is None:
            as_private = self.secret_exponent() is not None
        is_hardened = not not is_hardened
        as_private = not not as_private
        lookup = (i, is_hardened, as_private)
        if lookup not in self._subkey_cache:
            self._subkey_cache[lookup] = self._subkey(i, is_hardened, as_private)
        return self._subkey_cache[lookup]

    def subkey_for_path(self, path):
        """
        path: a path of subkeys denoted by numbers and slashes. Use H or p
            for private key derivation. End with .pub to force the key
            public.

        Examples: 1H/5/2/1 would call subkey(i=1, is_hardened=True)
            .subkey(i=5).subkey(i=2).subkey(i=1) and then yield the
            private key 0/0/458.pub would call subkey(i=0).subkey(i=0)
            .subkey(i=458) and then yield the public key

        You should choose one of the H or p convention for private key
        derivation and stick with it.
        """
        force_public = (path[-4:] == '.pub')
        if force_public:
            path = path[:-4]
        key = self
        if path:
            invocations = path.split("/")
            for v in invocations:
                is_hardened = v[-1] in ("'pH")
                if is_hardened:
                    v = v[:-1]
                v = int(v)
                key = key.subkey(i=v, is_hardened=is_hardened, as_private=key.secret_exponent() is not None)
        if force_public and key.secret_exponent() is not None:
            key = key.public_copy()
        return key

    def subkeys(self, path):
        """
        A generalized form that can return multiple subkeys.
        """
        for _ in subpaths_for_path_range(path, hardening_chars="'pH"):
            yield self.subkey_for_path(_)

    def children(self, max_level=50, start_index=0, include_hardened=True):
        for i in range(start_index, max_level+start_index+1):
            yield self.subkey(i)
            if include_hardened:
                yield self.subkey(i, is_hardened=True)


"""
The MIT License (MIT)

Copyright (c) 2013 by Richard Kiss

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
