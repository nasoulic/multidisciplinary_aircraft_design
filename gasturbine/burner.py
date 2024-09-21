from gasturbine.gas_properties import gas_properties
import numpy as np

def burner(eta_burner, TET, dp, LHV, bl, point):
    
    '''
    -------------------------------------------
    Define burner
    
    eta_burner      : burner efficiency
    TET             : turbine entry temperature
    dp              : burner pressure drop
    LHV             : Jet-A fuel low heating value
    point           : list 
                    point[0] : Pressure (Total)
                    point[1] : Temperature (Total)
                    point[2] : mass flow
                    point[3] : entropy
    
    -------------------------------------------
    '''
    
    gas_props = gas_properties()
    [Po1, To1, m1, So1] = point
    
    f = 1e-10
    fx = 1e-3
    while abs(fx - f) > 1e-4:
        f = (1 - bl)*(gas_props.h_hot(TET, fx) - gas_props.h_cold(To1))/(eta_burner*LHV)
        fx += 1e-4
    
    To2 = (1 - bl)*TET + bl*To1
    Po2 = Po1*(1 - dp)
    
    # sgen = (1 - bl)*(gas_props.ds_hot(To2, TET, f)  - gas_props.R_kerosene_hot(f)*np.log(Po2/Po1)) + bl*gas_props.ds_cold(To1, To2)
    So2 = So1 + gas_props.ds_hot(To1, To2, f) - gas_props.R_kerosene_hot(f)*np.log(Po2/Po1)
    ho2 = gas_props.h_hot(To2, f)
    ho1 = gas_props.h_cold(To1)
    
    q = ((1 - bl)*(1 + f) + bl)*ho2 - ho1
    
    return [m1*(1 + f), To2, Po2, ho2, So2, f, q]
