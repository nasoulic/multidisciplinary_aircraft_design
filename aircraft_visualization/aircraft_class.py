from aircraft_visualization.VSP_Objects import *

class aircraft(object):

    def __init__(self) -> None:

        pass

    def initialize_inputs(self, file_name):
        
        master_input = Read_Input_File(file_name)

        # form dictionaries from master input
        self.fuselage_input = master_input["Fuselage"]
        self.wing_input = master_input["Main_Wing"]
        self.horizontal_tail_input = master_input["Horizontal_Tail"]
        self.vertical_tail_input = master_input["Vertical_Tail"]
        self.engine_L_input = master_input["PT6A - 67D L"]
        self.engine_R_input = master_input["PT6A - 67D R"]
        self.landing_gear_input = master_input["Landing_Gear"]
        self.wing_reinforcement_input = master_input["Wing_Reinforcement"]
        self.cockpit_input = master_input["Cockpit"]
        self.cabin_input = master_input["Cabin"]
        self.cargo_1_input = master_input["Cargo Box 1"]
        self.cargo_2_input = master_input["Cargo Box 2"]
        self.cargo_3_input = master_input["Cargo Box 3"]
        self.cargo_4_input = master_input["Cargo Box 4"]
        try:
            self.duct_input = master_input['Duct']
        except:
            pass

        self.assembly_list = []

    def add_fuselage(self, fuselage_input):

        fuselage = Fuselage(fuselage_input)
        self.assembly_list.append(fuselage)

    def add_wing(self, wing_input):

        wing = Wing(wing_input)
        self.assembly_list.append(wing)

    def add_engine(self, engine_input):

        engine = Engine(engine_input)
        self.assembly_list.append(engine)

    def add_reinforcements(self, reinf_inputs):

        reinfocement = Reinforcements(reinf_inputs)
        self.assembly_list.append(reinfocement)

    def add_cabin(self, cabin_input):

        cabin = Cabin(cabin_input)
        self.assembly_list.append(cabin)

    def add_box(self, box_input):

        box = Box(box_input)
        self.assembly_list.append(box)

    def add_duct(self, duct_input):

        duct = Duct(duct_input)
        self.assembly_list.append(duct)

    def form_assembly(self):

        for item in self.assembly_list:
            file_name = item.Get_Name()
            item.draw()
            if file_name == "Main_Wing":
                item.insert_control_surfaces()
            if file_name == "Horizontal_Tail":
                item.insert_control_surfaces()
            if file_name == "Vertical_Tail":
                item.insert_control_surfaces()

        # check_for_errors()
        WriteFile("Assembly")

        for item in self.assembly_list:
            file_name = item.Get_Name()
            item.draw()
            if file_name == "Main_Wing":
                item.insert_control_surfaces()
            if file_name == "Horizontal_Tail":
                item.insert_control_surfaces()
            if file_name == "Vertical_Tail":
                item.insert_control_surfaces()
            # check_for_errors()
            WriteFile(file_name)