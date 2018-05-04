from __future__ import division, print_function

import numpy as np
import matplotlib.pyplot as plt

def posterior(fitresult,plot_likelihood=False):
    '''
    Plot the posterior probablity/likelihood from the given FitResult object.
    '''

    #The fit parameters and the inverse covariance matrix
    p0 = fitresult.p
    cov = fitresult.cov
    invcov = np.linalg.inv(fitresult.cov)

    #A single parameter
    if p0.size == 1:
        x = np.linspace(p0[0]-5*np.sqrt(cov[0,0]),p0[0]+5*np.sqrt(cov[0,0]),150)

        #L might not be vectorized in terms of p, so will calculate the values
        #separately for compatibility
        L = np.zeros(x.shape)

        for i in range(L.size):
            L[i] = fitresult.L([x[i]])

        #Normalize L
        L = L-np.max(L)

        if plot_likelihood:
            plt.plot(x,L,label='Likelihood')
            plt.plot(x,-0.5*(x-p0[0])**2/cov[0,0],label='Gaussian approximation')
            plt.ylabel('$L(p_1|data)$')

        else:
            #Compute probablity
            p = np.exp(L)

            #Normalize
            p = p/np.trapz(p,x)

            plt.plot(x,p,label='Probability')
            plt.plot(x,np.exp(-0.5*(x-p0)**2*invcov[0,0])/np.sqrt(2*np.pi*cov[0,0]),label='Gaussian approximation')
            plt.ylabel('$p(p_1|data)$')

        plt.xlabel('$p_1$')

        plt.legend()

    elif p0.size == 2:
        x = np.linspace(p0[0]-5*np.sqrt(cov[0,0]),p0[0]+5*np.sqrt(cov[0,0]),100)
        y = np.linspace(p0[1]-5*np.sqrt(cov[1,1]),p0[1]+5*np.sqrt(cov[1,1]),100)

        X,Y = np.meshgrid(x,y)

        #L might not be vectorized in terms of p, so will calculate the values
        #separately for compatibility
        L = np.zeros(X.shape)

        for i in range(L.shape[0]):
            for j in range(L.shape[1]):
                L[i,j] = fitresult.L([x[i],y[j]])

        #Normalize L
        L = L-np.max(L[:])

        #Calculate L values for the gaussian approximation
        Lapprox = np.zeros(X.shape)

        for i in range(L.shape[0]):
            for j in range(L.shape[1]):
                coord = np.array([[X[i,j]-p0[0],Y[i,j]-p0[1]]]).T
                Lapprox[i,j] = -0.5*np.dot(coord.T,np.dot(invcov,coord))

        if plot_likelihood:
            plt.pcolor(X,Y,L)

        else:
            #Compute probablity
            p = np.exp(L)

            plt.pcolor(X,Y,p)


        #plot sigma contours
        CS = plt.contour(X,Y,Lapprox,[-4.5,-2,-0.5],colors='black',linestyles='solid')

        fmt = {}
        strs = ['$3 \sigma$','$2 \sigma$','$1 \sigma$']
        for l, s in zip(CS.levels, strs):
            fmt[l] = s

        # Label every other level using strings
        plt.clabel(CS, CS.levels, inline=True, fmt=fmt, fontsize=10)

        plt.xlabel('$p_1$')
        plt.ylabel('$p_2$')

    else:
        print('More than 2-parameter plots not supported yet!')
