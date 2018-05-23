# Austin Griffith
# Barriers

import numpy as np
from scipy.stats import norm

# lambda constant
def _lambdaVal(r,vol,q):
    l = 1 + (r - q - vol*vol*0.5) / (vol*vol)
    return(l)

# I's are set values used as the analytical solution to the barrier options
def _I1(alpha,beta,s,k,r,Z,T,vol,q):
    L = _lambdaVal(r,vol,q)
    xval = np.log(s/k) / (vol*np.sqrt(T)) + L*vol*np.sqrt(T)
    partial = alpha*s*norm.cdf(alpha*xval) - alpha*k*np.exp(-r*T)*norm.cdf(alpha*xval - alpha*vol*np.sqrt(T))
    return(partial)

def _I2(alpha,beta,s,k,r,Z,T,vol,q):
    L = _lambdaVal(r,vol,q)
    xval = np.log(s/Z)/(vol*np.sqrt(T)) + L*vol*np.sqrt(T)
    partial = alpha*s*norm.cdf(alpha*xval) - alpha*k*np.exp(-r*T)*norm.cdf(alpha*xval - alpha*vol*np.sqrt(T))
    return(partial)

def _I3(alpha,beta,s,k,r,Z,T,vol,q):
    L = _lambdaVal(r,vol,q)
    xval = np.log(np.square(Z)/(s*k))/(vol*np.sqrt(T)) + L*vol*np.sqrt(T)
    partial = (alpha*s*np.power(Z/s,2*L)*norm.cdf(beta*xval) -
        alpha*k*np.exp(-r*T)*np.power(Z/s,2*L-2)*norm.cdf(beta*xval-beta*vol*np.sqrt(T)))
    return(partial)

def _I4(alpha,beta,s,k,r,Z,T,vol,q):
    L = _lambdaVal(r,vol,q)
    xval = np.log(Z/s)/(vol*np.sqrt(T)) + L*vol*np.sqrt(T)
    partial = (alpha*s*np.power(Z/s,2*L)*norm.cdf(beta*xval) -
        alpha*k*np.exp(-r*T)*np.power(Z/s,2*L - 2)*norm.cdf(beta*xval - beta*vol*np.sqrt(T)))
    return(partial)

# out barriers
def DownOutPutLow(s,k,r,Z,T,vol,q):
    '''
    Calculate the Down-and-Out Put option, where barrier is less than strike

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.)
        Spot value of underlying asset at current time, t
    k : number of any type (int, float8, float64 etc.)
        Strike value of option, determined at initiation
    r : number of any type (int, float8, float64 etc.)
        Risk free interest rate, implied constant till expiration
    Z : number of any type (int, float8, float64 etc.)
        Barrier value of option, determined at initiation
    T : number of any type (int, float8, float64 etc.)
        Time till expiration for option, can be interpreted as 'T - t' should
        the option already be initiated, and be 't' time from time = 0
    vol : number of any type (int, float8, float64 etc.)
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.)
        Continuous dividend payout, as a percentage

    * Z < k must hold true for this function

    Returns
    -------
    price : float
        Price value of barrier option.

    Examples
    --------
    >>> from qcfoptions.barriers import DownOutPutLow
    >>> s = 1
        k = 1
        r = 0.015
        Z = 0.6
        T = 2
        vol = 0.25
        q = 0.01
    >>> DownOutPutLow(s,k,r,Z,T,vol,q)
    0.05510635577234088

    '''
    a = -1
    b = 1

    if s >= Z:
        price = (_I1(a,b,s,k,r,Z,T,vol,q) - _I2(a,b,s,k,r,Z,T,vol,q) +
                _I3(a,b,s,k,r,Z,T,vol,q) - _I4(a,b,s,k,r,Z,T,vol,q))
    else:
        price = 0.0
    return(max(price, 0.0))

def DownOutCall(s,k,r,Z,T,vol,q):
    '''
    Calculate the Down-and-Out Call option, for any barrier

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.)
        Spot value of underlying asset at current time, t
    k : number of any type (int, float8, float64 etc.)
        Strike value of option, determined at initiation
    r : number of any type (int, float8, float64 etc.)
        Risk free interest rate, implied constant till expiration
    Z : number of any type (int, float8, float64 etc.)
        Barrier value of option, determined at initiation
    T : number of any type (int, float8, float64 etc.)
        Time till expiration for option, can be interpreted as 'T - t' should
        the option already be initiated, and be 't' time from time = 0
    vol : number of any type (int, float8, float64 etc.)
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.)
        Continuous dividend payout, as a percentage

    Returns
    -------
    price : float
        Price value of barrier option.

    Examples
    --------
    >>> from qcfoptions.barriers import DownOutCall
    >>> s = 1
        k = 1
        r = 0.015
        Z = 0.6
        T = 2
        vol = 0.25
        q = 0.01
    >>> DownOutCall(s,k,r,Z,T,vol,q)
    0.05510635577234088

    '''
    a = 1
    b = 1

    if k > Z and s >= Z:
        price = _I1(a,b,s,k,r,Z,T,vol,q) - _I3(a,b,s,k,r,Z,T,vol,q)
    elif k <= Z and s >= Z:
        price = _I2(a,b,s,k,r,Z,T,vol,q) - _I4(a,b,s,k,r,Z,T,vol,q)
    else:
        price = 0.0
    return(max(price, 0.0))

def UpOutCallHigh(s,k,r,Z,T,vol,q):
    '''
    Calculate the Up-and-Out Call option, where barrier is greater than strike

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.)
        Spot value of underlying asset at current time, t
    k : number of any type (int, float8, float64 etc.)
        Strike value of option, determined at initiation
    r : number of any type (int, float8, float64 etc.)
        Risk free interest rate, implied constant till expiration
    Z : number of any type (int, float8, float64 etc.)
        Barrier value of option, determined at initiation
    T : number of any type (int, float8, float64 etc.)
        Time till expiration for option, can be interpreted as 'T - t' should
        the option already be initiated, and be 't' time from time = 0
    vol : number of any type (int, float8, float64 etc.)
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.)
        Continuous dividend payout, as a percentage

    * Z > k must hold true for this function

    Returns
    -------
    price : float
        Price value of barrier option.

    Examples
    --------
    >>> from qcfoptions.barriers import UpOutCallHigh
    >>> s = 1
        k = 1
        r = 0.015
        Z = 1.2
        T = 2
        vol = 0.25
        q = 0.01
    >>> UpOutCallHigh(s,k,r,Z,T,vol,q)
    0.003623404694383797

    '''
    a = 1
    b = -1

    if s <= Z:
        price = (_I1(a,b,s,k,r,Z,T,vol,q) - _I2(a,b,s,k,r,Z,T,vol,q) +
                _I3(a,b,s,k,r,Z,T,vol,q) - _I4(a,b,s,k,r,Z,T,vol,q))
    else:
        price = 0.0
    return(max(price, 0.0))

def UpOutPut(s,k,r,Z,T,vol,q):
    '''
    Calculate the Up-and-Out Put option, for any barrier

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.)
        Spot value of underlying asset at current time, t
    k : number of any type (int, float8, float64 etc.)
        Strike value of option, determined at initiation
    r : number of any type (int, float8, float64 etc.)
        Risk free interest rate, implied constant till expiration
    Z : number of any type (int, float8, float64 etc.)
        Barrier value of option, determined at initiation
    T : number of any type (int, float8, float64 etc.)
        Time till expiration for option, can be interpreted as 'T - t' should
        the option already be initiated, and be 't' time from time = 0
    vol : number of any type (int, float8, float64 etc.)
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.)
        Continuous dividend payout, as a percentage

    Returns
    -------
    price : float
        Price value of barrier option.

    Examples
    --------
    >>> from qcfoptions.barriers import UpOutPut
    >>> s = 1
        k = 1
        r = 0.015
        Z = 1.2
        T = 2
        vol = 0.25
        q = 0.01
    >>> UpOutPut(s,k,r,Z,T,vol,q)
    0.10028057349038572

    '''
    a = -1
    b = -1

    if k <= Z and s <= Z:
        price = _I1(a,b,s,k,r,Z,T,vol,q) - _I3(a,b,s,k,r,Z,T,vol,q)
    elif k > Z and s <= Z:
        price = _I2(a,b,s,k,r,Z,T,vol,q) - _I4(a,b,s,k,r,Z,T,vol,q)
    else:
        price = 0.0
    return(max(price, 0.0))

# in barriers
def DownInCall(s,k,r,Z,T,vol,q):
    '''
    Calculate the Down-and-In Call option, for any barrier

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.)
        Spot value of underlying asset at current time, t
    k : number of any type (int, float8, float64 etc.)
        Strike value of option, determined at initiation
    r : number of any type (int, float8, float64 etc.)
        Risk free interest rate, implied constant till expiration
    Z : number of any type (int, float8, float64 etc.)
        Barrier value of option, determined at initiation
    T : number of any type (int, float8, float64 etc.)
        Time till expiration for option, can be interpreted as 'T - t' should
        the option already be initiated, and be 't' time from time = 0
    vol : number of any type (int, float8, float64 etc.)
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.)
        Continuous dividend payout, as a percentage

    Returns
    -------
    price : float
        Price value of barrier option.

    Examples
    --------
    >>> from qcfoptions.barriers import DownInCall
    >>> s = 1
        k = 1
        r = 0.015
        Z = 1.2
        T = 2
        vol = 0.25
        q = 0.01
    >>> DownInCall(s,k,r,Z,T,vol,q)
    0.4299600426787612

    '''
    a = 1
    b = 1

    if k > Z:
        price = _I3(a,b,s,k,r,Z,T,vol,q)
    elif k <= Z:
        price = (_I1(a,b,s,k,r,Z,T,vol,q) - _I2(a,b,s,k,r,Z,T,vol,q) +
            _I4(a,b,s,k,r,Z,T,vol,q))
    else:
        price = 0.0
    return(max(price, 0.0))

def DownInPut(s,k,r,Z,T,vol,q):
    '''
    Calculate the Down-and-In Put option, for any barrier

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.)
        Spot value of underlying asset at current time, t
    k : number of any type (int, float8, float64 etc.)
        Strike value of option, determined at initiation
    r : number of any type (int, float8, float64 etc.)
        Risk free interest rate, implied constant till expiration
    Z : number of any type (int, float8, float64 etc.)
        Barrier value of option, determined at initiation
    T : number of any type (int, float8, float64 etc.)
        Time till expiration for option, can be interpreted as 'T - t' should
        the option already be initiated, and be 't' time from time = 0
    vol : number of any type (int, float8, float64 etc.)
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.)
        Continuous dividend payout, as a percentage

    Returns
    -------
    price : float
        Price value of barrier option.

    Examples
    --------
    >>> from qcfoptions.barriers import DownInPut
    >>> s = 1
        k = 1
        r = 0.015
        Z = 1.2
        T = 2
        vol = 0.25
        q = 0.01
    >>> DownInPut(s,k,r,Z,T,vol,q)
    0.12373904745993392

    '''
    a = -1
    b = 1

    if k > Z:
        price = (_I2(a,b,s,k,r,Z,T,vol,q) - _I3(a,b,s,k,r,Z,T,vol,q) +
            _I4(a,b,s,k,r,Z,T,vol,q))
    elif k <= Z:
        price = _I1(a,b,s,k,r,Z,T,vol,q)
    else:
        price = 0.0
    return(max(price, 0.0))

def UpInCall(s,k,r,Z,T,vol,q):
    '''
    Calculate the Up-and-In Call option, for any barrier

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.)
        Spot value of underlying asset at current time, t
    k : number of any type (int, float8, float64 etc.)
        Strike value of option, determined at initiation
    r : number of any type (int, float8, float64 etc.)
        Risk free interest rate, implied constant till expiration
    Z : number of any type (int, float8, float64 etc.)
        Barrier value of option, determined at initiation
    T : number of any type (int, float8, float64 etc.)
        Time till expiration for option, can be interpreted as 'T - t' should
        the option already be initiated, and be 't' time from time = 0
    vol : number of any type (int, float8, float64 etc.)
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.)
        Continuous dividend payout, as a percentage

    Returns
    -------
    price : float
        Price value of barrier option.

    Examples
    --------
    >>> from qcfoptions.barriers import UpInCall
    >>> s = 1
        k = 1
        r = 0.015
        Z = 1.2
        T = 2
        vol = 0.25
        q = 0.01
    >>> UpInCall(s,k,r,Z,T,vol,q)
    0.14967010921704207

    '''
    a = 1
    b = -1

    if k > Z:
        price = _I1(a,b,s,k,r,Z,T,vol,q)
    elif k <= Z:
        price = (_I2(a,b,s,k,r,Z,T,vol,q) - _I3(a,b,s,k,r,Z,T,vol,q) +
            _I4(a,b,s,k,r,Z,T,vol,q))
    else:
        price = 0.0
    return(max(price, 0.0))

def UpInPut(s,k,r,Z,T,vol,q):
    '''
    Calculate the Up-and-In Put option, for any barrier

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.)
        Spot value of underlying asset at current time, t
    k : number of any type (int, float8, float64 etc.)
        Strike value of option, determined at initiation
    r : number of any type (int, float8, float64 etc.)
        Risk free interest rate, implied constant till expiration
    Z : number of any type (int, float8, float64 etc.)
        Barrier value of option, determined at initiation
    T : number of any type (int, float8, float64 etc.)
        Time till expiration for option, can be interpreted as 'T - t' should
        the option already be initiated, and be 't' time from time = 0
    vol : number of any type (int, float8, float64 etc.)
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.)
        Continuous dividend payout, as a percentage

    Returns
    -------
    price : float
        Price value of barrier option.

    Examples
    --------
    >>> from qcfoptions.barriers import UpInCall
    >>> s = 1
        k = 1
        r = 0.015
        Z = 1.2
        T = 2
        vol = 0.25
        q = 0.01
    >>> UpInPut(s,k,r,Z,T,vol,q)
    0.0234584739695482

    '''
    a = -1
    b = -1

    if k > Z:
        price = (_I1(a,b,s,k,r,Z,T,vol,q) - _I2(a,b,s,k,r,Z,T,vol,q) +
            _I4(a,b,s,k,r,Z,T,vol,q))
    elif k <= Z:
        price = _I3(a,b,s,k,r,Z,T,vol,q)
    else:
        price = 0.0
    return(max(price, 0.0))
