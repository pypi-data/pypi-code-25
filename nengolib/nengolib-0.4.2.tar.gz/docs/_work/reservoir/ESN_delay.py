# -*- coding: utf-8 -*-
"""
A minimalistic Echo State Networks demo with Mackey-Glass (delay 17) data
in "plain" scientific Python.
by Mantas LukoÅ¡eviÄ?ius 2012
http://minds.jacobs-university.de/mantas
"""
from numpy import *
from matplotlib.pyplot import *
import scipy.linalg

# load the data
dt = 0.0005
def make_data(dt, high=8, length=20000, delay=200):
    from nengo.processes import WhiteSignal
    data = WhiteSignal(length*dt, high=high).run_steps(length, dt=dt)
    return data #[:-delay], data[delay:]
train_x = make_data(dt)
test_x = make_data(dt)
initLen = 100  # delay


# plot some of it

# generate the ESN reservoir
inSize = outSize = 1
resSize = 1000
a = 0.3 # leaking rate

random.seed(42)
Win = (random.rand(resSize,1+inSize)-0.5) * 1
W = random.rand(resSize,resSize)-0.5
# Option 1 - direct scaling (quick&dirty, reservoir-specific):
#W *= 0.135
# Option 2 - normalizing and setting spectral radius (correct, slow):
print 'Computing spectral radius...',
rhoW = max(abs(linalg.eig(W)[0]))
print 'done.'
W *= 1.25 / rhoW

# allocated memory for the design (collected states) matrix
X = zeros((1+inSize+resSize,len(train_x) - initLen))
# set the corresponding target matrix directly
Yt = train_x[:-initLen].T  # None, initLen:]

figure(10).clear()
plot(train_x[:-initLen])
plot(train_x[initLen:])
title('A sample of data')

# run the reservoir with the data and collect X
x = zeros((resSize,1))
for t in range(len(train_x)):
    u = train_x[t]
    x = (1-a)*x + a*tanh( dot( Win, vstack((1,u)) ) + dot( W, x ) )
    if t >= initLen:
        X[:,t-initLen] = vstack((1,u,x))[:,0]

# train the output
reg = 0.01  # regularization coefficient
X_T = X.T
Wout = dot( dot(Yt,X_T), linalg.inv( dot(X,X_T) + \
    reg*eye(1+inSize+resSize) ) )
#Wout = dot( Yt, linalg.pinv(X) )

figure()
title('Training')
plot(train_x, label='Input')
plot(np.dot(Wout, X).T, label='Output')
legend()

# run the trained ESN in a generative mode. no need to initialize here,
# because x is initialized with training data and we continue from there.
Y = zeros((outSize,len(test_x)))
for t in range(len(test_x)):
    u = test_x[t]
    x = (1-a)*x + a*tanh( dot( Win, vstack((1,u)) ) + dot( W, x ) )
    y = dot( Wout, vstack((1,u,x)) )
    Y[:,t] = y
    # generative mode:
    #u = y
    ## this would be a predictive mode:
    #u = data[trainLen+t+1]

# compute MSE for the first errorLen time steps
from nengo.utils.numpy import rmse
print 'MSE = %s' % rmse(test_x[:-initLen], Y[:, initLen:].T)

# plot some signals
figure(1).clear()
plot( test_x[:-initLen], 'g' )
plot( Y[:, initLen:].T, 'b' )
title('Target and generated signals $y(n)$ starting at $n=0$')
legend(['Target signal', 'Free-running predicted signal'])

#figure(2).clear()
#plot( X[0:20,0:200].T )
#title('Some reservoir activations $\mathbf{x}(n)$')

#figure(3).clear()
#bar( range(1+inSize+resSize), Wout.T )
#title('Output weights $\mathbf{W}^{out}$')

show()
