from abc import ABC, abstractmethod
import numpy as np
from scipy.stats import norm


class Equity():

    def __init__(self, price, r, vol):
        self.price = price
        self.r = r
        self.vol = vol

    def get_price(self):
        return self.price

    def set_price(self, price):
        self.price = price

    def get_r(self):
        return self.r

    def set_r(self, r):
        self.r = r

    def get_vol(self):
        return self.vol

    def set_vol(self, vol):
        self.vol = vol

    def next_simulated_price(self, dt):
        """
        Using formula and standard Gaussian to calculate a next simulated
        price, the price will be returned and the equity's price will be
        updated as well.

        Args:
            dt (float): The time param that will be used to calculated sigma

        Returns:
            float: The next simulated price.
        """
        sigma = self.vol * np.sqrt(dt)
        mu = self.r * dt - sigma ** 2 / 2
        next_price = self.get_price() \
            * np.exp(mu + sigma * np.random.normal(0, 1))

        self.set_price(next_price)
        return self.get_price()


class Option(ABC):

    def __init__(self, K, T, r, sigma):
        self.K = K
        self.T = T
        self.sigma = sigma
        self.r = r

    @abstractmethod
    def get_exercise_value(self, s, t, *args):
        pass


class EuropeanOption(Option):
    pass


class EuropeanCall(EuropeanOption):

    def get_exercise_value(self, s, t, *args):
        """
        Given spot price and time to maturity, return the european call's
        exercise value. Europeanoptions can only be exercised at maturity

        Args:
            s (float): Current spot price
            t (float): Time to maturity

        Returns:
            float:  Exercise value of european call
        """

        if (t < self.T):
            return 0
        else:
            if (s - self.K > 0):
                return s - self.K
            else:
                return 0

    def get_black_scholes_value(self, s):
        """
        Using Black-Scholes Formula to calculate the value of a Euro Call
        option

        Args:
            s (float): Current spot price

        Returns:
            float: The expected call option price based on BS formula
        """
        d1 = 1 / (self.sigma * np.sqrt(self.T)) \
            * (np.log(s / self.K) + (self.r + self.sigma ** 2 / 2) * self.T)
        d2 = d1 - self.sigma * np.sqrt(self.T)
        return norm.cdf(d1) * s \
            - norm.cdf(d2) * self.K * np.exp(-self.r * self.T)


class EuropeanPut(EuropeanOption):

    def get_exercise_value(self, s, t, *args):
        """
        Given spot price and time to maturity, return the european put's
        exercise value. Europeanoptions can only be exercised at maturity

        Args:
            s (float): Current spot price
            t (float): Time to maturity

        Returns:
            float:  Exercise value of european put
        """

        if (t < self.T):
            return 0
        else:
            if (self.K - s > 0):
                return self.K - s
            else:
                return 0

    def get_black_scholes_value(self, s):
        """
        Using Black-Scholes Formula to calculate the value of a Euro Put
        option

        Args:
            s (float): Current spot price

        Returns:
            float: The expected put option price based on BS formula
        """
        d1 = 1 / (self.sigma * np.sqrt(self.T)) \
            * (np.log(s / self.K) + (self.r + self.sigma ** 2 / 2) * self.T)
        d2 = d1 - self.sigma * np.sqrt(self.T)
        return norm.cdf(-d2) * self.K * np.exp(-self.r * self.T) \
            - norm.cdf(-d1) * s


class AmericanOption(Option):
    pass


class AmericanCall(AmericanOption):

    def get_exercise_value(self, s, t, *args):
        """
        Given spot price and time to maturity, return the american call's
        instrinct value

        Args:
            s (float): Current spot price
            t (float): Time to maturity

        Returns:
            float:  Exercise value of american call
        """

        if s - self.K > 0:
            return s - self.K
        else:
            return 0


class AmericanPut(AmericanOption):

    def get_exercise_value(self, s, t, *args):
        """
        Given spot price and time to maturity, return the american put's
        instrinct value

        Args:
            s (float): Current spot price
            t (float): Time to maturity

        Returns:
            float:  Exercise value of american put
        """

        if self.K - s > 0:
            return self.K - s
        else:
            return 0
