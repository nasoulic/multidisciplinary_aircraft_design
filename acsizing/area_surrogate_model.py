import numpy as np
from openmdao.surrogate_models.multifi_cokriging import MultiFiCoKriging

input_data = np.loadtxt('./acsizing/Surrogates/DOE25')
vsp_result = np.loadtxt('./acsizing/Surrogates/results25')

def make_cokriging_fuselage_volume(val):

    '''
    -------------------------------------------------------------------------------
    Co-Kriging model to predict fuselage volume from it's dimensions

    INPUTS:
    val :                   Fuselage length
    -------------------------------------------------------------------------------
    '''

    xtrain = input_data[:, 0].reshape(-1, 1)
    ytrain = vsp_result[-2, :].reshape(-1, 1)

    # Setup Kriging
    model = MultiFiCoKriging(theta0=1, thetaL=1e-5, thetaU=50.)
    model.fit([xtrain], [ytrain])
    ret = model.predict(val)
    
    return ret[0][0][0]

def make_cokriging_wing_volume(val):

    '''
    -------------------------------------------------------------------------------
    Co-Kriging model to predict wing volume from it's dimensions

    INPUTS:
    val :                   Wing Sref
    -------------------------------------------------------------------------------
    '''

    xtrain = input_data[:, 1].reshape(-1, 1)
    ytrain = vsp_result[-1, :].reshape(-1, 1)

    # Setup Kriging
    model = MultiFiCoKriging(theta0=1, thetaL=1e-5, thetaU=50.)
    model.fit([xtrain], [ytrain])
    ret = model.predict(val)
    
    return ret[0][0][0]

def make_cokriging_fuselage_wetted(val):

    '''
    -------------------------------------------------------------------------------
    Co-Kriging model to predict fuselage wetted area from it's dimensions

    INPUTS:
    val :                   Fuselage length
    -------------------------------------------------------------------------------
    '''

    xtrain = input_data[:, 0].reshape(-1, 1)
    ytrain = vsp_result[0, :].reshape(-1, 1)

    # Setup Kriging
    model = MultiFiCoKriging(theta0=1, thetaL=1e-5, thetaU=50.)
    model.fit([xtrain], [ytrain])
    ret = model.predict(val)
    
    return ret[0][0][0]

def make_cokriging_main_wing_wetted(val):

    '''
    -------------------------------------------------------------------------------
    Co-Kriging model to predict wing wetted area from it's dimensions

    INPUTS:
    val :                   Wing Sref
    -------------------------------------------------------------------------------
    '''

    xtrain = input_data[:, 1].reshape(-1, 1)
    ytrain = vsp_result[1, :].reshape(-1, 1)

    # Setup Kriging
    model = MultiFiCoKriging(theta0=1, thetaL=1e-5, thetaU=50.)
    model.fit([xtrain], [ytrain])
    ret = model.predict(val)
    
    return ret[0][0][0]

def make_cokriging_horizontal_tail_wetted(val):

    '''
    -------------------------------------------------------------------------------
    Co-Kriging model to predict horizontal tail wetted area from it's dimensions

    INPUTS:
    val :                   Horizontal Tail Sref
    -------------------------------------------------------------------------------
    '''

    xtrain = input_data[:, 0:1].reshape(-1, 1)
    ytrain = vsp_result[2, :].reshape(-1, 1)

    # Setup Kriging
    model = MultiFiCoKriging(theta0=1, thetaL=1e-5, thetaU=50.)
    model.fit([xtrain], [ytrain])
    ret = model.predict(val)
    
    return ret[0][0][0]

def make_cokriging_vertical_tail_wetted(val):

    '''
    -------------------------------------------------------------------------------
    Co-Kriging model to predict vertical tail wetted area from it's dimensions

    INPUTS:
    val :                   Vertical Tail Sref
    -------------------------------------------------------------------------------
    '''

    xtrain = input_data[:, 0:1].reshape(-1, 1)
    ytrain = vsp_result[3, :].reshape(-1, 1)

    # Setup Kriging
    model = MultiFiCoKriging(theta0=1, thetaL=1e-5, thetaU=50.)
    model.fit([xtrain], [ytrain])
    ret = model.predict(val)
    
    return ret[0][0][0]

def engine_wetted_area():

    '''
    -------------------------------------------------------------------------------
    Co-Kriging model to predict engine wetted area from it's dimensions
    -------------------------------------------------------------------------------
    '''

    swe = vsp_result[-3, :]
    
    return np.average(swe)