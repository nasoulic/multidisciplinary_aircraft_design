from gasturbine.gas_properties import gas_properties

def kerosene_properties():
    
    MW = 12*12 + 26*1
    cp = 2010
    LHV = 43.124*1e6

    return MW, cp, LHV

def air_properties():

    MW = 0.79*14*2 + 0.21*16*2
    Ru = 8314
    Rair = Ru/MW

    return MW, Rair

def mixture(T):

    lambda_combustion = 1
    air_props = gas_properties()
    cp_air = air_props.cp_cold(T)

    MW_air, Rair = air_properties()

    MW_kerosene, cp_kerosene, LHV = kerosene_properties()

    a_s = 12 + 26/4
    yf = 1 / (1 + 4.76*a_s)
    ya = 1 - yf

    MW_mix = yf*MW_kerosene + ya*MW_air
    cp_mix = yf*cp_kerosene + ya*cp_air
    R_mix = 8314/MW_mix
    gamma_mix = cp_mix/(cp_mix - R_mix)

    return MW_mix, cp_mix, gamma_mix, R_mix

