import sys, json, os
from PyQt5.QtWidgets import (QScrollArea, QApplication, QDialog, QWidget, QVBoxLayout, QGroupBox,
                             QLabel, QLineEdit, QPushButton, QTabWidget, QGridLayout, QFileDialog,
                             QMessageBox, QHBoxLayout)
from doc.DOC import Direct_Operating_Cost
from doc.post_processor_spider import generate_spider_plot

class AircraftCostCalculator(QDialog):
    def __init__(self, home_dir, output_dir):
        super().__init__()

        self.home_dir = home_dir
        self.output_dir = output_dir

        self.input_data = None

        self.setWindowTitle("Aircraft Annual Operating Cost Calculator")
        self.setGeometry(100, 100, 700, 800)

        # self.central_widget = QWidget()
        # self.setCentralWidget(self.central_widget)
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        
        # self.setLayout(self.layout)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.create_general_inputs_tab()
        self.create_energy_cost_inputs_tab()
        self.create_labor_cost_inputs_tab()
        self.create_aircraft_cost_inputs_tab()
        self.create_capital_cost_inputs_tab()

        self.central_widget.setLayout(self.layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.central_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

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

        self.calculate_button.clicked.connect(self.calculate_costs)
        self.load_button.clicked.connect(self.load_inputs_from_file)
        self.export_button.clicked.connect(self.export_inputs_to_file)
        self.save_fig_button.clicked.connect(self.export_result_plots)

        # self.setWidgetResizable(True)
        # self.setWidget(self.central_widget)
        # self.setLayout(self.layout)

        self.inputs = {}  # Store inputs in a dictionary

    def create_general_inputs_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout()
        tab.setLayout(tab_layout)

        general_inputs_defaults = {
            "block_time_input": "185",
            "days_in_year_input": "365",
            "checks_repairs_input": "11.4",
            "years_examined_input": "1",
            "day_off_time_input": "7",
            "navigation_factor_input": "850",
            "fixed_cost_per_flight_input": "100"
        }

        self.create_category(tab, "General Inputs", [
            ("Block Time (minutes):", "block_time_input", general_inputs_defaults["block_time_input"]),
            ("Days in Year:", "days_in_year_input", general_inputs_defaults["days_in_year_input"]),
            ("Checks/Repairs (days):", "checks_repairs_input", general_inputs_defaults["checks_repairs_input"]),
            ("Years Examined:", "years_examined_input", general_inputs_defaults["years_examined_input"]),
            ("Day-Off Time (hours):", "day_off_time_input", general_inputs_defaults["day_off_time_input"]),
            ("Navigation Factor (euro per km):", "navigation_factor_input", general_inputs_defaults["navigation_factor_input"]),
            ("Fixed Cost per Flight (euro per flight):", "fixed_cost_per_flight_input", general_inputs_defaults["fixed_cost_per_flight_input"])
        ])
        self.tab_widget.addTab(tab, "General Inputs")

    def create_energy_cost_inputs_tab(self):
        tab = QWidget()
        tab_layout = QGridLayout()  # Use a grid layout for Energy Pricing tab
        tab.setLayout(tab_layout)

        self.create_category(tab, "Energy Cost Inputs", [
            ("Fuel Price (euro per kg):", "fuel_price_input", "0.85"),
            ("Electricity Price (euro per kWh):", "electricity_price_input", "0.2")
        ])
        self.tab_widget.addTab(tab, "Energy Cost Inputs")

    def create_labor_cost_inputs_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout()
        tab.setLayout(tab_layout)

        self.create_category(tab, "Labor Cost Inputs", [
            ("Crew Complements:", "crew_complements_input", "5"),
            ("Pilots:", "pilots_input", "1"),
            ("Crew:", "crew_input", "0"),
            ("Pilot Salary (euro per year):", "pilot_salary_input", "80000"),
            ("Crew Salary (euro per year):", "crew_salary_input", "40000"),
            ("Labor Cost (euro per hour):", "labor_cost_input", "50")
        ])
        self.tab_widget.addTab(tab, "Labor Cost Inputs")

    def create_aircraft_cost_inputs_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout()
        tab.setLayout(tab_layout)

        aircraft_cost_defaults = {
            "block_fuel_input": "700",
            "battery_energy_input": "500",
            "payload_input": "1940",
            "max_takeoff_mass_input": "8000",
            "mission_range_input": "400",
            "empty_mass_input": "5000",
            "propulsion_mass_input": "740",
            "wing_span_input": "22.1",
            "fuselage_length_input": "14.5",
            "v1_velocity_input": "51",
            "max_total_gt_power_input": "1300",
            "max_em_power_input": "500",
            "battery_cycles_input": "1500",
            "battery_sets_input": "3"
        }

        self.create_category(tab, "Aircraft Cost Inputs", [
            ("Block Fuel (kg):", "block_fuel_input", aircraft_cost_defaults["block_fuel_input"]),
            ("Battery Energy (kWh):", "battery_energy_input", aircraft_cost_defaults["battery_energy_input"]),
            ("Payload (kg):", "payload_input", aircraft_cost_defaults["payload_input"]),
            ("Max Take-off Mass (kg):", "max_takeoff_mass_input", aircraft_cost_defaults["max_takeoff_mass_input"]),
            ("Mission Range (nm):", "mission_range_input", aircraft_cost_defaults["mission_range_input"]),
            ("Empty Mass (kg):", "empty_mass_input", aircraft_cost_defaults["empty_mass_input"]),
            ("Propulsion Mass (kg):", "propulsion_mass_input", aircraft_cost_defaults["propulsion_mass_input"]),
            ("Wing Span (m):", "wing_span_input", aircraft_cost_defaults["wing_span_input"]),
            ("Fuselage Length (m):", "fuselage_length_input", aircraft_cost_defaults["fuselage_length_input"]),
            ("V1 Velocity (m/s):", "v1_velocity_input", aircraft_cost_defaults["v1_velocity_input"]),
            ("Max Total GT Power (kW):", "max_total_gt_power_input", aircraft_cost_defaults["max_total_gt_power_input"]),
            ("Max EM Power (kW):", "max_em_power_input", aircraft_cost_defaults["max_em_power_input"]),
            ("Battery Cycles:", "battery_cycles_input", aircraft_cost_defaults["battery_cycles_input"]),
            ("Battery Sets:", "battery_sets_input", aircraft_cost_defaults["battery_sets_input"])
        ])
        self.tab_widget.addTab(tab, "Aircraft Cost Inputs")

    def create_capital_cost_inputs_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout()
        tab.setLayout(tab_layout)

        capital_cost_defaults = {
            "depreciation_period_input": "20",
            "interest_rate_input": "20",
            "residual_value_factor_input": "0.1",
            "insurance_rate_input": "0.5",
            "airframe_price_input": "1600",
            "gas_turbine_price_input": "560",
            "electric_motor_price_input": "150",
            "inverter_price_input": "75",
            "battery_price_input": "150",
            "k_eps_input": "0.2",
            "k_gt_input": "0.3",
            "k_af_input": "0.1",
            "eta_em_input": "0.96",
            "eta_pmad_input": "0.98"
        }

        self.create_category(tab, "Capital Cost Inputs", [
            ("Depreciation Period (years):", "depreciation_period_input", capital_cost_defaults["depreciation_period_input"]),
            ("Interest Rate (%):", "interest_rate_input", capital_cost_defaults["interest_rate_input"]),
            ("Residual Value Factor:", "residual_value_factor_input", capital_cost_defaults["residual_value_factor_input"]),
            ("Insurance Rate (%):", "insurance_rate_input", capital_cost_defaults["insurance_rate_input"]),
            ("Airframe Price (euro per kg):", "airframe_price_input", capital_cost_defaults["airframe_price_input"]),
            ("Gas Turbine Price (euro per kg):", "gas_turbine_price_input", capital_cost_defaults["gas_turbine_price_input"]),
            ("Electric Motor Price (euro per kg):", "electric_motor_price_input", capital_cost_defaults["electric_motor_price_input"]),
            ("Inverter Price (euro per kg):", "inverter_price_input", capital_cost_defaults["inverter_price_input"]),
            ("Battery Price (euro per kWh):", "battery_price_input", capital_cost_defaults["battery_price_input"]),
            ("k_EPS:", "k_eps_input", capital_cost_defaults["k_eps_input"]),
            ("k_GT:", "k_gt_input", capital_cost_defaults["k_gt_input"]),
            ("k_AF:", "k_af_input", capital_cost_defaults["k_af_input"]),
            ("eta_EM:", "eta_em_input", capital_cost_defaults["eta_em_input"]),
            ("eta_PMAD:", "eta_pmad_input", capital_cost_defaults["eta_pmad_input"])
        ])
        self.tab_widget.addTab(tab, "Capital Cost Inputs")

    def create_category(self, tab, title, labels_and_inputs):
        group_box = QGroupBox(title)
        category_layout = QVBoxLayout()
        group_box.setLayout(category_layout)

        for label_text, input_name, default_value in labels_and_inputs:
            label = QLabel(label_text)
            input_field = QLineEdit(default_value)
            input_field.setObjectName(input_name)  # Set the object name for the input field
            category_layout.addWidget(label)
            category_layout.addWidget(input_field)

        tab.layout().addWidget(group_box)

    def getInputData(self):

        # Create an empty dictionary to collect input data
        self.input_data = {}

        # Iterate through the tabs and retrieve input data
        for tab_index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(tab_index)

            # Iterate through the input fields in the current tab
            for widget in tab.findChildren(QLineEdit):
                input_name = widget.objectName()
                input_value = widget.text()
                self.input_data[input_name] = input_value
        
        for key, item in self.input_data.items():
            try:
                self.input_data[key] = float(item)
            except ValueError:
                raise ValueError("Could not convert %s string item into float".format(item))
        

    def calculate_costs(self, output_dir = None, export_msg = True):
        exit_code = 0
        
        if not self.input_data:
            self.getInputData()

        if not output_dir:
            os.chdir(output_dir)
        else:
            os.chdir(self.output_dir)

        aircraft = Direct_Operating_Cost()
        aircraft.load_data_from_input_list(self.input_data)
        aircraft.Evaluate_Design()
        aircraft.doc_breakdown()
        aircraft.write_outputs('./doc_results_bkdwn.csv', "full")
        aircraft.write_outputs('./doc_results_simple.csv', "simple")
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

                print(f"Input data loaded from '{file_path}' successfully.")
            except Exception as e:
                print(f"Error loading input data: {e}")

    def export_inputs_to_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly  # Allow read-only access to the selected file
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Input Data", "", "JSON Files (*.json)", options=options)

        if file_path:
            # Create an empty dictionary to collect input data
            input_data = {}

            # Iterate through the tabs and retrieve input data
            for tab_index in range(self.tab_widget.count()):
                tab = self.tab_widget.widget(tab_index)

                # Iterate through the input fields in the current tab
                for widget in tab.findChildren(QLineEdit):
                    input_name = widget.objectName()
                    input_value = widget.text()
                    input_data[input_name] = input_value

            # Save the collected input data as a JSON file
            try:
                with open(file_path, "w") as json_file:
                    json.dump(input_data, json_file, indent=4)
                print(f"Input data exported to '{file_path}' successfully.")
            except Exception as e:
                print(f"Error exporting input data: {e}")

    def export_result_plots(self, output_dir = None, export_msg = True):
        
        if not output_dir:
            os.chdir(output_dir)
        else:
            os.chdir(self.output_dir)
            
        generate_spider_plot("./doc_results_simple.csv")
        generate_spider_plot("./doc_results_bkdwn.csv")
        output_directory = os.getcwd() # Update with your actual output directory

        if export_msg:
            message = f"Outputs exported to:\n{output_directory}"
            QMessageBox.information(self, "Save Completed", message, QMessageBox.Ok)

        os.chdir(self.home_dir)
        return - 1
    
    def on_ok_clicked(self):
        self.accept() # Close the dialog and return QDialog.Accepted

    def on_cancel_clicked(self):
        self.reject() # Close the dialog and return QDialog.Rejected

def main():
    app = QApplication(sys.argv)
    window = AircraftCostCalculator()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
