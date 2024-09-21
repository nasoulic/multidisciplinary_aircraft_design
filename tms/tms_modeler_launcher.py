import sys, json, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QFileDialog, QLabel, QComboBox, QFormLayout, QLineEdit, QDialog, QListWidget, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from tms.configparser_multi import configparser_multi
from tms.build_system import build_thermal_cycle

class Branch:
    def __init__(self, name):
        self.name = name
        self.components = []

class Component:
    def __init__(self, name, Q, A, Tlim):
        self.name = name
        self.Q = Q
        self.A = A
        self.Tlim = Tlim

class ConfigEditorPopup(QDialog):

    data_accepted = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Branch Configurator")
        self.branches = []
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        font = QFont()
        font.setBold(True)

        self.import_button = QPushButton("Load inputs from file")
        self.import_button.clicked.connect(self.load_inputs_from_file)
        self.defaults_button = QPushButton("Load defaults")
        self.defaults_button.clicked.connect(self.load_defaults)
        self.export_button = QPushButton("Export to JSON")
        self.export_button.clicked.connect(self.export_to_json)

        self.branch_name_label = QLabel("Thermal Branch Name:", self)
        self.branch_name_label.setFont(font)
        self.branch_name_input = QLineEdit()

        self.add_branch_button = QPushButton("Add Thermal Branch")
        self.add_branch_button.clicked.connect(self.add_branch)

        self.remove_branch_button = QPushButton("Remove Thermal Branch")
        self.remove_branch_button.clicked.connect(self.remove_branch)

        self.branch_list = QListWidget()
        self.branch_list.itemClicked.connect(self.show_components)

        self.component_list = QListWidget()     

        self.component_name_label = QLabel("Thermal Component Name:", self)
        self.component_name_label.setFont(font)
        self.component_name_input = QLineEdit()
        self.component_q_label = QLabel("Q:")
        self.component_q_input = QLineEdit()
        self.component_a_label = QLabel("A:")
        self.component_a_input = QLineEdit()
        self.component_tlim_label = QLabel("Tlim:")
        self.component_tlim_input = QLineEdit()

        self.component_list.itemClicked.connect(self.show_component_data)

        self.add_component_button = QPushButton("Add Thermal Component")
        self.add_component_button.clicked.connect(self.add_component)
        self.remove_component_button = QPushButton("Remove Thermal Component")
        self.remove_component_button.clicked.connect(self.remove_component)

        self.confirm_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        self.confirm_button.clicked.connect(self.accept)

        self.layout.addWidget(self.import_button)
        self.layout.addWidget(self.defaults_button)
        self.layout.addWidget(self.export_button)
        self.layout.addWidget(self.branch_list)
        self.layout.addWidget(self.branch_name_label)
        self.layout.addWidget(self.branch_name_input)
        self.layout.addWidget(self.add_branch_button)
        self.layout.addWidget(self.remove_branch_button)
        self.layout.addWidget(self.component_list)
        self.layout.addWidget(self.component_name_label)
        self.layout.addWidget(self.component_name_input)
        self.layout.addWidget(self.component_q_label)
        self.layout.addWidget(self.component_q_input)
        self.layout.addWidget(self.component_a_label)
        self.layout.addWidget(self.component_a_input)
        self.layout.addWidget(self.component_tlim_label)
        self.layout.addWidget(self.component_tlim_input)
        self.layout.addWidget(self.add_component_button)
        self.layout.addWidget(self.remove_component_button)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(button_layout)
        self.resize(350, 800)

        self.show()

    def add_branch(self):
        branch_name = self.branch_name_input.text()
        if branch_name:
            branch = Branch(branch_name)
            self.branches.append(branch)
            self.branch_list.addItem(branch.name)

    def remove_branch(self):
        selected_item = self.branch_list.currentItem()
        if selected_item:
            branch_name = selected_item.text()
            branch = next((b for b in self.branches if b.name == branch_name), None)
            if branch:
                self.branches.remove(branch)
                self.branch_list.takeItem(self.branch_list.row(selected_item))
                self.clear_component_fields()

    def add_component(self):
        branch_name = self.branch_name_input.text()
        component_name = self.component_name_input.text()
        Q = float(self.component_q_input.text())
        A = float(self.component_a_input.text())
        Tlim = int(self.component_tlim_input.text())

        if not branch_name or not component_name:
            return

        branch = next((b for b in self.branches if b.name == branch_name), None)
        if branch:
            component = Component(component_name, Q, A, Tlim)
            branch.components.append(component)
            self.show_components()
            self.clear_component_fields()

    def remove_component(self):
        selected_item = self.component_list.currentItem()
        if selected_item:
            branch_name = self.branch_name_input.text()
            component_name = selected_item.text()
            branch = next((b for b in self.branches if b.name == branch_name), None)
            if branch:
                component = next((c for c in branch.components if c.name == component_name), None)
                if component:
                    branch.components.remove(component)
                    self.show_components()
                    self.clear_component_fields()

    def show_components(self):
        selected_item = self.branch_list.currentItem()
        if selected_item:
            branch_name = selected_item.text()
            branch = next((b for b in self.branches if b.name == branch_name), None)
            if branch:
                # self.clear_component_fields()
                self.branch_name_input.setText(branch_name)
                self.component_list.clear()
                for component in branch.components:
                    self.component_list.addItem(component.name)

    def show_component_data(self, item):
        branch_name = self.branch_name_input.text()
        component_name = item.text()
        branch = next((b for b in self.branches if b.name == branch_name), None)
        if branch:
            component = next((c for c in branch.components if c.name == component_name), None)
            if component:
                # Update component data labels
                self.component_name_input.setText(component.name)
                self.component_q_input.setText(str(component.Q))
                self.component_a_input.setText(str(component.A))
                self.component_tlim_input.setText(str(component.Tlim))

    def clear_component_fields(self):
        self.component_name_input.clear()
        self.component_q_input.clear()
        self.component_a_input.clear()
        self.component_tlim_input.clear()

    def get_branch_data(self):
        config = {}
        for branch in self.branches:
            config[branch.name] = {}
            for i, component in enumerate(branch.components, 1):
                config[branch.name][f"Component{i}"] = {
                    "name": component.name,
                    "Q": component.Q,
                    "A": component.A,
                    "Tlim": component.Tlim,
                }
        return config
    
    def load_defaults(self):

        data = {
                "BATTERIES": {
                    "Component1": {
                        "name": "batteries",
                        "Q": 9.06,
                        "A": 7.9,
                        "Tlim": 321
                    }
                },
                "ELECTRIC MOTOR": {
                    "Component1": {
                        "name": "E-Motor",
                        "Q": 42.84,
                        "A": 0.606,
                        "Tlim": 363
                    },
                    "Component2": {
                        "name": "Inverter",
                        "Q": 5.76,
                        "A": 0.0276,
                        "Tlim": 344
                    }
                },
                "ELECTRIC GENERATOR": {
                    "Component1": {
                        "name": "E-Gen",
                        "Q": 9.78,
                        "A": 0.1606,
                        "Tlim": 363
                    },
                    "Component2": {
                        "name": "Converter",
                        "Q": 0.2,
                        "A": 0.00992,
                        "Tlim": 340
                    },
                    "Component3": {
                        "name": "DC-DC",
                        "Q": 0.258,
                        "A": 0.0216,
                        "Tlim": 347
                    }
                }
            }
        
        # Clear existing branches and components
        self.branch_list.clear()
        self.branches = []

        # Populate branches and components from the loaded JSON data
        for branch_name, components_data in data.items():
            branch = Branch(branch_name)
            for key, component_data in components_data.items():
                component_name = component_data.get("name", "")
                Q = component_data.get("Q", 0.0)
                A = component_data.get("A", 0.0)
                Tlim = component_data.get("Tlim", 0)
                component = Component(component_name, Q, A, Tlim)
                branch.components.append(component)
            self.branches.append(branch)
            self.branch_list.addItem(branch_name)
    
    def load_inputs_from_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load Config File", "", "Config Files (*.json)")
        if filename:
            try:
                with open(filename, "r") as f:
                    data = json.load(f)

                # Clear existing branches and components
                self.branch_list.clear()
                self.branches = []

                # Populate branches and components from the loaded JSON data
                for branch_name, components_data in data.items():
                    branch = Branch(branch_name)
                    for key, component_data in components_data.items():
                        component_name = component_data.get("name", "")
                        Q = component_data.get("Q", 0.0)
                        A = component_data.get("A", 0.0)
                        Tlim = component_data.get("Tlim", 0)
                        component = Component(component_name, Q, A, Tlim)
                        branch.components.append(component)
                    self.branches.append(branch)
                    self.branch_list.addItem(branch_name)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading data from file: {str(e)}")

    def export_to_json(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Config File", "", "Config Files (*.json)")
        if filename:
            with open(filename, "w") as f:
                json.dump(self.get_branch_data(), f, indent=4)

    def accept(self):
        # This method is automatically called when the "OK" button is clicked
        # Emit the signal with the heat exchanger data before closing the dialog
        data = self.get_branch_data()
        self.data_accepted.emit(data)
        super().accept()
        self.close()

class HeatExchangerConfiguratorPopup(QDialog):

    data_accepted = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("HEX Configurator")
        self.layout = QVBoxLayout(self)

        font = QFont()
        font.setBold(True)

        self.import_button = QPushButton("Load inputs from file")
        self.import_button.clicked.connect(self.load_inputs_from_file)
        self.defaults_button = QPushButton("Load defaults")
        self.defaults_button.clicked.connect(self.load_defaults)
        self.export_button = QPushButton("Export to JSON")
        self.export_button.clicked.connect(self.export_to_json)

        self.layout.addWidget(self.import_button)
        self.layout.addWidget(self.defaults_button)
        self.layout.addWidget(self.export_button)

        # Heat Exchanger Type Selection
        self.exchanger_type_label = QLabel("Select Heat Exchanger Type:", self)
        self.exchanger_type_label.setFont(font)
        self.exchanger_type_dropdown = QComboBox()
        self.exchanger_type_dropdown.addItems(["Cross-Flow"])
        self.layout.addWidget(self.exchanger_type_label)
        self.layout.addWidget(self.exchanger_type_dropdown)

        # Liquid-Air Heat Exchanger Config
        self.liquid_air_label = QLabel("Select Liquid-Air Heat Exchanger Configuration:", self)
        self.liquid_air_label.setFont(font)
        self.liquid_air_dropdown = QComboBox()
        self.liquid_air_dropdown.addItems(["Liquid-Air"])
        self.layout.addWidget(self.liquid_air_label)
        self.layout.addWidget(self.liquid_air_dropdown)

        # Primary Side Configuration
        self.primary_label = QLabel("Primary Side Configuration:", self)
        self.primary_label.setFont(font)
        self.primary_layout = QFormLayout()
        self.primary_coolant_dropdown = QComboBox()
        self.primary_coolant_dropdown.addItems(["Propylene Glycerol"])
        self.primary_layout.addRow("Coolant Type:", self.primary_coolant_dropdown)
        self.primary_coolant_percentage_input = QLineEdit()
        self.primary_layout.addRow("Coolant Solution Percentage (%):", self.primary_coolant_percentage_input)
        self.primary_inlet_temp_input = QLineEdit()
        self.primary_layout.addRow("Inlet Temperature (K):", self.primary_inlet_temp_input)
        self.primary_outlet_temp_input = QLineEdit()
        self.primary_layout.addRow("Outlet Temperature (K):", self.primary_outlet_temp_input)

        # Secondary Side Configuration
        self.secondary_label = QLabel("Secondary Side Configuration:", self)
        self.secondary_label.setFont(font)
        self.secondary_layout = QFormLayout()
        self.secondary_ambient_temp_input = QLineEdit()
        self.secondary_layout.addRow("Ambient Temperature (K):", self.secondary_ambient_temp_input)
        self.secondary_max_temp_difference_input = QLineEdit()
        self.secondary_layout.addRow("Max Temperature Difference (K):", self.secondary_max_temp_difference_input)

        self.confirm_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        self.confirm_button.clicked.connect(self.accept)

        self.layout.addWidget(self.primary_label)
        self.layout.addLayout(self.primary_layout)
        self.layout.addWidget(self.secondary_label)
        self.layout.addLayout(self.secondary_layout)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(button_layout)

        self.resize(350, 400)

    def get_heat_exchanger_data(self):
        data = {
            "Heat Exchanger Type": self.exchanger_type_dropdown.currentText(),
            "Liquid-Air Configuration": self.liquid_air_dropdown.currentText(),
            "Coolant Type": self.primary_coolant_dropdown.currentText(),
            "Coolant Solution Percentage": self.primary_coolant_percentage_input.text(),
            "Primary Inlet Temperature": self.primary_inlet_temp_input.text(),
            "Primary Outlet Temperature": self.primary_outlet_temp_input.text(),
            "Secondary Ambient Temperature": self.secondary_ambient_temp_input.text(),
            "Secondary Max Temperature Difference": self.secondary_max_temp_difference_input.text()
        }
        return data
    
    def load_defaults(self):
        
        data = {
            "Heat Exchanger Type": "Cross-Flow",
            "Liquid-Air Configuration": "Liquid-Air",
            "Coolant Type": "Propylene Glycol",
            "Coolant Solution Percentage": "30",
            "Primary Inlet Temperature": "280",
            "Primary Outlet Temperature": "288.15",
            "Secondary Ambient Temperature": "297",
            "Secondary Max Temperature Difference": "25"
        }

        # Fill in the input fields with data from the JSON file
        self.exchanger_type_dropdown.setCurrentText(data.get("Heat Exchanger Type", ""))
        self.liquid_air_dropdown.setCurrentText(data.get("Liquid-Air Configuration", ""))
        self.primary_coolant_dropdown.setCurrentText(data.get("Coolant Type", ""))
        self.primary_coolant_percentage_input.setText(data.get("Coolant Solution Percentage", ""))
        self.primary_inlet_temp_input.setText(data.get("Primary Inlet Temperature", ""))
        self.primary_outlet_temp_input.setText(data.get("Primary Outlet Temperature", ""))
        self.secondary_ambient_temp_input.setText(data.get("Secondary Ambient Temperature", ""))
        self.secondary_max_temp_difference_input.setText(data.get("Secondary Max Temperature Difference", ""))
    
    def load_inputs_from_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load Config File", "", "Config Files (*.json)")
        if filename:
            try:
                with open(filename, "r") as f:
                    data = json.load(f)

                # Fill in the input fields with data from the JSON file
                self.exchanger_type_dropdown.setCurrentText(data.get("Heat Exchanger Type", ""))
                self.liquid_air_dropdown.setCurrentText(data.get("Liquid-Air Configuration", ""))
                self.primary_coolant_dropdown.setCurrentText(data.get("Coolant Type", ""))
                self.primary_coolant_percentage_input.setText(data.get("Coolant Solution Percentage", ""))
                self.primary_inlet_temp_input.setText(data.get("Primary Inlet Temperature", ""))
                self.primary_outlet_temp_input.setText(data.get("Primary Outlet Temperature", ""))
                self.secondary_ambient_temp_input.setText(data.get("Secondary Ambient Temperature", ""))
                self.secondary_max_temp_difference_input.setText(data.get("Secondary Max Temperature Difference", ""))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading data from file: {str(e)}")

    def export_to_json(self):     
        filename, _ = QFileDialog.getSaveFileName(self, "Save Config File", "", "Config Files (*.json)")
        if filename:
            with open(filename, "w") as f:
                json.dump(self.get_heat_exchanger_data(), f, indent=4)

    def accept(self):
        # This method is automatically called when the "OK" button is clicked
        # Emit the signal with the heat exchanger data before closing the dialog
        data = self.get_heat_exchanger_data()
        self.data_accepted.emit(data)
        super().accept()
        self.close()


class TMSConfigApp(QDialog):
    def __init__(self, home_dir, output_dir):
        super().__init__()
        self.forced_convection_option = False
        self.force_laminar_primary_option = False

        self.setWindowTitle("TMS system config")
        # self.central_widget = QWidget()
        # self.setCentralWidget(self.central_widget)
        self.resize(350, 150)

        self.home_dir = home_dir
        self.output_dir = output_dir
        self.TMS_mass = 1e6

        # Create widgets
        self.btn_configure_thermal_branches = QPushButton("Configure thermal branches")
        self.btn_configure_hex = QPushButton("Configure HEX")
        self.checkbox_forced_convection = QCheckBox("Forced convection")
        self.checkbox_forced_convection.clicked.connect(self.forced_convection_check)
        self.checkbox_laminar_flow = QCheckBox("Force Laminar Flow on primary")
        self.checkbox_laminar_flow.clicked.connect(self.force_laminar_primary)
        self.btn_run_analysis = QPushButton("Run Analysis")
        self.confirm_button = QPushButton("OK")
        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)

        # Create layout
        layout = QVBoxLayout()
        # self.central_widget.setLayout(layout)
        self.setLayout(layout)

        # Add buttons and checkboxes to layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_configure_thermal_branches)
        button_layout.addWidget(self.btn_configure_hex)
        layout.addLayout(button_layout)
        layout.addWidget(self.checkbox_forced_convection)
        layout.addWidget(self.checkbox_laminar_flow)
        layout.addWidget(self.btn_run_analysis)

        button_layout1 = QHBoxLayout()
        button_layout1.addWidget(self.confirm_button)
        button_layout1.addWidget(self.cancel_button)
        layout.addLayout(button_layout1)

        # Connect buttons to their respective functions
        self.btn_configure_thermal_branches.clicked.connect(self.launch_configure_thermal_branches)
        self.btn_configure_hex.clicked.connect(self.launch_configure_hex)
        self.btn_run_analysis.clicked.connect(self.run_analysis)

    def launch_configure_thermal_branches(self):
        popup = ConfigEditorPopup()
        popup.data_accepted.connect(self.handle_branch_data_slot)  # Connect to the slot
        result = popup.exec_()
        if result == QDialog.Accepted:
            self.branch_data = popup.get_branch_data()
            # print(branch_data)

    def launch_configure_hex(self):
        popup = HeatExchangerConfiguratorPopup()
        popup.data_accepted.connect(self.handle_heat_exchanger_data_slot)  # Connect to the slot
        result = popup.exec_()
        if result == QDialog.Accepted:
            self.heat_exchanger_data = popup.get_heat_exchanger_data()
            # print(heat_exchanger_data)

    # Define a slot to handle the data received from the HeatExchangerConfiguratorPopup
    @pyqtSlot(dict)
    def handle_heat_exchanger_data_slot(self, data):
        # Do whatever you want with the data received from the dialog
        # print("Received heat exchanger data in TMSConfigApp:", data)
        # print("Received heat exchanger data in TMSConfigApp")
        pass

    @pyqtSlot(dict)
    def handle_branch_data_slot(self, data):
        # print("Received branch data in TMSConfigApp")
        pass

    def run_analysis(self):
        # Code to run the analysis

        os.chdir(self.output_dir)

        config = configparser_multi()

        for i in range(len(self.branch_data.keys())):
            config.add_section("Branch{0}".format(i + 1))
        
        i = 0
        for key, item in self.branch_data.items():
            config.config_sections["Branch{0}".format(i + 1)]["name"] = key
            for inkey, initem in item.items():
                config.add_subsection(inkey, "Branch{0}".format(i + 1))
                config.add_items(config.config_sections["Branch{0}".format(i + 1)][inkey], ["name", "Q", "A", "Tlim"], [ininitem for ininkey, ininitem in initem.items()])
            i += 1

        config.add_section("HEX")
        config.add_items(config.config_sections["HEX"], ["Tout", "Tin", "DT_secondary", "Tambient", "Coolant Solution"],
                         [float(self.heat_exchanger_data["Primary Outlet Temperature"]),
                          float(self.heat_exchanger_data["Primary Inlet Temperature"]), 
                          float(self.heat_exchanger_data["Secondary Max Temperature Difference"]),
                          float(self.heat_exchanger_data["Secondary Ambient Temperature"]), 
                          float(self.heat_exchanger_data["Coolant Solution Percentage"])])
        
        config.add_section("FLAGS")
        config.config_sections["FLAGS"]["forced convection"] = self.forced_convection_option
        config.config_sections["FLAGS"]["force laminar flow on primary"] = True
        
        config.write("TMS_system_layout.config")

        res = build_thermal_cycle()
        if res[0] < 0:
            self.TMS_mass = res[1]
            output_directory = os.getcwd() # Update with your actual output directory
            message = f"Calculation completed. Outputs exported to:\n{output_directory}"
            QMessageBox.information(self, "Calculation Completed", message, QMessageBox.Ok)
        
        os.chdir(self.home_dir)


    def forced_convection_check(self):
        self.forced_convection_option = not self.forced_convection_option
        # print(self.forced_convection_option)

    def force_laminar_primary(self):
        self.force_laminar_primary_option = not self.force_laminar_primary_option
        # print(self.force_laminar_primary_option)

    def confirm(self):
        self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TMSConfigApp()
    window.show()
    sys.exit(app.exec_())