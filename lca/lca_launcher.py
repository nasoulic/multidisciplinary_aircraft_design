import sys, json, os
from PyQt5.QtWidgets import (QScrollArea, QApplication, QDialog, QTabWidget, QWidget,
                             QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QGroupBox,
                             QFileDialog, QMessageBox, QHBoxLayout)
from lca.lca import Case, Share_emission, Share_sources, Share_Endpoints, Share_Midpoints, write_to_excel
from lca.lca_post_processor import create_donut_charts

class AircraftLifeCycleEval(QDialog):
    def __init__(self, home_dir, output_dir):
        super().__init__()

        self.home_dir = home_dir
        self.output_dir = output_dir
        self.inputData = None

        self.setWindowTitle("Aircraft Life Cycle Evaluation")
        self.setGeometry(100, 100, 700, 800)

        # self.central_widget = QWidget()
        # self.setCentralWidget(self.central_widget)

        self.central_widget =  QWidget()
        self.layout = QVBoxLayout(self.central_widget)

        # self.central_widget.setLayout(self.layout)
        # self.setLayout(self.layout)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.create_general_inputs_tab()
        self.create_mission_data_tab()
        self.create_aircraft_mass_tab()
        self.create_lca_settings_tab()

        self.central_widget.setLayout(self.layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.central_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

        # self.setWidgetResizable(True)
        # self.setWidget(self.central_widget)

        # self.resize(600, 600)

        self.calculate_button = QPushButton("Calculate")
        self.load_button = QPushButton("Read Inputs from File")
        self.export_button = QPushButton("Export Inputs")
        self.save_fig_button = QPushButton("Save Result Plots")
        self.save_fig_button.setDisabled(True)

        self.confirm_button = QPushButton("OK")
        self.confirm_button.clicked.connect(self.on_ok_clicked)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.calculate_button)
        button_layout.addWidget(self.save_fig_button)

        navi_buttons_layout = QHBoxLayout()
        navi_buttons_layout.addWidget(self.confirm_button)
        navi_buttons_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)
        main_layout.addLayout(navi_buttons_layout)
        
        # self.layout.addLayout(button_layout)
        # self.layout.addLayout(navi_buttons_layout)
        
        self.calculate_button.clicked.connect(self.perform_lca)
        self.load_button.clicked.connect(self.load_inputs_from_file)
        self.export_button.clicked.connect(self.export_inputs_to_file)
        self.save_fig_button.clicked.connect(self.export_result_plots)

        self.inputs = {}  # Store inputs in a dictionary

    def create_general_inputs_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout()
        tab.setLayout(tab_layout)

        general_default_values_dict = {
            "Max Number of Seats:": "19",
            "Battery Cycles:": "1500",
            "Service Ceiling [ft]:": "10000",
            "Number of Aircraft Built:": "2000",
            "Aircraft Life [years]:": "20",
            "Development Cost [USD billion]:": "2",
            "Entry Into Service date:": "2030",
            "Percentage of passenger mass on total payload mass of passenger aircraft [%]": "82",
            "Percentage of passengers mass on total payload mass at airports [%]": "70",
            "Average number of PAX per flight [%]": "85",
            "Number of flights per year (on average distance traveled)": "1630"
        }

        val2key_dict = {
            "Max Number of Seats:": "nseat_max",
            "Battery Cycles:": "battery cycles",
            "Service Ceiling [ft]:": "flight level",
            "Number of Aircraft Built:": "number of aircraft built",
            "Aircraft Life [years]:": "Airc_life",
            "Development Cost [USD billion]:": "dev_costs",
            "Entry Into Service date:": "EIS_date",
            "Percentage of passenger mass on total payload mass of passenger aircraft [%]": "palo_PAX",
            "Percentage of passengers mass on total payload mass at airports [%]": "palo_PAX_FH",
            "Average number of PAX per flight [%]": "p_seat",
            "Number of flights per year (on average distance traveled)": "num_flights_y"
        }

        general_tooltips_dict = {
            "Max Number of Seats:": "Maximum number of passenger seats in the aircraft",
            "Battery Cycles:": "Number of battery cycles before replacement",
            "Service Ceiling [ft]:": "Maximum altitude at which the aircraft can operate",
            "Number of Aircraft Built:": "Total number of aircraft built",
            "Aircraft Life [years]:": "Expected operational life of the aircraft",
            "Development Cost [USD billion]:": "Total development cost of the aircraft",
            "Entry Into Service date:": "Target Entry Into Service date",
            "Percentage of passenger mass on total payload mass of passenger aircraft [%]": "Percentage of passenger mass on total payload mass of passenger aircraft",
            "Percentage of passengers mass on total payload mass at airports [%]": "Percentage of passengers mass on total payload mass at airports",
            "Average number of PAX per flight [%]": "Average number of passengers per flight",
            "Number of flights per year (on average distance traveled)": "Number of flights per year (on average distance traveled)"
        }

        self.create_category(tab, "General Input", general_default_values_dict, general_tooltips_dict, val2key_dict) 
        self.tab_widget.addTab(tab, "General Input")



    def create_mission_data_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout()
        tab.setLayout(tab_layout)

        default_values_dict = {
            "Taxi Out & In Time [min]": "14",
            "Take-off & Overshoot Time [min]": "8",
            "Climb Time [min]": "16",
            "Approach Time [min]": "79",
            "Idle Time [min]": "14",
            "Turnaround Time [min]": "30",
            "Take-off Fuel Consumption [kg/s]": "0.11928",
            "Climb Fuel Consumption [kg/s]": "0.108109",
            "Cruise Fuel [kg]": "561.6",
            "Approach Fuel Consumption [kg/s]": "0.040181",
            "Idle Fuel Consumption [kg/s]": "0.013159",
            "Average Distance Traveled [%]": "85",
            "Average Flight Time [hr]": "3.39",
            "Max Range [nmi]": "500",
            "Mission Fuel Consumed [kg]": "927",
            "Electric Energy Consumption [kWh]": "690",
            "Average Load Factor [%]": "81"
        }

        value2key = {
            "Taxi Out & In Time [min]": "taxi time",
            "Take-off & Overshoot Time [min]": "take-off time",
            "Climb Time [min]": "climb time",
            "Approach Time [min]": "approach time",
            "Idle Time [min]": "idle time",
            "Turnaround Time [min]": "turnaround time",
            "Take-off Fuel Consumption [kg/s]": "take-off fuel",
            "Climb Fuel Consumption [kg/s]": "climb fuel",
            "Cruise Fuel [kg]": "fuel at cruise",
            "Approach Fuel Consumption [kg/s]": "approach fuel",
            "Idle Fuel Consumption [kg/s]": "idle fuel",
            "Average Distance Traveled [%]": "avg distance travel",
            "Average Flight Time [hr]": "flight time",
            "Max Range [nmi]": "maximum range",
            "Mission Fuel Consumed [kg]": "fuel",
            "Electric Energy Consumption [kWh]": "battery energy",
            "Average Load Factor [%]": "avg load factor"
        }

        tooltips_dict = {
            "Taxi Out & In Time [min]": "Time spent taxiing on the ground.",
            "Take-off & Overshoot Time [min]": "Time taken for take-off and overshoot phases.",
            "Climb Time [min]": "Time spent climbing after take-off until Top-of-Climb.",
            "Approach Time [min]": "Time taken during descent, approach and landing.",
            "Idle Time [min]": "Time spent in idle.",
            "Turnaround Time [min]": "Time taken for turnaround between flights.",
            "Take-off Fuel Consumption [kg/s]": "Fuel consumption during take-off.",
            "Climb Fuel Consumption [kg/s]": "Fuel consumption during the climb phase.",
            "Cruise Fuel [kg]": "Fuel consumed during cruise.",
            "Approach Fuel Consumption [kg/s]": "Fuel consumption during approach and landing.",
            "Idle Fuel Consumption [kg/s]": "Fuel consumption in idle.",
            "Average Distance Traveled [%]": "Average distance traveled compared to maximum range @ maximum payload",
            "Average Flight Time [hr]": "Average flight time per mission @ average distance traveled.",
            "Max Range [nmi]": "Maximum range of the aircraft @ maximum payload",
            "Mission Fuel Consumed [kg]": "Fuel consumed during an average mission.",
            "Electric Energy Consumption [kWh]": "Electric energy consumption rate at average travel distance",
            "Average Load Factor [%]": "Average payload for a typical mission compared to maximum payload."
        }

        self.create_category(tab, "Mission Data", default_values_dict, tooltips_dict, value2key) 
        self.tab_widget.addTab(tab, "Mission Data")

    def create_aircraft_mass_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout()
        tab.setLayout(tab_layout)

        aircraft_mass_default_values_dict = {
            "Main Wing Mass [kg]:": "740",
            "Vertical Stabilizer Mass [kg]:": "56",
            "Horizontal Stabilizer Mass [kg]:": "51",
            "Fuselage Mass [kg]:": "1402",
            "Engines Mass [kg]:": "739",
            "Nose Landing Gear Mass [kg]:": "53",
            "Main Landing Gear Mass [kg]:": "299",
            "Operating Empty Mass [kg]:": "4985",
            "Battery Mass [kg]:": "1656"
        }

        value2key = {
            "Main Wing Mass [kg]:": "main wing",
            "Vertical Stabilizer Mass [kg]:": "vertical stabilizer",
            "Horizontal Stabilizer Mass [kg]:": "horizontal stabilizer",
            "Fuselage Mass [kg]:": "fuselage",
            "Engines Mass [kg]:": "engines",
            "Nose Landing Gear Mass [kg]:": "nose landing gear",
            "Main Landing Gear Mass [kg]:": "main landing gear",
            "Operating Empty Mass [kg]:": "empty mass",
            "Battery Mass [kg]:": "batteries"
        }

        aircraft_mass_tooltips_dict = {
            "Main Wing Mass [kg]:": "Mass of the main wing",
            "Vertical Stabilizer Mass [kg]:": "Mass of the vertical stabilizer",
            "Horizontal Stabilizer Mass [kg]:": "Mass of the horizontal stabilizer",
            "Fuselage Mass [kg]:": "Mass of the fuselage",
            "Engines Mass [kg]:": "Mass of the engines",
            "Nose Landing Gear Mass [kg]:": "Mass of the nose landing gear",
            "Main Landing Gear Mass [kg]:": "Mass of the main landing gear",
            "Operating Empty Mass [kg]:": "Operating empty mass of the aircraft",
            "Battery Mass [kg]:": "Mass of the aircraft's battery"
        }

        self.create_category(tab, "Aircraft Mass", aircraft_mass_default_values_dict, aircraft_mass_tooltips_dict, value2key) 
        self.tab_widget.addTab(tab, "Aircraft Mass")

    def create_lca_settings_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout()
        tab.setLayout(tab_layout)

        self.create_dropdown(tab, "LCA Settings")
        self.tab_widget.addTab(tab, "LCA Settings")

    def create_category(self, tab, title, labels, tooltips, inp2obj):
        group_box = QGroupBox(title)
        category_layout = QVBoxLayout()
        group_box.setLayout(category_layout)

        # for label_text, input_name, default_value in labels_and_inputs:
        for key, item in labels.items():
            label = QLabel(key)
            input_field = QLineEdit(item)
            input_field.setObjectName(inp2obj[key])  # Set the object name for the input field
            input_field.setToolTip(tooltips[key])
            category_layout.addWidget(label)
            category_layout.addWidget(input_field)

        tab.layout().addWidget(group_box)

    def create_dropdown(self, tab, title):
        group_box = QGroupBox(title)
        category_layout = QVBoxLayout()
        group_box.setLayout(category_layout)

        # LCA Settings Labels
        electric_energy_label = QLabel("Electric Energy Production Method:")
        weighting_method_label = QLabel("Choose Weighting Method:")

        # LCA Settings Dropdowns
        electric_energy_combobox = QComboBox()
        electric_energy_combobox.addItems(["EU-Mix", "Renewables"])
        electric_energy_combobox.setCurrentIndex(0)
        electric_energy_combobox.setObjectName("Elec_prod_mtd")

        weighting_method_combobox = QComboBox()
        weighting_method_combobox.addItems(["Individualist", "Hierarchist", "Egalitarian"])
        weighting_method_combobox.setCurrentIndex(1)
        weighting_method_combobox.setObjectName("type_of_weight")

        category_layout.addWidget(electric_energy_label)
        category_layout.addWidget(electric_energy_combobox)

        category_layout.addWidget(weighting_method_label)
        category_layout.addWidget(weighting_method_combobox)

        tab.layout().addWidget(group_box)

    def perform_lca(self, output_dir = None, export_msg = True):
        exit_code = 0
        self.retreive_input_data()

        aircraft_config = Case("aircraft_01")

        if not output_dir:
            os.chdir(output_dir)
        else:
            os.chdir(self.output_dir)

        aircraft_config.write_config_file_from_GUI(self.inputData)
        aircraft_config.Read_config_file()

        try:
            aircraft_config.Execution()
        except Exception as e:
            self.show_exception_message(e)

        self.LCA_results = {}
        self.elec_prod = "EUMix"
        if aircraft_config.Elec_prod_mtd == 1:
            self.elec_prod = "renewables"

        self.weight_mtd = "individualist"
        if aircraft_config.type_of_weight == 1:
            self.weight_mtd = "hierarchist"
        elif aircraft_config.type_of_weight == 2:
            self.weight_mtd = "Egalitarian"

        write_to_excel({}, "aircraft_01", write_type = "w", elec_prod_mtd = aircraft_config.Elec_prod_mtd, weight_type = aircraft_config.type_of_weight)

        res = Share_emission(aircraft_config)
        self.LCA_results["Emissions Share"] = res
        write_to_excel(res, "aircraft_01", elec_prod_mtd = aircraft_config.Elec_prod_mtd, weight_type = aircraft_config.type_of_weight)

        res = Share_sources(aircraft_config)
        self.LCA_results["Sources Share"] = res
        write_to_excel(res, "aircraft_01", elec_prod_mtd = aircraft_config.Elec_prod_mtd, weight_type = aircraft_config.type_of_weight)

        res = Share_Endpoints(aircraft_config.xPKM_overall, aircraft_config.type_of_analys, aircraft_config.FL,
                              aircraft_config.weight_h, aircraft_config.weight_eco, aircraft_config.weight_r,
                              aircraft_config.xPKM_Cruise)
        self.LCA_results["Endpoints Share"] = res
        write_to_excel(res, "aircraft_01", elec_prod_mtd = aircraft_config.Elec_prod_mtd, weight_type = aircraft_config.type_of_weight)

        res = Share_Midpoints(aircraft_config.xPKM_overall, aircraft_config.type_of_analys, aircraft_config.FL,
                              aircraft_config.weight_h, aircraft_config.weight_eco, aircraft_config.weight_r,
                              aircraft_config.xPKM_Cruise)
        self.LCA_results["Midpoints Share"] = res
        write_to_excel(res, "aircraft_01", elec_prod_mtd = aircraft_config.Elec_prod_mtd, weight_type = aircraft_config.type_of_weight)
        exit_code = -1

        if export_msg:
            message = f"Calculation completed. Outputs exported to:\n{self.output_dir}"
            QMessageBox.information(self, "Calculation Completed", message, QMessageBox.Ok)

        self.save_fig_button.setEnabled(True)
        os.chdir(self.home_dir)

        return exit_code

    def load_inputs_from_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly  # Allow read-only access to the selected file
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Input Data from JSON", "", "JSON Files (*.json)", options=options)

        if file_path:
            try:
                # Open and load the selected JSON file
                with open(file_path, "r") as json_file:
                    input_data = json.load(json_file)

                # Update the input fields with the loaded data
                for tab_index in range(self.tab_widget.count()):
                    tab = self.tab_widget.widget(tab_index)

                    # Iterate through the input fields in the current tab
                    for widget in tab.findChildren(QLineEdit):
                        input_name = widget.objectName()

                        # Update the input field with the loaded value if it exists in the JSON data
                        if input_name in input_data:
                            widget.setText(input_data[input_name])
                            # print(f"Updated '{input_name}' with value '{input_data[input_name]}'")
                    
                    for widget in tab.findChildren(QComboBox):
                        input_name = widget.objectName()

                        # Update the input field with the loaded value if it exists in the JSON data
                        if input_name in input_data:
                            widget.setCurrentIndex(input_data[input_name])
                            # print(f"Updated '{input_name}' with value '{input_data[input_name]}'")

                print(f"Input data loaded from '{file_path}' successfully.")
            except Exception as e:
                print(f"Error loading input data: {e}")

    def export_inputs_to_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly  # Allow read-only access to the selected file
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Input Data", "", "JSON Files (*.json)", options=options)

        if file_path:
            # Create an empty dictionary to collect input data
            self.retreive_input_data()

            # Save the collected input data as a JSON file
            try:
                with open(file_path, "w") as json_file:
                    json.dump(self.inputData, json_file, indent=4)
                print(f"Input data exported to '{file_path}' successfully.")
            except Exception as e:
                print(f"Error exporting input data: {e}")

    def export_result_plots(self, output_dir = None, export_msg = True):

        if not output_dir:
            os.chdir(output_dir)
        else:
            os.chdir(self.output_dir)
            
        create_donut_charts(self.LCA_results, self.elec_prod, self.weight_mtd)

        if export_msg:
            output_directory = os.getcwd() # Update with your actual output directory
            message = f"Outputs exported to:\n{output_directory}"
            QMessageBox.information(self, "Output Completed", message, QMessageBox.Ok)

        os.chdir(self.home_dir)

    def retreive_input_data(self):
        input_data = {}

        # Iterate through the tabs and retrieve input data
        for tab_index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(tab_index)

            # Iterate through the input fields in the current tab
            for widget in tab.findChildren(QLineEdit):
                input_name = widget.objectName()
                input_value = widget.text()
                input_data[input_name] = input_value

            for widget in tab.findChildren(QComboBox):
                input_name = widget.objectName()
                input_value = widget.currentIndex()
                input_data[input_name] = input_value
        
        self.inputData = input_data
    
    def show_exception_message(self, exception):
        error_message = str(exception)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Exception")
        msg.setText("Error!:")
        msg.setInformativeText(error_message)
        msg.exec_()

    def on_ok_clicked(self):
        self.accept() # Close the dialog and return QDialog.Accepted

    def on_cancel_clicked(self):
        self.reject() # Close the dialog and return QDialog.Rejected

def main():
    app = QApplication(sys.argv)
    window = AircraftLifeCycleEval()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()