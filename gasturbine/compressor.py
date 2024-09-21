import numpy as np
from gasturbine.gas_properties import gas_properties

def compressor(eta_poly, pr, point):
    
    '''
    -------------------------------------------
    Define compressor
    
    eta_poly        : polytropic efficiency
    pr              : pressure ratio
    point           : list 
    
                    point[0] : Pressure (Total)
                    point[1] : Temperature (Total)
                    point[2] : mass flow
                    point[3] : entropy
    
    -------------------------------------------
    '''
    
    Po1, To1, m1, so1 = point
    air_props = gas_properties()
    
    Po2 = Po1*pr
    T2 = To1
    To2 = 1e10
    while abs(T2 - To2) > 1:
        cp = air_props.cp_cold(0.5*(To1 + T2))
        gamma = air_props.gamma(cp, air_props.R_cold)
        To2 = To1*pr**((gamma - 1)/(gamma*eta_poly))
        T2 += 1
        
    cp_mid = air_props.cp_cold(0.5*(To1 + To2))
    gamma_mid = air_props.gamma(cp_mid, air_props.R_cold)
    
    nc_is = (pr**((gamma_mid - 1)/gamma_mid) - 1)/(pr**((gamma_mid - 1)/(gamma_mid*eta_poly)) - 1)
    so2 = so1 + air_props.ds_cold(To1, To2)  - air_props.R_cold*np.log(Po2/Po1)
    ho2 = air_props.h_cold(To2)
    ho1 = air_props.h_cold(To1)*To2
    
    return [m1, To2, Po2, ho2, so2]