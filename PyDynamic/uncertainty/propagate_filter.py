# -*- coding: utf-8 -*-

import numpy as np
from scipy.signal import lfilter,tf2ss
from scipy.linalg import toeplitz
from ..misc.tools import zerom
# Note: The Elster-Link paper assumes that the autocovariance is known and that noise is stationary!

# TODO Implement formula for colored noise
# TODO Implement formula for covariance calculation


def FIRuncFilter(y,sigma_noise,theta,Utheta=None,shift=0,blow=None):
    """Uncertainty propagation for signal y and uncertain FIR filter theta

    Parameters
    ----------
        y: np.ndarray
            filter input signal
<<<<<<< HEAD
        sigma_noise: float
            standard deviation of white noise in y
=======
        sigma_noise: float or np.ndarray
            when float then standard deviation of white noise in y; when ndarray then point-wise standard uncertainties
>>>>>>> devel1
        theta: np.ndarray
            FIR filter coefficients
        Utheta: np.ndarray
            covariance matrix associated with theta
        shift: int
            time delay of filter output signal (in samples)
        blow: np.ndarray
            optional FIR low-pass filter

    Returns
    -------
        x: np.ndarray
            FIR filter output signal
        ux: np.ndarray
            point-wise uncertainties associated with x


    References
    ----------
        * Elster and Link 2008 [Elster2008]_

    .. seealso:: :mod:`PyDynamic.deconvolution.fit_filter`

    Todo:
        * Implement formula for colored noise
        * Implement formula for covariance calculation

    """
<<<<<<< HEAD
    if not isinstance(sigma_noise, float):
        raise NotImplementedError(
            "FIR formula for covariance propagation not implemented yet. Suggesting Monte Carlo propagation instead.")
    Ncomp = len(theta) - 1

    if not isinstance(Utheta, np.ndarray):
        Utheta = np.zeros((Ncomp, Ncomp))

    if isinstance(blow,np.ndarray):
        LR = 600
        Bcorr = np.correlate(blow, blow, 'full')
        ycorr = np.convolve(sigma_noise**2,Bcorr)
=======
    L = len(theta)
    if not isinstance(Utheta, np.ndarray):
        Utheta = np.zeros((L, L))

    if isinstance(blow,np.ndarray):
        LR = 600
        Bcorr = np.correlate(blow,blow,mode='full')
        if isinstance(sigma_noise,float):
            ycorr = np.convolve(sigma_noise**2,Bcorr)
        else:
            if len(sigma_noise.shape)==1:
                assert (len(sigma_noise)==len(y)), "Length of uncertainty and signal are inconsistent"
                ycorr = np.convolve(sigma_noise, Bcorr)
            else:
                raise NotImplementedError("FIR formula for covariance propagation not implemented. Suggesting Monte Carlo propagation instead.")
>>>>>>> devel1
        Lr = len(ycorr)
        Lstart = int(np.ceil(Lr//2))
        Lend = Lstart + LR -1
        Ryy = toeplitz(ycorr[Lstart:Lend])
        Ulow= Ryy[:Ncomp+1,:Ncomp+1]
        xlow = lfilter(blow,1.0,y)
    else:
        Ulow = np.eye(len(theta))*sigma_noise**2
        xlow = y

    x = lfilter(theta,1.0,xlow)
<<<<<<< HEAD
    x = np.roll(x,-int(shift))

    L = Utheta.shape[0]
    if len(theta.shape)==1:
        theta = theta[:, np.newaxis]
    UncCov = theta.T.dot(Ulow.dot(theta)) + np.abs(np.trace(Ulow.dot(Utheta)))
    unc = np.zeros_like(y)
    for m in range(L,len(xlow)):
        XL = xlow[m:m-L:-1, np.newaxis]
        unc[m] = XL.T.dot(Utheta.dot(XL))
    ux = np.sqrt(np.abs(UncCov + unc))
    ux = np.roll(ux,-int(shift))

    return x, ux.flatten()

=======
    x = np.roll(x,int(shift))

    if isinstance(sigma_noise, float):
        UncCov = np.dot(theta[:,np.newaxis].T,np.dot(Ulow,theta)) + np.abs(np.trace(np.dot(Ulow,Utheta)))
        unc = np.zeros_like(y)
        unc[:L] = 0.0
        for m in range(L,len(y)):
            XL = xlow[m:m-L:-1]
            unc[m] = np.dot(XL[:,np.newaxis].T,np.dot(Utheta,XL[:,np.newaxis]))

        ux = np.sqrt(np.abs(UncCov + unc))
    else:
        ux = np.zeros_like(y)
        ux[:L] = 0.0
        for m in range(L, len(y)):
            XL = xlow[m:m-L:-1]
            UL = Ulow[m:m-L:-1, m:m-L:-1]
            ux[m] = np.dot(theta[:,np.newaxis].T, UL.dot(theta)) + np.abs(np.trace( UL.dot(Utheta))) + \
                     np.dot(XL[:,np.newaxis].T, Utheta.dot(XL[:,np.newaxis]))

    ux = np.roll(ux,int(shift))
>>>>>>> devel1



#TODO: Remove utilization of numpy.matrix
#TODO: Extend to colored noise
#TODO: Allow zero uncertainty for filter
#TODO: use second-order-system structure for higher-order IIR filters (i.e. throw warning to user as a first step)
def IIRuncFilter(x, noise, b, a, Uab):
    """Uncertainty propagation for the signal x and the uncertain IIR filter (b,a)

    Parameters
    ----------
	    x: np.ndarray
	        filter input signal
	    noise: float
	        signal noise standard deviation
	    b: np.ndarray
	        filter numerator coefficients
	    a: np.ndarray
	        filter denominator coefficients
	    Uab: np.ndarray
	        covariance matrix for (a[1:],b)

    Returns
    -------
	    y: np.ndarray
	        filter output signal
	    Uy: np.ndarray
	        uncertainty associated with y

    References
    ----------
        * Link and Elster [Link2009]_

    .. seealso:: :mod:`PyDynamic.uncertainty.propagate_MonteCarlo.SMC`

	"""

    if not isinstance(noise, np.ndarray):
        noise = noise * np.ones(np.shape(x))

    p = len(a) - 1
    if not len(b) == len(a):
        b = np.hstack((b, np.zeros((len(a) - len(b),))))

    # from discrete-time transfer function to state space representation
    [A, bs, c, b0] = tf2ss(b, a)

    A = np.matrix(A)
    bs = np.matrix(bs)
    c = np.matrix(c)

    phi = zerom((2 * p + 1, 1))
    dz = zerom((p, p))
    dz1 = zerom((p, p))
    z = zerom((p, 1))
    P = zerom((p, p))

    y = np.zeros((len(x),))
    Uy = np.zeros((len(x),))

    Aabl = np.zeros((p, p, p))
    for k in range(p):
        Aabl[0, k, k] = -1

    for n in range(len(y)):
        for k in range(p):  # derivative w.r.t. a_1,...,a_p
            dz1[:, k] = A * dz[:, k] + np.squeeze(Aabl[:, :, k]) * z
            phi[k] = c * dz[:, k] - b0 * z[k]
        phi[p + 1] = -np.matrix(a[1:]) * z + x[n]  # derivative w.r.t. b_0
        for k in range(p + 2, 2 * p + 1):  # derivative w.r.t. b_1,...,b_p
            phi[k] = z[k - (p + 1)]
        P = A * P * A.T + noise[n] ** 2 * (bs * bs.T)
        y[n] = c * z + b0 * x[n]
        Uy[n] = phi.T * Uab * phi + c * P * c.T + b[0] ** 2 * noise[n] ** 2
        # update of the state equations
        z = A * z + bs * x[n]
        dz = dz1

    Uy = np.sqrt(np.abs(Uy))

    return y, Uy


