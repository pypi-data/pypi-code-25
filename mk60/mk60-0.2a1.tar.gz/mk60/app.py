import struct
import sys


sample_rate = 48000
soft_ends = True


assert sample_rate % 1000 == 0


def main():
    if len(sys.argv) < 1 + 2:
        raise SystemExit("specify input and output files in the command line")

    fi = open(sys.argv[1], 'rU')
    fo = open(sys.argv[2], 'wb')

    # skip header; will write it in the end
    fo.seek(44)
    data_size = 0

    # how many times shall repeat each sample
    rep = sample_rate // 1000

    # write introduction; takes about 1 sec.
    wave = bytearray(128 * 16 * rep)
    if soft_ends:
        # move levels to -127 slowly
        for v in range(128):
            wave[v * 16 * rep:(v + 1) * 16 * rep] = [0x80 - v] * 16 * rep
    else:
        # switch levels to -127 and keep for a while
        for v in range(128):
            wave[v * 16 * rep:(v + 1) * 16 * rep] = [0x01] * 16 * rep
    fo.write(wave)
    data_size += len(wave)

    # write data
    vv = [-127, -127]
    for s in fi:
        s = s.strip(' \n')
        if not s or s.startswith('#'):
            continue

        # read decimal code, like 0512, and convert it to byte
        d = int(s)
        hi, lo = d // 100, d % 100
        assert 0 <= hi <= 15 and 0 <= lo <= 15
        b = hi << 4 | lo

        # represent byte as a sequence of 8 bits, MSB first; append parity bit
        p = 0
        wave = bytearray(18 * rep)
        for i in range(8):
            ch = b >> (7 - i) & 1
            vv[ch] *= -1
            wave[i * 2 * rep:(i + 1) * 2 * rep] =\
                [0x80 + vv[0], 0x80 + vv[1]] * rep
            p ^= ch
        vv[p] *= -1
        wave[-2 * rep:] = [0x80 + vv[0], 0x80 + vv[1]] * rep

        fo.write(wave)
        data_size += len(wave)
    else:
        assert d == int('0512'), "file must end with '0512'"

    # write conclusion; takes about 1 sec.
    wave = bytearray(128 * 16 * rep)
    if soft_ends:
        # move levels to 0 slowly
        vv = [v // 127 for v in vv]
        for v in range(128):
            wave[v * 16 * rep + 0:(v + 1) * 16 * rep + 0:2] =\
                [0x80 + vv[0] * (127 - v)] * 8 * rep
            wave[v * 16 * rep + 1:(v + 1) * 16 * rep + 1:2] =\
                [0x80 + vv[1] * (127 - v)] * 8 * rep
    else:
        # keep levels fixed
        for v in range(128):
            wave[v * 16 * rep:(v + 1) * 16 * rep] =\
                [0x80 + vv[0], 0x80 + vv[1]] * 8 * rep
    fo.write(wave)
    data_size += len(wave)

    # write header
    fo.seek(0)
    head = struct.pack('<4sL4s4sLHHLLHH4sL',
                       b"RIFF", (0 + 4) + (8 + 16) + (8 + data_size), b"WAVE",
                       b"fmt ", 16, 1, 2, sample_rate, sample_rate * 2, 2, 8,
                       b"data", data_size)
    assert len(head) == 44
    fo.write(head)

    fi.close()
    fo.close()

    print("ok")
