#! /usr/bin/python3
# coding: utf-8

from bitstring import BitArray
import math
import pybfilter.hashf as hashf


class BloomFilter:
    def __init__(self, n=100, error=0.001):
        """
        >>> import pybfilter
        >>> bf = pybfilter.BloomFilter(n=10000, error=0.0001)
        :param n: expected number of items stored in Bloom Filter
        :param error: error rate
        """
        self.n = n
        if not n > 0:
            raise ValueError("BloomFilter: n must be > 0.")
        if not (0 < error < 1):
            raise ValueError("error must be between 0 and 1.")
        self.error = error  # error rate
        self.capacity = int(- self.n * math.log(self.error) / (math.log(2) ** 2)) + 1  # bloom filter capacity
        self.k = int(- math.log(self.error, 2)) + 1  # the number of hash functions
        self.count = 0  # stored data in bloom filter
        self.hashes = []  # hash functions list
        for i in range(10):
            self.hashes.append(getattr(hashf, "hashf" + str(i)))
        self.hashes.append(getattr(hashf, "hashf"))
        self.bits = BitArray(int=0, length=self.capacity)  # stored tag

    def add(self, key):
        """
        >>> bf = BloomFilter()
        >>> bf.add(1)
        True
        >>> bf.add(1)
        False
        :param key: add key to bloom filter
        :return: if key has been in bloom filter, return False, else True
        """
        key = str(key)  # convert all para to string
        # if self.count > self.capacity:
        #     raise IndexError("BloomFilter is at capacity.")
        if self.count > self.n:  # overload
            raise IndexError("BloomFilter is overload.")
            # pass
        all_found = True
        offset = 0
        for i in range(self.k):
            if i > 9:
                value = self.hashes[10](key, self.capacity, i % 10)
            else:
                value = self.hashes[i](key, self.capacity)
            if all_found and not self.bits[value]:
                all_found = False
            self.bits[offset + value] = True
        if not all_found:
            self.count += 1
            return True
        else:
            return False  # false means the key has been in bloom filter

    def __contains__(self, key):
        """
        >>> import pybfilter
        >>> bf = pybfilter.BloomFilter()
        >>> bf.add(1)
        True
        >>> 1 in bf
        True
        :param key: check if key is in Bloom Filter
        :return: if key in Bloom Filter, return True, else False
        """
        key = str(key)
        for i in range(self.k):
            if i > 9:
                value = self.hashes[10](key, self.capacity, i % 10)
            else:
                value = self.hashes[i](key, self.capacity)
            if not self.bits[value]:
                return False
        return True
