from tms.thermal_branch import thermal_branch_builder
from tms.create_log_file import clear_log, write_log, create_report, log_msg
from tms.flow_mixing import flow_mix
from tms.coolants_lib import propylene_glycerol_solution, air
from tms.heat_exchanger_model import heat_exchanger
from tms.overall_mass_calculation import thermal_management_system_mass_model
from tms.configparser_multi import configparser_multi
from time import process_time, time

def build_thermal_cycle():

    print("-----------------------------------------------------------------------------------------------\n")
    print("Reading TMS_system_layout.config file... \n")
    print("-----------------------------------------------------------------------------------------------\n\n")

    ## Read the config file
    config = configparser_multi()
    config.read("TMS_system_layout.config")

    input_args = config.config_file

    count_branches = 0
    for key in input_args.keys():
        if "Branch" in key:
            count_branches += 1

    if bool(input_args["FLAGS"]["forced convection"]):
        h = 30.48 # From our AIAA paper 
    else:
        h = 2 # Free convection value

    if bool(input_args["FLAGS"]["force laminar flow on primary"]):
        flow_type = "Laminar"
    else:
        flow_type = "Turbulent"

    clear_log("mylogfile")

    '''
    --------------------------------------------------------------
    Begin branch build
    --------------------------------------------------------------
    '''

    model_branch_list = []

    for i in range(count_branches): # include all thermal branches

        branch_args = input_args["Branch{0}".format(i + 1)]

        t0 = time()
        ct0 = process_time()

        branch = thermal_branch_builder()
        branch.rename_branch(branch_args["name"])

        count_components = 0
        for key in branch_args.keys():
            if "Component" in key:
                count_components += 1

        for j in range(count_components): # include all thermal components
            branch.add_component()
            branch.component.add_name(branch_args["Component{0}".format(j + 1)]["name"])
            branch.component.add_thermal_attributes(branch_args["Component{0}".format(j + 1)]["Q"]*1e3,
                                                    branch_args["Component{0}".format(j + 1)]["A"],
                                                    branch_args["Component{0}".format(j + 1)]["Tlim"])
            branch.component.Tamb = input_args["HEX"]["Tambient"]
            branch.component.Tin = input_args["HEX"]["Tout"]

        branch.define_cooling_sequence(branch.component_list)
        print("Add check for coolant type in line 72 (build system)")
        branch.add_coolant(propylene_glycerol_solution, sol = input_args["HEX"]["Coolant Solution"])
        branch.forced_convection(h)
        exit_code = branch.solve_heat_transfer_equations(branch.heat_transfer_equations, branch.initial_guess())
        branch.get_branch_flow_properties()

        t1 = time()
        ct1 = process_time()
        write_log("mylogfile", branch.name, [t0, t1, ct0, ct1], exit_code)

        model_branch_list.append(branch)


    '''
    --------------------------------------------------------------
    Flow mixing
    --------------------------------------------------------------
    '''

    t0 = time()
    ct0 = process_time()
    branch4 = thermal_branch_builder()
    branch4.rename_branch("MIXING_BRANCH")
    branch4.add_coolant(propylene_glycerol_solution, sol = input_args["HEX"]["Coolant Solution"])

    flow_mixer = flow_mix()
    flow_mixer.flow_mixing(model_branch_list)

    branch4.coolant_medium.specific_heat(0.5*(input_args["HEX"]["Tout"] + flow_mixer.T_mix))
    branch4.flow_conditions = [flow_mixer.m_mix, branch4.coolant_medium.Cp, input_args["HEX"]["Tout"], flow_mixer.T_mix]
    model_branch_list.append(branch4)

    t1 = time()
    ct1 = process_time()
    write_log("mylogfile", branch4.name, [t0, t1, ct0, ct1], -1)

    '''
    --------------------------------------------------------------
    Air branch
    --------------------------------------------------------------
    '''

    t0 = time()
    ct0 = process_time()

    Tair_out = input_args["HEX"]["Tin"] + input_args["HEX"]["DT_secondary"]

    branch5 = thermal_branch_builder()
    branch5.rename_branch("AIR_BRANCH")
    branch5.add_coolant(air)
    branch5.coolant_medium.specific_heat(0.5*(Tair_out + input_args["HEX"]["Tin"]))

    mfow_air = flow_mixer.m_mix*branch4.coolant_medium.Cp*(flow_mixer.T_mix - input_args["HEX"]["Tout"])/(branch5.coolant_medium.Cp*(Tair_out - input_args["HEX"]["Tin"]))

    branch5.flow_conditions = [mfow_air, branch5.coolant_medium.Cp, Tair_out, input_args["HEX"]["Tin"]]
    model_branch_list.append(branch5)

    t1 = time()
    ct1 = process_time()
    write_log("mylogfile", branch5.name, [t0, t1, ct0, ct1], -1)

    '''
    ------------------------------------------------------------------
    Evaluate heat exchanger area
    ------------------------------------------------------------------
    '''

    t0 = time()
    ct0 = process_time()

    heat_X = heat_exchanger()
    heat_X.add_name("HEAT EXCHANGER")
    heat_X.set_material("Aluminum")
    heat_X.set_fouling(1e-4)
    heat_X.set_primary_flow_type(flow_type)
    heat_X.set_primary_flow_hydraylic_diameter(0.018)
    heat_X.set_secondary_flow_hydraylic_diameter(0.24)
    Area = heat_X.eps_NTU(branch4, branch5, write_sizing_report = True)

    t1 = time()
    ct1 = process_time()

    write_log("mylogfile", heat_X.name, [t0, t1, ct0, ct1], -1)

    '''
    ------------------------------------------------------------------
    Calculate overall TMS mass
    ------------------------------------------------------------------
    '''
    t0 = time()
    ct0 = process_time()

    system_mass = thermal_management_system_mass_model()
    system_mass.add_name("TMS MASS")
    system_mass.Batteries_Qflow0 = input_args["Branch1"]["Component1"]["Q"]
    system_mass.Converter_Qflow0 = input_args["Branch3"]["Component2"]["Q"] + input_args["Branch3"]["Component3"]["Q"]
    system_mass.EG_Qflow0 = input_args["Branch3"]["Component1"]["Q"]
    system_mass.EM_Qflow0 = input_args["Branch2"]["Component1"]["Q"]
    system_mass.Inverter_Qflow0 = input_args["Branch2"]["Component2"]["Q"]

    tms_mass, tms_preq = system_mass.TMS_mass_calculation(m_tot = flow_mixer.m_mix, m_bat = model_branch_list[0].operating_conditions[-1],
                                                          m_eM = model_branch_list[1].operating_conditions[-1],
                                                          m_eG = model_branch_list[2].operating_conditions[-1], HT_Area = Area)

    t1 = time()
    ct1 = process_time()

    write_log("mylogfile", system_mass.name, [t0, t1, ct0, ct1], -1)
    log_msg("mylogfile")

    create_report(model_branch_list, system_mass)

    return [-1, system_mass.tms_mass_no_cold_plates]

if __name__ == "__main__":
    build_thermal_cycle()