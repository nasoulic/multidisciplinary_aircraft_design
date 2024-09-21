def Standard_Atmosphere(Units, Alt):
        
    '''
        INPUT:

        units  -  = Metric - metric units

                 <> Imperial - English units
    
        Alt  -  altitude, in feet or meters


        exit_value -    0 - good return

                        1 - error: altitude out of table,

                            do not use output (max altitude for this

                            routine is 84.85 km or 282,152 ft.)
    
            
        OUTPUT:

                        units:      metric              English

        T  - temp.                  deg K               deg F

        R  - density (rho)          kg/m^3              1E4 slug/ft^3

        P  - pressure               N/m^2               lb/ft^2

        A  - speed of sound         m/sec               ft/sec

        MU - viscosity              kg/(m sec)          1E7 slug/<ft sec)

        
        TS - t/t at sea level

        RR - rho/rho at sea level

        PP - p/p at sea level
    
        RM - Reynolds number per Mach per unit of length

        QM - dynamic pressure/Mach^2

    '''

    import numpy as np
    
    exit_value = 0
    K = 34.163195
    C1 = 3.048e-4
    T = 1
    PP = 0

    if Units == 'Metric':
        TL = 288.15
        PL = 101325
        RL = 1.225
        C1 = 0.001
        AL = 340.294
        ML = 1.7894e-5
        BT = 1.458e-6
        Temp = 0
    else:
        TL = 518.67
        PL = 2116.22
        RL = 0.0023769
        AL = 1116.45
        ML = 3.7373e-7
        BT = 3.0450963e-8
        Temp = -459.67

    H = C1*Alt/(1 + C1*Alt/6356.766)

    if H < 11:
        T = 288.15 - 6.5*H
        PP = (288.15/T)**(-K/6.5)
    elif H < 20:
        T = 216.65
        PP = 0.22336*np.exp(-K*(H - 11)/216.65)
    elif H < 32:
        T = 216.65 + (H - 20)
        PP = 0.054032*(216.65/T)**K
    elif H < 47:
        T = 228.65 + 2.8*(H -32)
        PP = 0.0085666*(228.65/T)**(K/2.8)
    elif H < 51:
        T = 270.65
        PP = 0.0010945*np.exp(-K*(H - 47)/270.65)
    elif H < 71:
        T = 270.65 - 2.8*(H - 51)
        PP = 0.00066063*(270.65/T)**(-K/2.8)
    elif H < 84.852:
        T = 214.65 - 2*(H - 71)
        PP = 3.9046e-5*(214.65/T)**(-K/2)
    else:
        exit_value = 1
        raise ValueError('Altitude is out of bounds!! Maximul altitude is 84.852 km.')
    
    P = PL*PP
    RR = PP/(T/288.15)
    R = RL*RR
    RAIR = P/(R*T)
    MU = BT*T**1.5/(T + 110.4)
    TS = T/288.15
    A = AL*TS**0.5
    T = TL*TS + Temp
    RM = R*A/MU
    QM = 0.7*P
    GAMMA = A**2/(RAIR*T)
    

    return [T, R, P, A, MU, RAIR, GAMMA, TS, RR, PP, RM, QM, exit_value]
