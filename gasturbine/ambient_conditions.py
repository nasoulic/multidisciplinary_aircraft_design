from gasturbine.gas_properties import gas_properties
from gasturbine.standard_atmosphere import Standard_Atmosphere as SA

def ambient_conditions(mair, alt, Vinf):
        
    '''
    -------------------------------------------
    Define free stream conditions
    -------------------------------------------
    '''

    ambient_atm = SA('Metric', alt)

    Tamb = ambient_atm[0]
    Pamb = ambient_atm[2]

    M0 = Vinf/ambient_atm[3]
    
    air = gas_properties()
    
    cp_amb = air.cp_cold(Tamb)
    g = air.gamma(cp_amb, air.R_cold)

    m0 = mair
    T0 = Tamb*(1 + (g - 1)/2*M0**2)
    P0 = Pamb*(T0/Tamb)**(g/(g - 1))
    cp0 = air.cp_cold(T0)
    h0 = air.h_cold(T0)
    s0 = 1600

    return [m0, T0, P0, h0, s0]