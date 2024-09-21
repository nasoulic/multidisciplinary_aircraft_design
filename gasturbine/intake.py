from gasturbine.gas_properties import gas_properties

def intake(nis, point):
    
    '''
    -------------------------------------------
    Define isentropic intake
    
    nis     : Isentropic efficiency
    point   : list 
            point[0] : Pressure (Total)
            point[1] : Temperature (Total)
            point[2] : mass flow
            point[3] : entropy
    -------------------------------------------
    '''
    
    Po1, To1, m1, So1 = point
    intake_air = gas_properties()
    
    Ptot_intake = nis*Po1
    Ttot_intake = To1
    htot_intake = intake_air.h_cold(Ttot_intake)
    
    return [m1, Ttot_intake, Ptot_intake, htot_intake, So1]