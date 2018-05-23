# Austin Griffith
# Options, Black Scholes

import numpy as np
from scipy.stats import norm

# options
def Euro(s,k,r,T,vol,q):
    '''
    Calculate the Black Scholes value of a European Call / Put option
    Payoffs are of the form :
    C = max(S - K, 0)
    P = max(K - S, 0)

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying s
        Spot value of underlying asset at current time, t
    k : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying k
        Strike value of option, determined at initiation
    r : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying r
        Risk free interest rate, implied constant till expiration
    T : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying T
        Time till expiration for option
    vol : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying vol
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying q
        Continuous dividend payout, as a percentage

    All parameters can be individual values.
    Only one of these parameters can be a numpy.array, otherwise there will be
    a dimension mismatch.

    Returns
    -------
    [call,put] : list of pair of float or numpy.array values
        European call and put values, type depends on input value.
        If all input values are individual numbers, then output will be float.
        If one input value is numpy.array, then output will be numpy.array.

    Examples
    --------
    >>> from qcfoptions.bsoptions import Euro
    >>> s = 1
        k = 1
        r = 0.015
        T = 2
        vol = 0.25
        q = 0.01
    >>> Euro(s,k,r,T,vol,q)
    [0.14178423526329242, 0.13203109550504533]
    >>> import numpy as np
    >>> s_array = np.array([0.5,1.0,1.5,2.0])
    >>> Euro(s_array,k,r,T,vol,q)
    [array([0.00244785, 0.14178424, 0.52452167, 0.99416626]),
    array([0.48279404, 0.1320311 , 0.0246692 , 0.00421444])]

    '''
    d1 = ((np.log(s/k) + (r - q + 0.5*vol*vol)*T)) / (vol*np.sqrt(T))
    d2 = d1 - vol*np.sqrt(T)

    option = np.exp(-q*T)*s
    strike = np.exp(-r*T)*k

    put = strike*norm.cdf(-d2) - option*norm.cdf(-d1)
    call = option*norm.cdf(d1) - strike*norm.cdf(d2)
    return([call,put])

def AsianGeometric(s,k,r,T,vol,q):
    '''
    Calculate the Black Scholes value of Geometric Average Asian Call / Put
    option with a fixed strike
    Payoffs are of the form :
    C = max(AVG_geo - K, 0)
    P = max(K - AVG_geo, 0)

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying s
        Spot value of underlying asset at current time, t
    k : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying k
        Strike value of option, determined at initiation
    r : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying r
        Risk free interest rate, implied constant till expiration
    T : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying T
        Time till expiration for option
    vol : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying vol
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying q
        Continuous dividend payout, as a percentage

    All parameters can be individual values.
    Only one of these parameters can be a numpy.array, otherwise there will be
    a dimension mismatch.

    Returns
    -------
    [call,put] : list of pair of float or numpy.array values
        Asian call and put values, type depends on input value.
        If all input values are individual numbers, then output will be float.
        If one input value is numpy.array, then output will be numpy.array.

    Examples
    --------
    >>> from qcfoptions.bsoptions import AsianGeometric
    >>> s = 1
        k = 1
        r = 0.015
        T = 2
        vol = 0.25
        q = 0.01
    >>> AsianGeometric(s,k,r,T,vol,q)
    [0.0760833709740742, 0.08132574004684912]
    >>> import numpy as np
    >>> s_array = np.array([0.5,1.0,1.5,2.0])
    >>> AsianGeometric(s_array,k,r,T,vol,q)
    [array([1.10488795e-05, 7.60833710e-02, 4.79636239e-01, 9.59987952e-01]),
    array([4.87855000e-01, 8.13257400e-02, 2.27702612e-03, 2.71568147e-05])]

    '''
    a = 0.5*(r - q - vol*vol/6)
    volG = vol/np.sqrt(3)

    d1 = (np.log(s/k) + (a + 0.5*volG*volG)*T) / (volG*np.sqrt(T))
    d2 = d1 - volG*np.sqrt(T)

    option = s*np.exp((a - r)*T)
    strike = k*np.exp(-r*T)

    put = strike*norm.cdf(-d2) - option*norm.cdf(-d1)
    call = option*norm.cdf(d1) - strike*norm.cdf(d2)
    return([call,put])

def AsianArithmetic(s,k,r,T,vol,q):
    '''
    Calculate the Black Scholes value of Arithmetic Average Asian Call / Put
    option with a fixed strike
    Payoffs are of the form :
    C = max(AVG_arithmetic - K, 0)
    P = max(K - AVG_arithmetic, 0)

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying s
        Spot value of underlying asset at current time, t
    k : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying k
        Strike value of option, determined at initiation
    r : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying r
        Risk free interest rate, implied constant till expiration
    T : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying T
        Time till expiration for option
    vol : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying vol
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying q
        Continuous dividend payout, as a percentage

    All parameters can be individual values.
    Only one of these parameters can be a numpy.array, otherwise there will be
    a dimension mismatch.

    * r > q, else the natural logarithm will break due to a relationship
        mismatch

    Returns
    -------
    [call,put] : list of pair of float or numpy.array values
        Asian call and put values, type depends on input value.
        If all input values are individual numbers, then output will be float.
        If one input value is numpy.array, then output will be numpy.array.

    Examples
    --------
    >>> from qcfoptions.bsoptions import AsianArithmetic
    >>> s = 1
        k = 1
        r = 0.01
        T = 2
        vol = 0.25
        q = 0.015
    >>> AsianArithmetic(s,k,r,T,vol,q)
    [0.8242269391820242, 0.8193584969058301]
    >>> import numpy as np
    >>> s_array = np.array([0.5,1.0,1.5,2.0])
    >>> AsianArithmetic(s_array,k,r,T,vol,q)
    [array([0.38280732, 0.82422694, 1.27915927, 1.7410437 ]),
    array([0.86559587, 0.8193585 , 0.78663384, 0.76086128])]

    '''
    m1 = s*(np.exp((r - q)*T) - 1) / ((r - q)*T)
    m2l = 2*s*s*np.exp((2*r - 2*q + vol*vol)*T) / ((r - q +vol*vol)*T*T*(2*r - 2*q + vol*vol))
    m2r = (2*s*s / ((r-q)*T*T))*((1/(2*(r-q) + vol*vol)) -
        np.exp((r-q)*T)/(r - q - vol*vol))
    m2 = m2l + m2r

    volA = np.sqrt(np.log(m2/(m1*m1)) / T)

    d1 = (np.log(m1/k) + 0.5*volA*volA*T) / (volA*np.sqrt(T))
    d2 = d1 - volA*np.sqrt(T)

    call = np.exp(-r*T)*(m1*norm.cdf(d1) - k*norm.cdf(d2))
    put = np.exp(-r*T)*(k*norm.cdf(-d2) - m1*norm.cdf(-d1))
    return([call,put])

def Power(s,k,r,T,vol,q,n):
    '''
    Calculate the Black Scholes value of a traditional Power Call / Put option
    with a fixed strike
    Payoffs are of the form :
    C = max(S**n - K, 0)
    P = max(K - S**n, 0)

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying s
        Spot value of underlying asset at current time, t
    k : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying k
        Strike value of option, determined at initiation
    r : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying r
        Risk free interest rate, implied constant till expiration
    T : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying T
        Time till expiration for option
    vol : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying vol
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying q
        Continuous dividend payout, as a percentage
    n : number of any type (int, float8, float64 etc.)
        Power to which the underlying spot is raised at payoff

    All parameters can be individual values.
    Only one of these parameters can be a numpy.array (not including 'n'),
    otherwise there will be a dimension mismatch.

    Returns
    -------
    [call,put] : list of pair of float or numpy.array values
        Power call and put values, type depends on input value.
        If all input values are individual numbers, then output will be float.
        If one input value, other than 'n', is numpy.array, then output
        will be numpy.array.

    Examples
    --------
    >>> from qcfoptions.bsoptions import Power
    >>> s = 1
        k = 1
        r = 0.01
        T = 2
        vol = 0.25
        q = 0.015
        n = 2.5
    >>> Power(s,k,r,T,vol,q,n)
    [0.5888398346686554, 0.2369822536424761]
    >>> import numpy as np
    >>> s_array = np.array([0.5,1.0,1.5,2.0])
    >>> Power(s_array,k,r,T,vol,q,n)
    [array([0.00881893, 0.58883983, 2.7187886 , 6.51733355]),
    array([0.74551209, 0.23698225, 0.04539523, 0.00770309])]

    '''
    d1 = (np.log(s/np.power(k,1/n)) +
        (r - q + vol*vol*(n - 0.5))*T) / (vol*np.sqrt(T))
    d2 = d1 - n*vol*np.sqrt(T)

    option = np.exp(T*(n-1)*(r + 0.5*n*vol*vol))*np.power(s,n)
    strike = k*np.exp(-r*T)

    put = strike*norm.cdf(-d2) - option*norm.cdf(-d1)
    call = option*norm.cdf(d1) - strike*norm.cdf(d2)
    return([call,put])

def PowerStrike(s,k,r,T,vol,q,n):
    '''
    Calculate the Black Scholes value of Power Call / Put option with a
    fixed strike to the power n
    Payoffs are of the form :
    C = max(S**n - K**n, 0)
    P = max(K**n - S**n, 0)

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying s
        Spot value of underlying asset at current time, t
    k : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying k
        Strike value of option, determined at initiation
    r : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying r
        Risk free interest rate, implied constant till expiration
    T : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying T
        Time till expiration for option
    vol : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying vol
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying q
        Continuous dividend payout, as a percentage
    n : number of any type (int, float8, float64 etc.)
        Power to which the underlying spot is raised at payoff

    All parameters can be individual values.
    Only one of these parameters can be a numpy.array (not including 'n'),
    otherwise there will be a dimension mismatch.

    Returns
    -------
    [call,put] : list of pair of float or numpy.array values
        Power call and put values, type depends on input value.
        If all input values are individual numbers, then output will be float.
        If one input value, other than 'n', is numpy.array, then output
        will be numpy.array.

    Examples
    --------
    >>> from qcfoptions.bsoptions import PowerStrike
    >>> s = 1
        k = 1
        r = 0.01
        T = 2
        vol = 0.25
        q = 0.015
        n = 2.5
    >>> PowerStrike(s,k,r,T,vol,q,n)
    [0.5888398346686554, 0.2369822536424761]
    >>> import numpy as np
    >>> s_array = np.array([0.5,1.0,1.5,2.0])
    >>> PowerStrike(s_array,k,r,T,vol,q,n)
    [array([0.00881893, 0.58883983, 2.7187886 , 6.51733355]),
    array([0.74551209, 0.23698225, 0.04539523, 0.00770309])]

    '''
    d1 = (np.log(s/np.power(k,1/n)) +
        (r - q + vol*vol*(n - 0.5))*T) / (vol*np.sqrt(T))
    d2 = d1 - n*vol*np.sqrt(T)

    option = np.exp(T*(n-1)*(r + 0.5*n*vol*vol))*np.power(s,n)
    strike = np.power(k,n)*np.exp(-r*T)

    put = strike*norm.cdf(-d2) - option*norm.cdf(-d1)
    call = option*norm.cdf(d1) - strike*norm.cdf(d2)
    return([call,put])

def Margrabe(s,s2,T,vol,vol2,q,q2,corr):
    '''
    Calculate the Black Scholes value of the Margrabe Option
    Payoff is of the form :
    O = max(S_1 - S_2, 0)

    Parameters
    ----------
    s1 and s2 : number of any type (int, float8, float64 etc.), numpy array of
        any type should the user wish to have a list of values output with
        varying s
        Spot value of underlying assets 1 and 2 at current time, t
    T : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying T
        Time till expiration for option
    vol1 and vol2 : number of any type (int, float8, float64 etc.), numpy array
        of any type should the user wish to have a list of values output with
        varying vol
        Volatility of underlying for assets 1 and 2, implied constant till
        expiration in Black Scholes model
    q1 and q2 : number of any type (int, float8, float64 etc.), numpy array of
        any type should the user wish to have a list of values output with
        varying q
        Continuous dividend payout for assets 1 and 2, as a percentage
    corr : number of any type (int, float8, float64 etc.), numpy array of any
        type should the user wish to have a list of values output with varying
        corr
        Correlation between the motion of the underlying (relationship between
        the Weiner process of asset 1 and 2)

    All parameters can be individual values.
    At most, only one pair of these parameters can be a numpy.array,
    otherwise there will be a dimension mismatch.

    Returns
    -------
    price : float or numpy.array value
        Margrabe price, type depends on input value.
        If all input values are individual numbers, then output will be float.
        If one pair of input values are a numpy.array,
        then output will be numpy.array.

    Examples
    --------
    >>> from qcfoptions.bsoptions import Margrabe
    >>> s1 = 1
        s2 = 1.2
        T = 2
        q1 = 0.1
        q2 = 0.05
        vol1 = 0.25
        vol2 = 0.15
        corr = 0.4
    >>> Margrabe(s1,s2,T,vol1,vol2,q1,q2,corr)
    0.0454498263366398
    >>> import numpy as np
    >>> s1_array = np.array([0.5,1.0,1.5,2.0])
        s2_array = np.array([0.5,1.0,1.5,2.0])
    >>> Margrabe(s1_array,s2_array,T,vol1,vol2,q1,q2,corr)
    array([0.04466118, 0.08932237, 0.13398355, 0.17864473])

    '''
    volMix = np.sqrt(vol*vol + vol2*vol2 - vol*vol2*corr)
    d1 = (np.log(s/s2) + (q2 - q + 0.5*(volMix**2))*T) / (volMix*np.sqrt(T))
    d2 = d1 - volMix*np.sqrt(T)

    option = np.exp(-q*T)*s*norm.cdf(d1)
    option2 = np.exp(-q2*T)*s2*norm.cdf(d2)

    price = option - option2
    return(price)

def Lookback(s,M,r,T,vol,q):
    '''
    Calculate the Black Scholes value of floating strike
    Lookback Call / Put option
    Payoffs are of the form :
    C = S_T - min(m,m_T)
    P = max(M,M_T) - S_T
    where 'm' is the current minimum, or starting strike at initiation, and
    'm_T' is the minimum over the remaining life of the option
    similarly, 'M' is the current maximum, or starting strike at initiation, and
    'M_T' is the maximum over the remaining life of the option

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying s
        Spot value of underlying asset at current time, t
    M : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying k
        Strike value of option, determined by minimum value of underlying
        over the life of the option
    r : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying r
        Risk free interest rate, implied constant till expiration
    T : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying T
        Time till expiration for option
    vol : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying vol
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying q
        Continuous dividend payout, as a percentage

    All parameters can be individual values.
    Only one of these parameters can be a numpy.array, otherwise there will be
    a dimension mismatch.

    Returns
    -------
    [call,put] : list of pair of float or numpy.array values
        Lookback call and put values, type depends on input value.
        If all input values are individual numbers, then output will be float.
        If one input value is numpy.array, then output will be numpy.array.

    Examples
    --------
    >>> from qcfoptions.bsoptions import Lookback
    >>> s = 1
        k = 1
        r = 0.015
        T = 2
        vol = 0.25
        q = 0.01
    >>> Lookback(s,M,r,T,vol,q)
    [0.2509969952730551, 0.30220097900385257]
    >>> import numpy as np
    >>> s_array = np.array([0.5,1.0,1.5,2.0])
    >>> Lookback(s_array,M,r,T,vol,q)
    [array([0.33036841, 0.250997  , 0.54619226, 0.99797004]),
    array([0.48550323, 0.30220098, 0.70926038, 1.40333811])]

    '''
    B = 2*(r - q) / (vol*vol)
    x = (np.log(s/M) + (r - q - 0.5*vol*vol)*T) / (vol*np.sqrt(T))
    y = (-np.log(s/M) - (r - q + 0.5*vol*vol)*T) / (vol*np.sqrt(T))

    option = s*np.exp(-q*T)
    minimum = M*np.exp(-r*T)
    left = np.exp(-r*T)*np.power(s/M,-B)
    right = np.exp(-q*T)

    call = (option*norm.cdf(x + vol*np.sqrt(T)) -
        minimum*norm.cdf(x) +
        (s/B)*(left*norm.cdf(y + B*vol*np.sqrt(T)) -
            right*norm.cdf(y)))
    put = (-option*norm.cdf(-x - vol*np.sqrt(T)) +
        minimum*norm.cdf(-x) -
        (s/B)*(left*norm.cdf(-y - B*vol*np.sqrt(T)) -
            right*norm.cdf(-y)))
    return([call,put])

# greeks
def EuroDelta(s,k,r,T,vol,q):
    '''
    Calculate the Black Scholes delta value of a European Call / Put option,
    measures sensitivity of option value with respect to change in underlying
    asset price, calculated from derivative dV/dS
    Deltas are of the form :
    C = e**-qT N(d1)
    P = -e**-qT N(-d1)

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying s
        Spot value of underlying asset at current time, t
    k : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying k
        Strike value of option, determined at initiation
    r : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying r
        Risk free interest rate, implied constant till expiration
    T : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying T
        Time till expiration for option
    vol : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying vol
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying q
        Continuous dividend payout, as a percentage

    All parameters can be individual values.
    Only one of these parameters can be a numpy.array, otherwise there will be
    a dimension mismatch.

    Returns
    -------
    [call,put] : list of pair of float or numpy.array values
        European call and put delta values, type depends on input value.
        If all input values are individual numbers, then output will be float.
        If one input value is numpy.array, then output will be numpy.array.

    Examples
    --------
    >>> from qcfoptions.bsoptions import EuroDelta
    >>> s = 1
        k = 1
        r = 0.015
        T = 2
        vol = 0.25
        q = 0.01
    >>> EuroDelta(s,k,r,T,vol,q)
    [0.56972847508580482, 0.41047019822095043]
    >>> import numpy as np
    >>> s_array = np.array([0.5,1.0,1.5,2.0])
    >>> EuroDelta(s_array,k,r,T,vol,q)
    [array([ 0.03880678,  0.56972848,  0.89373992,  0.96532734]),
    array([-0.94139189, -0.4104702 , -0.08645875, -0.01487133])]

    '''
    d1 = ((np.log(s/k) + (r - q + 0.5*vol*vol)*T)) / (vol*np.sqrt(T))

    call = np.exp(-q*T)*norm.cdf(d1)
    put = -np.exp(-q*T)*norm.cdf(-d1)
    return([call,put])

def EuroGamma(s,k,r,T,vol,q):
    '''
    Calculate the Black Scholes gamma value of a European Call / Put option,
    measures sensitivity of option delta with respect to change in underlying
    asset price, calculated from derivative d2C/dS2
    Gamma is of the form :
    G = e**(-qT) N'(d1) / S vol sqrt(T)

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying s
        Spot value of underlying asset at current time, t
    k : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying k
        Strike value of option, determined at initiation
    r : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying r
        Risk free interest rate, implied constant till expiration
    T : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying T
        Time till expiration for option
    vol : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying vol
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying q
        Continuous dividend payout, as a percentage

    All parameters can be individual values.
    Only one of these parameters can be a numpy.array, otherwise there will be
    a dimension mismatch.

    Returns
    -------
    gamma : float or numpy.array value
        European gamma value, type depends on input value.
        If all input values are individual numbers, then output will be float.
        If one input value is numpy.array, then output will be numpy.array.

    Examples
    --------
    >>> from qcfoptions.bsoptions import EuroGamma
    >>> s = 1
        k = 1
        r = 0.015
        T = 2
        vol = 0.25
        q = 0.01
    >>> EuroGamma(s,k,r,T,vol,q)
    1.08302411826
    >>> import numpy as np
    >>> s_array = np.array([0.5,1.0,1.5,2.0])
    >>> EuroGamma(s_array,k,r,T,vol,q)
    array([ 0.47384156,  1.08302412,  0.29567765,  0.05301251])

    '''
    d1 = ((np.log(s/k) + (r - q + 0.5*vol*vol)*T)) / (vol*np.sqrt(T))
    gamma = np.exp(-q*T)*norm.pdf(d1) / (s*vol*np.sqrt(T))
    return(gamma)

def EuroVega(s,k,r,T,vol,q):
    '''
    Calculate the Black Scholes vega value of a European Call / Put option,
    measures sensitivity of option value with respect to change in underlying
    asset volatility, calculated from derivative dV/dσ
    Vega is of the form :
    V = S e**(-qT) N'(d1) sqrt(T)

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying s
        Spot value of underlying asset at current time, t
    k : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying k
        Strike value of option, determined at initiation
    r : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying r
        Risk free interest rate, implied constant till expiration
    T : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying T
        Time till expiration for option
    vol : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying vol
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying q
        Continuous dividend payout, as a percentage

    All parameters can be individual values.
    Only one of these parameters can be a numpy.array, otherwise there will be
    a dimension mismatch.

    Returns
    -------
    vega : float or numpy.array value
        European vega value, type depends on input value.
        If all input values are individual numbers, then output will be float.
        If one input value is numpy.array, then output will be numpy.array.

    Examples
    --------
    >>> from qcfoptions.bsoptions import EuroVega
    >>> s = 1
        k = 1
        r = 0.015
        T = 2
        vol = 0.25
        q = 0.01
    >>> EuroVega(s,k,r,T,vol,q)
    0.541512059132
    >>> import numpy as np
    >>> s_array = np.array([0.5,1.0,1.5,2.0])
    >>> EuroVega(s_array,k,r,T,vol,q)
    array([ 0.0592302 ,  0.54151206,  0.33263735,  0.10602502])

    '''
    d1 = ((np.log(s/k) + (r - q + 0.5*vol*vol)*T)) / (vol*np.sqrt(T))
    vega = s*np.exp(-q*T)*norm.pdf(d1)*np.sqrt(T)
    return(vega)

def EuroTheta(s,k,r,T,vol,q):
    '''
    Calculate the Black Scholes theta value of a European Call / Put option,
    measures sensitivity of option value with respect to change in time,
    calculated from derivative dV/dT

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying s
        Spot value of underlying asset at current time, t
    k : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying k
        Strike value of option, determined at initiation
    r : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying r
        Risk free interest rate, implied constant till expiration
    T : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying T
        Time till expiration for option
    vol : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying vol
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying q
        Continuous dividend payout, as a percentage

    All parameters can be individual values.
    Only one of these parameters can be a numpy.array, otherwise there will be
    a dimension mismatch.

    Returns
    -------
    [call,put] : list of pair of float or numpy.array values
        European call and put theta values, type depends on input value.
        If all input values are individual numbers, then output will be float.
        If one input value is numpy.array, then output will be numpy.array.

    Examples
    --------
    >>> from qcfoptions.bsoptions import EuroTheta
    >>> s = 1
        k = 1
        r = 0.015
        T = 2
        vol = 0.25
        q = 0.01
    >>> EuroTheta(s,k,r,T,vol,q)
    [-0.034566382542201617, -0.029811686272041546]
    >>> import numpy as np
    >>> s_array = np.array([0.5,1.0,1.5,2.0])
    >>> EuroTheta(s_array,k,r,T,vol,q)
    [array([-0.00376219, -0.03456638, -0.01962506, -0.00136734]),
    array([ 0.0058935 , -0.02981169, -0.01977136, -0.00641463])]

    '''
    d1 = ((np.log(s/k) + (r - q + 0.5*vol*vol)*T)) / (vol*np.sqrt(T))
    d2 = d1 - vol*np.sqrt(T)

    deriv = -0.5*np.exp(-q*T)*norm.pdf(d1)*s*vol / np.sqrt(T)
    strike = r*k*np.exp(-r*T)
    option = q*s*np.exp(-q*T)

    call = deriv - strike*norm.cdf(d2) + option*norm.cdf(d1)
    put = deriv + strike*norm.cdf(-d2) - option*norm.cdf(-d1)
    return([call,put])

def EuroRho(s,k,r,T,vol,q):
    '''
    Calculate the Black Scholes rho value of a European Call / Put option,
    measures sensitivity of option value with respect to change in interest
    rate over the life of the option, calculated from derivative dV/dr

    Rhos are of the form :
    C = e**-rT K T N(d2)
    P = -e**-rT K T N(-d2)

    Parameters
    ----------
    s : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying s
        Spot value of underlying asset at current time, t
    k : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying k
        Strike value of option, determined at initiation
    r : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying r
        Risk free interest rate, implied constant till expiration
    T : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying T
        Time till expiration for option
    vol : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying vol
        Volatility of underlying, implied constant till expiration in Black
        Scholes model
    q : number of any type (int, float8, float64 etc.), numpy array of any type
        should the user wish to have a list of values output with varying q
        Continuous dividend payout, as a percentage

    All parameters can be individual values.
    Only one of these parameters can be a numpy.array, otherwise there will be
    a dimension mismatch.

    Returns
    -------
    [call,put] : list of pair of float or numpy.array values
        European call and put rho values, type depends on input value.
        If all input values are individual numbers, then output will be float.
        If one input value is numpy.array, then output will be numpy.array.

    Examples
    --------
    >>> from qcfoptions.bsoptions import EuroRho
    >>> s = 1
        k = 1
        r = 0.015
        T = 2
        vol = 0.25
        q = 0.01
    >>> EuroRho(s,k,r,T,vol,q)
    [0.85588847964502479, -1.0850025874519915]
    >>> import numpy as np
    >>> s_array = np.array([0.5,1.0,1.5,2.0])
    >>> EuroRho(s_array,k,r,T,vol,q)
    [array([ 0.03391108,  0.85588848,  1.63217641,  1.87297685]),
    array([-1.90697998, -1.08500259, -0.30871465, -0.06791421])]

    '''
    d1 = ((np.log(s/k) + (r - q + 0.5*vol*vol)*T)) / (vol*np.sqrt(T))
    d2 = d1 - vol*np.sqrt(T)

    strike = k*T*np.exp(-r*T)

    call = strike*norm.cdf(d2)
    put = -strike*norm.cdf(-d2)
    return([call,put])
