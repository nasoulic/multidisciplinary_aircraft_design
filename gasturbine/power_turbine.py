from gasturbine.gas_properties import gas_properties
import numpy as np

def power_turbine(Penv, Tenv, far, bl, point, vinf, eta_nozzle, eta_prop, eta_gb, eta_pt, eta_mech):
    
    '''
    -------------------------------------------
    Define isentropic intake
    
    Penv        : Ambient total pressure
    Tenv        : Ambient total temperature
    far         : fuel to air ratio
    bl          : bleed air ratio
    point       : list
                point[0] : Pressure (Total)
                point[1] : Temperature (Total)
                point[2] : mass flow
                point[3] : entropy
    vinf        : freestream velocity
    eta_nozzle  : nozzle isentropic efficiency
    eta_prop    : propeller efficiency
    eta_gb      : gearbox efficiency
    eta_pt      : power turbine isentropic efficiency
    eta_mech    : shaft efficiency
    
    -------------------------------------------
    '''
    
    Po1, To1, m1, So1 = point
    gas_props = gas_properties()
    
    cp_f = gas_props.cp_hot(0.5*(To1 + Tenv), far)
    gamma_f = gas_props.gamma(cp_f, gas_props.R_kerosene_hot(far))
    
    T_ = To1*(Penv/Po1)**((gamma_f - 1)/gamma_f)
    delta_h_avg = gas_props.h_hot(To1, far) - gas_props.h_hot(T_, far)
    l_opt = 1 - eta_nozzle*vinf**2/(2*(eta_prop*eta_gb*eta_pt*eta_mech)**2*((1 - bl)*(1 + far) + bl)*delta_h_avg)
    T2 = To1
    To2 = 1e10
    while abs(T2 - To2) > 1:
        cp = gas_props.cp_hot(0.5*(To1 + T2), far)
        To2 = To1 - eta_pt*l_opt*delta_h_avg/cp
        T2 -= 1
    
    cp_mid = gas_props.cp_hot(0.5*(To1 + To2), far)
    gamma_mid = gas_props.gamma(cp_mid, gas_props.R_kerosene_hot(far))
    Po2 = Po1*(To1/(To1 - l_opt*delta_h_avg/cp_mid))**(-(gamma_mid/(gamma_mid - 1)))
    PRpt = Po1/Po2
    ho2 = gas_props.h_hot(To2, far)
    So2 = So1 + gas_props.ds_hot(To1, To2, far) - gas_props.R_kerosene_hot(far)*np.log(Po2/Po1)
    Dh_pt = -((1 - bl)*(1 + far) + bl)*eta_mech*eta_pt*l_opt*delta_h_avg
    
    return [m1, To2, Po2, ho2, So2, PRpt, Dh_pt, l_opt, delta_h_avg]