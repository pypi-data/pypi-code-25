import numpy as np


class BinomTree():

    def __init__(self, n, T, equity, keep_s=False, keep_p=False):
        """
        Given the current stock price and the depth, return the value of the
        option using a binomial tree method.

        Use a single list to record each layer's stock prices. In
        this way, we can use the entire paths of stock prices for some
        complicated option pricing. Whether to use this feature depends on your
        own option design. There is a trade-off between memory and real-time
        calculation expenditures.

        Args:
            n (int): The depth of the binomial tree.
            T (float): The time assigned for this tree.
            equity (Equity): An equity with given interest rate and volatility.
            keep_s (bool, Optional): Default to False. If this is selected
                as True, then all the paths of changing stock prices will be
                calculated and passed to Option's exercise price calculation
                method. It's useful for some options that will adjust its
                prices based on historical or expected future underlying
                payoffs.
            keep_p (bool, Optional): Defaut to False. If this is selected
                as True, then all the paths of calculated payoffs will be
                stored seperately for the future uses.

        Return:
            float: The price returned by the given binomial tree model.
        """
        self.n = n
        self.T = T
        self.dt = T / n

        self.s = equity.get_price()
        self.r = equity.get_r()
        self.sigma = equity.get_vol()

        # Up and down for the equity payoffs
        self.u = np.exp(self.sigma * np.sqrt(self.dt))
        self.d = 1 / self.u

        # Risk neutral probability
        self.q = (np.exp(self.r * self.dt) - self.d) / (self.u - self.d)

        # A list of equity prices for each node, default not to store it and
        # will calculate them dynamically during pricing.
        self.st = []
        if keep_s:
            for layer in range(n + 1):
                for i in reversed(range(layer + 1)):
                    self.st.append(self.s * self.u ** (2 * i - layer))
        if keep_p:
            self.payoffs = {}
        else:
            self.payoffs = None

    def price(self, option, *args):
        """
        Given an option, use the current binomial model to fit its price based
        on its own excerice pricing formula.

        Args:
            option (Option): An Option object as defined.

        Returns:
            float: the fair price approximated based on Binomial Tree.
        """

        nodes = []

        for i in reversed(range(self.n + 1)):
            spot = self.s * self.u ** (2 * i - self.n)
            nodes.append(option.get_exercise_value(spot, self.T, *args))

        t = self.T

        for j in reversed(range(self.n)):
            t = t - self.dt
            if self.payoffs is not None:
                self.payoffs[j] = []
            for i in reversed(range(j + 1)):
                spot = self.s * self.u ** (2 * i - j)
                exercise = option.get_exercise_value(spot, t, *args)
                nodes[j - i] = np.exp(-self.r * self.dt) \
                    * (self.q * nodes[j - i] + (1 - self.q) * nodes[j - i + 1])

                # Check for early exercise
                if nodes[j - i] < exercise:
                    nodes[j - i] = exercise

                if self.payoffs is not None:
                    self.payoffs[j].append(nodes[j - i])

        return nodes[0]
