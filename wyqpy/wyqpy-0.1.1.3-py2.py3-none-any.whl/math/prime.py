"""
Created on 2017年8月12日

@author: WYQ
"""

import math


def isPrime(n):
    """
    alter:from mpmath.libmp.libintmath import isprime
    @param n: 大于0
    @return: 判断n是否是质数
    """
    if n <= 1:
        return False
    for i in range(2, math.floor(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def isComposite(n):
    """
    @param n: 大于3
    @return: 判断n是否是合数
    """
    if n < 4 or isPrime(n):
        return False
    return True


def isOdd(n):
    """
    @param n: 大于等于0
    @return: 判断n是否是奇数
    """
    if n % 2 == 1:
        return True
    return False


def isEven(n):
    """
    @param n: 大于等于0
    @return: 判断n是否是偶数
    """
    if n % 2 == 0:
        return True
    return False


def getMaxPrime(n):
    """
    @param n: 大于等于2
    @return: 获取最大质数
    """
    if (n < 2):
        return None
    while True:
        if isPrime(n):
            return n
        n = n - 1


def getMaxComposite(n):
    """
    @param n: 大于等于4
    @return: 判断n是否是质数
    """
    if (n < 4):
        return None
    while True:
        if isComposite(n):
            return n
        n = n - 1


def getMaxEven(n):
    """
    @param n: 大于等于0
    @return: 获取最大偶数
    """
    if (n < 0):
        return None
    return n if isEven(n) else n - 1


def getMaxOdd(n):
    """
    @param n: 大于0
    @return: 获取最大奇数
    """
    if (n < 1):
        return None
    return n if isOdd(n) else n - 1


def getAllPrimes(minn, maxn):
    """
    @param minn: 大于等于0
    @param maxn: 大于等于minn
    @return: 获取所有质数
    """
    result = [];
    if minn <= 2:
        minn = 2
    if minn > maxn:
        return result;
    for i in range(minn, maxn + 1):
        if (isPrime(i)):
            result.append(i)
    return result


def getNextPrime(startPrime):
    if startPrime <= 0:
        raise ValueError("startPrime 必须大于0 ")
    n = startPrime + 1
    while (not isPrime(n)):
        n += 1
    return n


def getPrePrime(endPrime):
    if endPrime <= 0:
        raise ValueError("endPrime 必须大于0 ")
    n = endPrime - 1
    while (not isPrime(n)):
        n -= 1
        if n < 2:
            return None
    return n


def getNextPrimes(startPrime, count):
    cntu = True
    ps = []
    lp = startPrime
    while (len(ps) < count):
        p = getNextPrime(lp)
        ps.append(p)
        lp = p

    return ps


def getPrimePosition(p):
    if not isPrime(p):
        return None
    else:
        return len(getAllPrimes(0, p))


def getAllComposites(minn, maxn):
    """
    @param minn: 大于等于0
    @param maxn: 大于等于minn
    @return: 获取所有复数
    """
    result = [];
    if minn <= 2:
        minn = 2
    if minn > maxn:
        return result;
    for i in range(minn, maxn + 1):
        if (isComposite(i)):
            result.append(i)
    return result


def getAllEvens(minn, maxn):
    """
    @param minn: 大于等于0
    @param maxn: 大于等于minn
    @return: 获取所有偶数
    """
    result = [];
    if minn <= 0:
        minn = 0
    if minn > maxn:
        return result;
    for i in range(minn, maxn + 1):
        if (isEven(i)):
            result.append(i)
    return result


def getAllOdds(minn, maxn):
    """
    @param minn: 大于等于0
    @param maxn: 大于等于minn
    @return: 获取所有奇数
    """
    result = [];
    if minn <= 0:
        minn = 0
    if minn > maxn:
        return result;
    for i in range(minn, maxn + 1):
        if (isOdd(i)):
            result.append(i)
    return result


def getEDPrimes(n, max=1000):
    """
    获取n左右等距离的所有素数对
    :param n:
    :param max:
    :return:
    """
    d = 0
    l = n - d
    r = n + d
    ps = {}
    count = 0
    while l > 1 and count < max:
        if isPrime(l) and isPrime(r):
            ps[d] = [l, r]
            count += 1
        d = d + 1
        l = n - d
        r = n + d
    return ps


def getRightEDPrime(p, nmax=100, countmax=100):
    """
    获取p以n左右等距离的所有素数对
    :param p:
    :param max:
    :return:
    """
    count = 0
    d = 0
    n = p + d
    ps = {}
    while count < countmax and n < nmax:
        r = 2 * n - p
        if isPrime(r):
            ps[d] = [p, r, n]
            count = +1
        d += 1
        n = p + d

    return ps


def getLeftEDPrime(p):
    """
    获取p以n左右等距离的所有素数对
    :param p:
    :param max:
    :return:
    """
    d = 0
    n = p - d
    l = n - d
    ps = {}
    while l > 1:
        if isPrime(l):
            ps[d] = [l, p, n]
        d += 1
        n = p - d
        l = n - d
    return ps


def factorial(n):
    """
    @param n: 大于0
    @return: 返回n的阶乘
    """
    return math.factorial(n)


def wilsontop(n):
    """
    @param n: n为质数
    @return: 返回威尔逊分子
    """
    #     if not isPrime(n):
    #         return None
    return math.factorial(n - 1) + 1


def wilson(n):
    """
    @param n: n为质数
    @return: 返回威尔逊数
    """
    if not isPrime(n):
        return None
    return (math.factorial(n - 1) + 1) / n


def getNearPrimes(p, evenSpan=2, count=1):
    """
    """
    if evenSpan % 2 != 0 or isComposite(p) or count <= 0:
        return None
    result = []
    while count > 0:
        if isPrime(p):
            if isPrime(p + evenSpan):
                result.append([p, p + evenSpan])
                count -= 1
        p += 1
    return result


def getMuxPPrime(length=1):
    pp = 1;
    for p in getNextPrimes(1, length):
        pp = pp * p
    return pp + 1


def getAllMuxPPrimes(count=1):
    pps = []
    ps = getNextPrimes(1, count)
    for i in range(0, count):
        pp = 1;
        for j in range(0, i + 1):
            pp = pp * ps[j]
        pps.append(pp + 1)

    return pps


"""
Odd Even Composite
"""

"""
factor
"""

import random
from collections import Counter


def gcd(a, b):
    if a == 0:
        return b
    if a < 0:
        return gcd(-a, b)
    while b > 0:
        c = a % b
        a, b = b, c
    return a


def mod_mul(a, b, n):
    result = 0
    while b > 0:
        if (b & 1) > 0:
            result = (result + a) % n
        a = (a + a) % n
        b = (b >> 1)
    return result


def mod_exp(a, b, n):
    result = 1
    while b > 0:
        if (b & 1) > 0:
            result = mod_mul(result, a, n)
        a = mod_mul(a, a, n)
        b = (b >> 1)
    return result


def MillerRabinPrimeCheck(n):
    if n in {2, 3, 5, 7, 11}:
        return True
    elif (n == 1 or n % 2 == 0 or n % 3 == 0 or n % 5 == 0 or n % 7 == 0 or n % 11 == 0):
        return False
    k, u = 0, n - 1
    while not (u & 1) > 0:
        k += 1
        u = (u >> 1)
    random.seed(0)
    s = 5
    for i in range(s):
        x = random.randint(2, n - 1)
        if x % n == 0:
            continue
        x = mod_exp(x, u, n)
        pre = x
        for j in range(k):
            x = mod_mul(x, x, n)
            if (x == 1 and pre != 1 and pre != n - 1):
                return False
            pre = x
        if x != 1:
            return False
        return True


def Pollard_rho(x, c):
    (i, k) = (1, 2)
    x0 = random.randint(0, x)
    y = x0
    while 1:
        i += 1
        x0 = (mod_mul(x0, x0, x) + c) % x
        d = gcd(y - x0, x)
        if d != 1 and d != x:
            return d
        if y == x0:
            return x
        if i == k:
            y = x0
            k += k


def PrimeFactorsListGenerator(n):
    result = []
    if n <= 1:
        return None
    if MillerRabinPrimeCheck(n):
        return [n]
    p = n
    while p >= n:
        p = Pollard_rho(p, random.randint(1, n - 1))
    result.extend(PrimeFactorsListGenerator(p))
    result.extend(PrimeFactorsListGenerator(n // p))
    return result


def PrimeFactorsListCleaner(n):
    return Counter(PrimeFactorsListGenerator(n))


def PrimeFactorsListCleanerSorted(n):
    d = PrimeFactorsListCleaner(n);
    ks = sorted(d.keys())
    nd = {}
    for k in ks:
        nd[k] = d[k]
    return nd
