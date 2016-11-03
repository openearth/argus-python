import numpy as np


def undistort(U, V, center=(0,0), coefs=(0,0), K=np.identity(3)):
    '''Remove lens distortion from pixel coordinates based on coefficients in Argus database (latest version)

    Parameters
    ----------
    U : iterable
        Distorted horizontal pixel coordinates
    V : iterable
        Distorted vertical pixel coordinates
    center : 2-tuple
        Pixel coordinates of center pixel
    coefs : 2-tuple
        Radial distortion coefficients
    K : 3x3 numpy.ndarray
        Camera matrix

    Returns
    -------
    U : numpy.ndaarray
        Undistorted horizontal pixel coordinates
    V : numpy.ndaarray
        Undistorted vertical pixel coordinates

    See Also
    --------
    undistort_0
    undistort_1

    '''

    dU = (np.asarray(U) - center[0]) / K[0,0]
    dV = (np.asarray(V) - center[1]) / K[1,1]

    r = np.sqrt(dU**2 + dV**2)
    scale = 1. + np.polyval(coefs, r) / r
    scale[np.isnan(scale)] = 1.

    r = r / scale
    scale = 1. + np.polyval(coefs, r) / r
    scale[np.isnan(scale)] = 1.

    U = dU / scale * K[0,0] + center[0]
    V = dV / scale * K[1,1] + center[1]

    return U, V


def undistort_1(U, V, center=(0,0), coefs=(0,0), K=np.identity(3)):
    '''Remove lens distortion from pixel coordinates based on coefficients in Argus database (deprecated version)

    See :func:`undistort` for usage.

    '''

    lx = 1.006
    ly = -1.

    dU = (U / lx) - center[0]
    dV = (V / ly) - center[1]

    d2 = dU**2 + dV**2;
    scale = 1 + coefs[1] + coefs[0]*d2

    d2 = d2 / scale**2;
    scale = 1 + coefs[1] + coefs[0]*d2

    dU = dU / scale
    dV = dV / scale;

    U = (dU + center[0]) * lx
    V = (dV + center[1]) * ly

    
def undistort_0(U, V, center=(0,0), coefs=(0,0), K=np.identity(3)):
    '''Remove lens distortion from pixel coordinates based on coefficients in Argus database (initial version)

    See :func:`undistort` for usage.

    '''

    dU = U.astype(np.float32) - center[0]
    dV = V.astype(np.float32) - center[1]
    
    r = np.sqrt(dU**2+dV**2)
    dr = coefs[0]*r**3 + coefs[1]*r
    pr = (r - dr) / r
    pr[np.isnan(pr)] = 1
    
    U = (dU * pr) + center[0]
    V = (dV * pr) + center[1]
    
    return U, V
