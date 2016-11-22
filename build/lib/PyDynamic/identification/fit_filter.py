# -*- coding: utf-8 -*-
'''
.. moduleauthor:: Sascha Eichstaedt (sascha.eichstaedt@ptb.de)
'''

from ..misc.filterstuff import grpdelay, mapinside

import numpy as np
import scipy.signal as dsp


#Todo: Include fitting of transfer function (continuous)
def LSIIR(Hvals,Nb,Na,f,Fs,tau=0,justFit=False):
    """Least-squares IIR filter fit to a given frequency response.
    
    This method uses Gauss-Newton non-linear optimization and pole
    mapping for filter stabilization
    
    Parameters:
        Hvals:   numpy array of frequency response values
        Nb:      integer numerator polynomial order
        Na:      integer denominator polynomial order
        f:       numpy array of frequencies at which Hvals is given
        Fs:      sampling frequency
        tau:     integer initial estimate of time delay
        justFit: boolean, when true then no stabilization is carried out
    
    Returns:
        b,a:    IIR filter coefficients as numpy arrays
        tau:    filter time delay in samples
    
    References:
    * Eichstädt et al. 2010 [Eichst2010]_
    * Vuerinckx et al. 1996 [Vuer1996]_
    
    """

    print("\nLeast-squares fit of an order %d digital IIR filter" % max(Nb,Na) )
    print("to a frequency response given by %d values.\n" % len(Hvals) )
  
    w = 2*np.pi*f/Fs
    Ns= np.arange(0,max(Nb,Na)+1)[:,np.newaxis]
    E = np.exp(-1j*np.dot(w[:,np.newaxis],Ns.T))
    
    def fitIIR(Hvals,tau,E,Na,Nb):
        # The actual fitting routine
        Ea= E[:,1:Na+1]
        Eb= E[:,:Nb+1]
        Htau = np.exp(-1j*w*tau)*Hvals
        HEa = np.dot(np.diag(Htau),Ea)
        D   = np.hstack((HEa,-Eb))
        Tmp1= np.real(np.dot(np.conj(D.T),D))
        Tmp2= np.real(np.dot(np.conj(D.T),-Htau))
        ab = np.linalg.lstsq(Tmp1,Tmp2)[0]
        a = np.hstack((1.0,ab[:Na]))
        b = ab[Na:]
        return b,a
        
    b,a = fitIIR(Hvals,tau,E,Na,Nb)
    
    if justFit:        
        print("Calculation done. No stabilization requested.")
        if np.count_nonzero(np.abs(np.roots(a))>1)>0:
            print( "Obtained filter is NOT stable.")
        sos = np.sum( np.abs( (dsp.freqz(b,a,2*np.pi*f/Fs)[1]-Hvals)**2 ) )
        print("Final sum of squares = %e" % sos)
        tau = 0
        return b,a,tau
    
    if np.count_nonzero(np.abs(np.roots(a))>1)>0:
        stable = False
    else:
        stable = True
    
    maxiter = 50
    
    astab = mapinside(a)
    run = 1
    
    while stable!=True and run < maxiter:
        g1 = grpdelay(b,a,Fs)[0]
        g2 = grpdelay(b,astab,Fs)[0]
        tau = np.ceil(tau + np.median(g2-g1))
        
        b,a = fitIIR(Hvals,tau,E,Na,Nb)
        if np.count_nonzero(np.abs(np.roots(a))>1)>0:
            astab = mapinside(a)
        else:
            stable = True
        run = run + 1
        
    if np.count_nonzero(np.abs(np.roots(a))>1)>0:
        print("Caution: The algorithm did NOT result in a stable IIR filter!")
        print("Maybe try again with a higher value of tau0 or a higher filter order?")
        
    print("Least squares fit finished after %d iterations (tau=%d)." % (run,tau))
    Hd = dsp.freqz(b,a,2*np.pi*f/Fs)[1]
    Hd = Hd*np.exp(1j*2*np.pi*f/Fs*tau)
    res= np.hstack((np.real(Hd) - np.real(Hvals), np.imag(Hd) - np.imag(Hvals)))
    rms= np.sqrt( np.sum( res**2 )/len(f))
    print("Final rms error = %e \n\n" % rms)

    return b,a,int(tau)    


def LSFIR(H,N,tau,f,Fs,Wt=None):
    """
    Least-squares fit of a digital FIR filter to a given frequency response.


    :param H: frequency response values
    :param N: FIR filter order
    :param tau: delay of filter
    :param f: frequencies
    :param Fs: sampling frequency of digital filter
    :param Wt: (optional) vector of weights

    :type H: ndarray
    :type N: int
    :type tau: int
    :type f: ndarray
    :type Fs: float

    :returns: filter coefficients bFIR (ndarray) of shape (N,)

    """

    print("\nLeast-squares fit of an order %d digital FIR filter to the" % N)
    print("reciprocal of a frequency response given by %d values.\n" % len(H))

    H = H[:,np.newaxis]

    w = 2*np.pi*f/Fs
    w = w[:,np.newaxis]

    ords = np.arange(N+1)[:,np.newaxis]
    ords = ords.T

    E = np.exp(-1j*np.dot(w,ords))

    if not Wt == None:
        if len(np.shape(Wt))==2: # is matrix
            weights = np.diag(Wt)
        else:
            weights = np.eye(len(f))*Wt
        X = np.vstack([np.real(np.dot(weights,E)), np.imag(np.dot(weights,E))])
    else:
        X = np.vstack([np.real(E), np.imag(E)])

    H = H*np.exp(1j*w*tau)
    iRI = np.vstack([np.real(1.0/H), np.imag(1.0/H)])

    bFIR, res = np.linalg.lstsq(X,iRI)[:2]

    if not isinstance(res,np.ndarray):
        print("Calculation of FIR filter coefficients finished with residual norm %e" % res)

    return np.reshape(bFIR,(N+1,))

