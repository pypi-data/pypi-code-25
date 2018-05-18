import pylab
try:
    import seaborn as sns  # optional; prettier graphs
except ImportError:
    pass

import numpy as np
import nengo
import nengolib


def make_model(synapses, encoders, decoders, n_neurons, tau_derivative,
               seed, stim_seed, dt, T, stim_cutoff_freq=5, stim_rms=0.5):

    with nengolib.Network(seed=seed) as model:

        # White noise input
        stim = nengo.Node(output=nengo.processes.WhiteSignal(
            T, high=stim_cutoff_freq, rms=stim_rms, seed=stim_seed))

        # Heterogeneous synapses (one per neuron)
        x_synapses = nengo.Node(
            size_in=1, output=nengolib.HeteroSynapse(synapses, dt=dt))

        # Ensemble that encodes the signal
        x = nengo.Ensemble(n_neurons, 1, encoders=encoders)

        # Optional decoding (linear readout)
        if decoders is None:
            decoders = np.zeros((n_neurons, 1))
        y = nengo.Node(size_in=1)

        # Connections
        nengo.Connection(stim, x_synapses, synapse=None)
        nengo.Connection(x_synapses, x.neurons,
                         function=lambda x: x*encoders[:, 0], synapse=None)
        nengo.Connection(x.neurons, y, transform=decoders.T,
                         synapse=tau_derivative)

        # Probes
        p_input = nengo.Probe(stim, synapse=None)
        p_synapses = nengo.Probe(x_synapses, synapse=tau_derivative)
        p_x = nengo.Probe(x.neurons, synapse=tau_derivative)
        p_y = nengo.Probe(y, synapse=None)

        return model, (p_input, p_synapses, p_x, p_y)


# Define constants, synapses, and encoders

n_neurons = 1000
tau_derivative = 0.005

seed = 0
rng = np.random.RandomState(seed)

taus = rng.uniform(0.0005, 0.01, size=n_neurons)  # encoding filters
synapses = [nengolib.Lowpass(tau) for tau in taus]
encoders = nengolib.stats.sphere.sample(n_neurons, rng=rng)


# Show what the filter looks like
gain = 5
H = gain*nengolib.synapses.Highpass(tau_derivative)

h_size = 1000
h_dt = 0.001
freqs = np.fft.rfftfreq(h_size, d=h_dt)
desired = nengolib.signal.impulse(H, h_dt, h_size)

pylab.figure()
pylab.title("Derivative Filter (Fourier Domain)")
pylab.plot(freqs, abs(np.fft.rfft(desired)), label="Desired")
pylab.xlabel("Frequency ($Hz$)")
pylab.show()


# Training

dt = 0.0001
T = 3.0

model, (p_input, p_synapses, p_x, p_y) = make_model(
    synapses, encoders, decoders=None, n_neurons=n_neurons,
    tau_derivative=tau_derivative, seed=seed, stim_seed=0, dt=dt, T=T)
sim = nengo.Simulator(model, dt=dt)
sim.run(T, progress_bar=False)

X = sim.data[p_input]
A = sim.data[p_x]
Y = nengolib.signal.apply_filter(H, dt, X, axis=0)
decoders, info = nengo.solvers.LstsqL2()(A, Y)  # AD = Y
Y_hat = np.dot(A, decoders)

gamma = np.dot(A.T, A)
U, S, V = np.linalg.svd(gamma)
chi = np.dot(A, U)
pylab.figure(figsize=(12, 7))
pylab.title("SVD of Gamma Matrix")
pylab.plot(sim.trange(), X, label="Input")
for i in range(3):
    pylab.plot(sim.trange(), chi[:, i] / len(chi), label=r"$\chi_%d$" % i)
pylab.legend(loc='best')
pylab.show()


def plot_signals(X, Y, Y_hat):
    pylab.figure(figsize=(12, 7))
    pylab.title("Derivative of Signal (RMSE: %.3f)" % (
        nengo.utils.numpy.rmse(Y, Y_hat)))
    pylab.plot(sim.trange(), X, label="Input")
    pylab.plot(sim.trange(), Y, label="Ideal")
    pylab.plot(sim.trange(), Y_hat, label="Approximation")
    pylab.legend(loc='best')
    pylab.xlabel("Time ($s$)")
    pylab.ylim(-1, 1)
    pylab.show()

plot_signals(X, Y, Y_hat)


# Validation on test signal

model, (p_input, p_synapses, p_x, p_y) = make_model(
    synapses, encoders, decoders=decoders, n_neurons=n_neurons,
    tau_derivative=tau_derivative, seed=seed, stim_seed=4, dt=dt, T=T)
sim = nengo.Simulator(model, dt=dt)
sim.run(T, progress_bar=False)

plot_signals(sim.data[p_input],
             nengolib.signal.apply_filter(H, dt, sim.data[p_input], axis=0),
             sim.data[p_y])


# Experiment for increasing heterogeneity

num_samples = 5
plot_x = []
plot_y = []
T = 1

for width in np.linspace(0, 0.03, num_samples):
    L, U = 0.0005, 0.0005 + width

    rng = np.random.RandomState(seed)
    taus = rng.uniform(L, U, size=n_neurons)
    synapses = [nengolib.Lowpass(tau) for tau in taus]

    model, (p_input, p_synapses, p_x, p_y) = make_model(
        synapses, encoders, decoders=None, n_neurons=n_neurons,
        tau_derivative=tau_derivative, seed=seed, stim_seed=0, dt=dt, T=T)
    sim = nengo.Simulator(model, dt=dt)
    sim.run(T, progress_bar=False)

    X = sim.data[p_input]
    A = sim.data[p_x]
    Y = nengolib.signal.apply_filter(H, dt, X, axis=0)
    decoders, info = nengo.solvers.LstsqL2()(A, Y)
    Y_hat = np.dot(A, decoders)

    plot_x.append(width)
    plot_y.append(nengo.utils.numpy.rmse(Y, Y_hat))


def fit(x, a, b, c, d, e):
    return a*np.exp(-b*x) + c*np.exp(-d*x) + e

from scipy.optimize import curve_fit
popt, pcov = curve_fit(
    fit, plot_x, plot_y, bounds=(0, [1., 10000., 1., 10000., 1.]))

pylab.figure()
pylab.title("Effect of Increasing Heterogeneity")
pylab.plot(plot_x, plot_y)
pylab.plot(plot_x, fit(np.asarray(plot_x), *popt), color='green',
           linewidth=1, alpha=0.8)
pylab.xlabel(r"$\tau$ width ($ms$)")
pylab.ylabel("RMSE")
pylab.show()
