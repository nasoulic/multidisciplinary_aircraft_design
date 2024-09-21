from tms.configparser_multi import configparser_multi

def create_config():

    config = configparser_multi()

    config.add_section("Branch1")
    config.config_sections["Branch1"]["name"] = "BATTERIES"
    config.add_subsection("Component1", "Branch1")
    config.add_items(config.config_sections["Branch1"]["Component1"], ["name", "Q", "A", "Tlim"], ["batteries", 4.53*2, 2*3.95, 321] )
    
    config.add_section("Branch2")
    config.config_sections["Branch2"]["name"] = "ELECTRIC MOTOR"
    config.add_subsection("Component1", "Branch2")
    config.add_items(config.config_sections["Branch2"]["Component1"], ["name", "Q", "A", "Tlim"], ["E-Motor", 2*21.42, 2*0.303, 363 ] )
    config.add_subsection("Component2", "Branch2")
    config.add_items(config.config_sections["Branch2"]["Component2"], ["name", "Q", "A", "Tlim"], ["Inverter", 2*2.88, 2*0.0138, 344 ] )

    config.add_section("Branch3")
    config.config_sections["Branch3"]["name"] = "ELECTRIC GENERATOR"
    config.add_subsection("Component1", "Branch3")
    config.add_items(config.config_sections["Branch3"]["Component1"], ["name", "Q", "A", "Tlim"], ["E-Gen", 2*4.89, 2*0.0803, 363 ] )
    config.add_subsection("Component2", "Branch3")
    config.add_items(config.config_sections["Branch3"]["Component2"], ["name", "Q", "A", "Tlim"], ["Converter", 2*0.1, 2*0.00496, 340 ] )
    config.add_subsection("Component3", "Branch3")
    config.add_items(config.config_sections["Branch3"]["Component3"], ["name", "Q", "A", "Tlim"], ["DC-DC", 2*0.129, 2*0.0108, 347 ] )

    config.add_section("HEX")
    config.add_items(config.config_sections["HEX"], ["Tout", "Tin", "DT_secondary", "Tambient", "Coolant Solution"], [288.15, 280, 25, 297, 30])

    config.add_section("FLAGS")
    config.config_sections["FLAGS"]["forced convection"] = True
    config.config_sections["FLAGS"]["force laminar flow on primary"] = True

    config.write("system_layout.config")
    config.read("system_layout.config")



if __name__ == "__main__":
    create_config()
