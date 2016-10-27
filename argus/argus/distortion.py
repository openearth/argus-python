import numpy as np


def undistort(U, V, center=(0,0), coefs=(0,0), K=np.identity(3)):

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

    dU = U.astype(np.float32) - center[0]
    dV = V.astype(np.float32) - center[1]
    
    r = np.sqrt(dU**2+dV**2)
    dr = coefs[0]*r**3 + coefs[1]*r
    pr = (r - dr) / r
    pr[np.isnan(pr)] = 1
    
    U = (dU * pr) + center[0]
    V = (dV * pr) + center[1]
    
    return U, V


def get_distortion_data(rectification_data):

    return dict(
        center = (rectification_data['D_U0'], rectification_data['D_V0']),
        coefs = rectification_data['Drad'],
        K = rectification_data['K']
    )
