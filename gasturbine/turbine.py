import numpy as np
from gasturbine.gas_properties import gas_properties

def turbine(far, delta_h, eta_mech, eta_poly, bl, point):
    
    '''
    -------------------------------------------
    Define turbine
    
    far         : fuel to air ratio
    delta_h     : enthalpic difference of points 1 and 2
    eta_mech    : shaft mechanical efficiency
    eta_poly    : polytropic efficiency
    bl          : bleed air ratio
    point       : list
                point[0] : Pressure (Total)
                point[1] : Temperature (Total)
                point[2] : mass flow
                point[3] : entropy
                
    -------------------------------------------
    '''
    
    Po1, To1, m1, So1 = point
    gas_props = gas_properties()
    
    T2 = To1
    To2 = 1e10
    while abs(T2 - To2) > 1:
        cp = gas_props.cp_hot(0.5*(To1 + T2), far)
        To2 = To1 - delta_h/(cp*((1 - bl)*(1 + far) + bl)*eta_mech)
        T2 -= 1
    
    cp_mid = gas_props.cp_hot(0.5*(To1 + To2), far)
    gamma_mid = gas_props.gamma(cp_mid, gas_props.R_kerosene_hot(far))
    Po2 = Po1*(To2/To1)**(gamma_mid/(eta_poly*(gamma_mid - 1)))

    PRt = Po1/Po2
    
    nt_is = (1 - (1/PRt)**((gamma_mid - 1)*eta_poly/gamma_mid))/(1 - (1/PRt)**((gamma_mid - 1)/gamma_mid))
    
    So2 = So1 + gas_props.ds_hot(To1, To2, far) - gas_props.R_kerosene_hot(far)*np.log(Po2/Po1)
    ho2 = gas_props.h_hot(To2, far)
    ho1 = gas_props.h_hot(To1, far)
    delta_h = ((1 - bl)*(1 + far) + bl)*(ho2 - ho1)*eta_mech

    return [m1, To2, Po2, ho2, So2, nt_is, PRt, delta_h]