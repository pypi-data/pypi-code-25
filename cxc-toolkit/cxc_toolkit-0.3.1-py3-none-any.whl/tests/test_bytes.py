from cxc_toolkit.bytes import (
    xor,
)


class TestBytes():

    def test_xor(self):
        bytes_1 = b"h3ib"
        bytes_2 = b"wkmn"
        xor_shortest_hex = "1f58040c"
        xor_longest_hex = xor_shortest_hex
        assert xor_shortest_hex == xor(bytes_1, bytes_2).hex()
        assert xor_shortest_hex == xor(bytes_2, bytes_1).hex()
        assert xor_longest_hex == xor(bytes_1, bytes_2, longest=True).hex()
        assert xor_longest_hex == xor(bytes_2, bytes_1, longest=True).hex()

        bytes_1 = b"1\".# s_hi+"
        bytes_2 = b"@w-ch`~ss123&&"
        xor_shortest_hex = "715503404813211b1a1a"
        xor_longest_hex = "715503404813211b1a1a32332626"
        assert xor_shortest_hex == xor(bytes_1, bytes_2).hex()
        assert xor_shortest_hex == xor(bytes_2, bytes_1).hex()
        assert xor_longest_hex == xor(bytes_1, bytes_2, longest=True).hex()
        assert xor_longest_hex == xor(bytes_2, bytes_1, longest=True).hex()
