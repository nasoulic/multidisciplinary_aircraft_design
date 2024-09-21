import os

def write_log(fname, model_ran, time, exit_code):

    '''
    ------------------------------------------------------------------
    Append to an existing log file

    INPUTS
    fname       : [string] [required]   log file name
    model_ran   : [string] [required]   model name
    time        : [list]   [required]   list of execution time and process time
                                        e.g. [et0, et1, pt0, pt1]
    exit_code   : [int]    [required]   model's exit code
    ------------------------------------------------------------------
    '''

    with open("{0}.log".format(fname), "a") as myfile:
        myfile.write('--------------------------------------------------------------------------- \n\n')
        myfile.write("{0} THERMAL MODEL BEGIN \n".format(model_ran))
        if exit_code < 0:
            myfile.write("{0} THERMAL MODEL FINNISHED SUCCESSFULLY \n".format(model_ran))
            myfile.write("ERROR CODE : %i \n" %(exit_code))
        else:
            myfile.write("{0} THERMAL MODEL TERMINATED WITH ERRORS \n".format(model_ran))
            myfile.write('ERROR CODE : %i \n' %(0))
        myfile.write('EXECUTION TIME : %f [s]\n' %(time[1] - time[0]))
        myfile.write('CPU TIME : %f [s]\n' %(time[3] - time[2]))
        myfile.write('{0} THERMAL MODEL END \n\n'.format(model_ran))
        myfile.write('--------------------------------------------------------------------------- \n\n')
    myfile.close()

def clear_log(fname):

    '''
    ------------------------------------------------------------------
    Clears previous log file
    ------------------------------------------------------------------
    '''

    with open("{0}.log".format(fname), "w") as myfile:
        pass
    myfile.close()

def create_report(branches, system_mass):

    items2write = ["mass flow", "specific heat", "inlet temperature", "outlet temperature"]
    units2write = ["[kg/s]", "[J/kgK]", "[K]", "[K]"]

    with open('./SYSTEM_SIZING_REPORT.dat', 'w') as myfile:
        for branch in branches:
            myfile.write("{0}\n".format(branch.name))
            myfile.write("==================================\n")
            for it, val, un in zip(items2write, branch.flow_conditions, units2write):
                myfile.write("{0}: {1} {2}\n".format(it, round(val, 3), un))
            for comp in branch.objs:
                myfile.write("Component: {0} Tlim: {1} [K] Toper: {2} [K]\n".format(comp.name, comp.Tlim, round(comp.Toper, 2)))
            myfile.write("Cooling sequence: {0}".format([comp.name for comp in branch.objs]))

            myfile.write("\n\n")
        myfile.write("TMS MASS BREAKDOWN\n")
        myfile.write("==================================\n")
        for key, item in system_mass.mass_breakdown.items():
            myfile.write("{0} mass {1} [kg]\n".format(key, round(item, 2)))
        myfile.write("TMS Combined Specific Power {0} [kW/kg]\n".format(system_mass.csp))
    myfile.close()

    print("----------------------------------------------------------------------------------------------- \n")
    print("File {0} exported to path : {1} \n".format('SYSTEM_SIZING_REPORT.dat', os.getcwd()))
    print("----------------------------------------------------------------------------------------------- \n\n")
    
    return -1

def log_msg(fname):

    print("----------------------------------------------------------------------------------------------- \n")
    print("File {0}.log exported to path : {1} \n".format(fname, os.getcwd()))
    print("----------------------------------------------------------------------------------------------- \n\n")