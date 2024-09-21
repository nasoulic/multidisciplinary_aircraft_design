import numpy as np
from gasturbine.gas_properties import gas_properties

def pressure_drop(dp, point, cold = True, far = 0):
    
    '''
    -------------------------------------------
    Define pressure drop
    
    dp      : pressure drop ratio
    point   : list 
        point[0] : Pressure (Total)
        point[1] : Temperature (Total)
        point[2] : mass flow
        point[3] : entropy
    cold    : specify hot or cold gas
    far     : fuel to air ratio (only for hot gas)    
    
    -------------------------------------------
    '''
    
    Po1, To1, m1, So1 = point
    
    air_prop = gas_properties()
    
    Po2 = Po1*(1 - dp)
    To2 = To1
    
    if cold:
        cp = air_prop.cp_cold(To2)
        R = air_prop.R_cold
        So2 = So1 + air_prop.ds_cold(To1, To2)  - R*np.log(Po2/Po1)
    else:
        cp = air_prop.cp_hot(To2, far)
        R = air_prop.R_kerosene_hot(far)
        So2 = So1 + air_prop.ds_hot(To1, To2, far) - R*np.log(Po2/Po1)
    
    ho2 = air_prop.h_cold(To2)
    
    return [m1, To2, Po2, ho2, So2]