#! /usr/bin/python3
# coding: utf-8


def hashf0(key, capacity):
    res = 0
    for ch in key:
        res += ord(ch)
        res += res << 10
        res ^= res >> 6
    res += res << 3
    res ^= res >> 11
    res += res << 15
    return res % capacity


def hashf1(key, capacity):
    res = 5381
    for ch in key:
        res = ((res << 5) + res + ord(ch) - 31)
    return res % capacity


def hashf2(key, capacity):
    res = 0
    for ch in key:
        res = (ord(ch) + (res << 6) + (res << 16) - res)
    return res % capacity


def hashf3(key, capacity):
    seed = 131
    res = 0
    for ch in key:
        res = (res * seed + ord(ch))
    return res % capacity


def hashf4(key, capacity):
    seed = 31
    res = 0
    for ch in key:
        res = (res * seed + ord(ch))
    return res % capacity


def hashf5(key, capacity):
    seed = 3131
    res = 0
    for ch in key:
        res = (res * seed + ord(ch))
    return res % capacity


def hashf6(key, capacity):
    seed = 13131
    res = 0
    for ch in key:
        res = (res * seed + ord(ch))
    return res % capacity


def hashf7(key, capacity):
    res = len(key)
    for ch in key:
        res = ((res << 5) ^ (res >> 27) ^ ord(ch))
    return res % capacity


def hashf8(key, capacity):
    b = 378551
    a = 63689
    res = 0
    for ch in key:
        res = (res * a + ord(ch))
        a *= b
    return res % capacity


def hashf9(key, capacity):
    res = int("0x811c9dc5", 16)
    for ch in key:
        res ^= ord(ch)
        res *= int("0x01000193", 16)
    return res % capacity


def hashf(key, capacity, n):
    seed = int("313131" + "31" * n)
    res = 0
    for ch in key:
        res = (res * seed + ord(ch))
    return res % capacity
