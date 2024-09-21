from aircraft_visualization.aircraft_class import aircraft
from aircraft_visualization.naca_generator import naca

def build_aircraft(ac_name, configuration = "Conventional"):

    try:
        dash1 = aircraft()
        dash1.initialize_inputs('{0}.dat'.format(ac_name))

        dash1.add_fuselage(dash1.fuselage_input)

        main_wing_profile = naca()
        main_wing_profile.create_airfoil(dash1.wing_input['Profile'][4:], create_output = True)

        horizontal_tail_profile = naca()
        horizontal_tail_profile.create_airfoil(dash1.horizontal_tail_input['Profile'][4:], create_output = True)

        vertical_tail_profile = naca()
        vertical_tail_profile.create_airfoil(dash1.vertical_tail_input['Profile'][4:], create_output = True)

        dash1.add_wing(dash1.wing_input)
        dash1.add_wing(dash1.vertical_tail_input)
        dash1.add_wing(dash1.horizontal_tail_input)
        dash1.add_engine(dash1.engine_L_input)
        dash1.add_engine(dash1.engine_R_input)
        dash1.add_reinforcements(dash1.wing_reinforcement_input)
        dash1.add_reinforcements(dash1.landing_gear_input)
        dash1.add_cabin(dash1.cabin_input)
        dash1.add_cabin(dash1.cockpit_input)
        dash1.add_box(dash1.cargo_1_input)
        dash1.add_box(dash1.cargo_2_input)
        dash1.add_box(dash1.cargo_3_input)
        dash1.add_box(dash1.cargo_4_input)

        if "Series" and "Parallel" in configuration:
            dash1.add_duct(dash1.duct_input)

        if "Series" in configuration and "Parallel" not in configuration:
            extra_engines_R = dash1.engine_R_input
            extra_engines_L = dash1.engine_L_input
            extra_engines_R["Relative Position Y Eng"] = 0.38
            extra_engines_R["Relative Position X Eng"] = 0.35
            extra_engines_R["Relative Position X Prop"] = extra_engines_R["Relative Position X Eng"] + 0.0366
            extra_engines_R["Relative Position Y Prop"] = extra_engines_R["Relative Position Y Eng"]
            extra_engines_L["Relative Position Y Eng"] = -extra_engines_R["Relative Position Y Eng"]
            extra_engines_L["Relative Position X Eng"] = extra_engines_R["Relative Position X Eng"]
            extra_engines_L["Relative Position X Prop"] = extra_engines_R["Relative Position X Prop"]
            extra_engines_L["Relative Position Y Prop"] = -extra_engines_R["Relative Position Y Eng"]
            dash1.add_engine(extra_engines_L)
            dash1.add_engine(extra_engines_R)


        dash1.form_assembly()
        exit_code = -1
    
    except:
        exit_code = 1

    return exit_code

if __name__ == "__main__":
    print(build_aircraft("test_vsp_input_file"))