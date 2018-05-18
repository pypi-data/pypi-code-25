import numpy as _np
from scipy.stats import chi2 as _chi2

_alpha = 0.01


class SNR:

    def __init__(self, X=None, E=None, df=None, s2=None, alpha=_alpha):
        "docstring"

        if X is not None:
            self.X = X

        if E is not None:
            self.E = E

        self.Sigma = _np.linalg.svd(self.X, compute_uv=False)

        if s2 is not None:
            if isinstance(s2, float) or isinstance(s2, int):
                s2 = [s2]

            self.s2 = s2

        self.alpha = alpha
        if df is None:
            df = _np.prod(X.shape)

        self._df = df

    def SNRspectra(self, s2=None, N=None):

        if s2 is None:
            s2 = self.s2[0]

        df = self._df

        chi2inv = _chi2.ppf(1 - self.alpha, df)

        SNR = []
        for S_n in self.Sigma:
            SNR.append(S_n / _np.sqrt(chi2inv * s2))

        SNR = _np.array(SNR)

        return SNR

    def scale2SNR_s2(self, SNR, n=None):

        if n is None:
            n = min(self.X.shape)

        S_n = self.Sigma[n]
        df = self._df

        chi2inv = _chi2.ppf(1 - self.alpha, df)

        s2 = S_n**2 / (chi2inv * SNR**2)

        return s2

    def SNRspectra_phi(self):

        SNR = []
        for i in self.X:
            SNR.append(_np.linalg.norm(self.X[i]) / _np.linalg.norm(self.E[i]))
