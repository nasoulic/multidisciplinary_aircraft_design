from gasturbine.gas_properties import gas_properties
import numpy as np

def nozzle(far, Penv, Tenv, n_nozzle, l_opt, Dh_aver, point):
    
    '''
    -------------------------------------------
    Define isentropic nozzle
    
    far         : fuel to air ratio
    Penv        : Ambient pressure
    Tenv        : Ambient temperature
    n_nozzle    : Isentropic efficiency
    l_opt       : optimum split
    Dh_aver     : hyrdaulic diameter (avg.)    
    point       : list 
            point[0] : Pressure (Total)
            point[1] : Temperature (Total)
            point[2] : mass flow
            point[3] : entropy
    -------------------------------------------
    '''
    
    Po1, To1, m1, So1 = point

    gas_props = gas_properties()
    
    cp = gas_props.cp_hot(0.5*(To1 + Tenv), far)
    gamma = gas_props.gamma(cp, gas_props.R_kerosene_hot(far))
    
    PRnozzle = Po1/Penv
    Tois = To1/PRnozzle**((gamma - 1)/gamma)
    To2 = To1 - n_nozzle*(To1 - Tois)
    Po2 = Po1/PRnozzle
    So2 = So1 + gas_props.ds_hot(To1, To2, far) - gas_props.R_kerosene_hot(far)*np.log(Po2/Po1)
    ho2 = gas_props.h_hot(To2, far)
    vjet = (2*(1 - l_opt)*Dh_aver*n_nozzle)**0.5
    
    return [m1, To2, Po2, ho2, So2, vjet, PRnozzle]