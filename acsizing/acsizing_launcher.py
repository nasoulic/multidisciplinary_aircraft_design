import sys, os
from PyQt5.QtWidgets import (QApplication, QDialog, QGridLayout, QWidget, QPushButton, QGroupBox,
                             QCheckBox, QLabel, QLineEdit, QComboBox, QVBoxLayout, QProgressBar, QMessageBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from tlars.tlars import TopLevelAircraftRequirementsForm
from tms.tms_modeler_launcher import TMSConfigApp
from acsizing.mission_profile import mission_profile
from acsizing.nested_gt_launcher import NestedGTlauncher
from acsizing.nested_gg_launcher import NestedGGlauncher
from acsizing.nested_propeller_launcher import NestedProplauncher
from acsizing.acsizing_wrapper import aircraft_sizing_wrapper
from acsizing.operating_modes_launcher import OperationModeDialog
from acsizing.acsizing_settings import AircraftSizingSettings
from aircraft_visualization.launch_openvsp import launch_openvsp
from aircraft_visualization.create_aircraft import build_aircraft
import openvsp as vsp

class AircraftSizingDialog(QDialog):
    def __init__(self, home_dir, output_dir):
        super().__init__()

        self.home_dir = home_dir
        self.output_dir = output_dir

        self.setWindowTitle("Aircraft Sizing Configurator")
        self.setGeometry(100, 100, 800, 600)

        self.tlars_window = None                        # Reference to TLARs instance
        self.TMS_window = None                          # Reference to TMS instance
        self.nested_GT_window = None                    # Reference to nested GT instance
        self.nested_prop_window = None                  # Reference to nested propeller instance
        self.mission_calculated = False                 # Reference to Plot Mission button
        self.operational_mode_configurator = False      # Reference to Set Operational Modes button
        self.acsizing_settings = None                   # Reference to acsizig advanced settings
        self.nested_GG_window = None                    # Reference to nested GG instance

        grid_layout = QGridLayout(self)
        self.create_tlars_group(grid_layout)
        self.create_eps_inputs_group(grid_layout)
        self.create_checkboxes_group(grid_layout)
        self.create_powertrain_group(grid_layout)
        self.create_buttons(grid_layout)

    def create_tlars_group(self, grid_layout):
        tlars_group = QGroupBox("TLARs")
        tlars_layout = QGridLayout()

        launch_button = QPushButton("Launch TLARs Configurator")
        launch_button.clicked.connect(self.launch_TLARS)
        launch_button.setToolTip("Launch the Top-Level Aircraft Requirements Configurator")
        self.mission_button = QPushButton("Plot Mission Profile")
        self.mission_button.clicked.connect(self.plot_mission_profile)
        self.mission_button.setToolTip("Plot the defined mission profile.")
        self.mission_button.setDisabled(True)

        tlars_layout.addWidget(launch_button)
        tlars_layout.addWidget(self.mission_button)

        tlars_group.setLayout(tlars_layout)
        grid_layout.addWidget(tlars_group, 0, 0)

    def create_eps_inputs_group(self, grid_layout):
        eps_inputs_group = QGroupBox("Define EPS Inputs")
        eps_inputs_layout = QGridLayout()

        self.eps_inputs = {
            "Battery specific energy [kWh/kg]"  : QLineEdit("0.65"),
            "Battery specific power [kW/kg]"    : QLineEdit("0.65"),
            "Specific power (electronics) [kW/kg]": QLineEdit("18"),
            "Specific power (motors) [kW/kg]": QLineEdit("10"),
            "Number of electric motors [-]" : QLineEdit("2"),
            "Electric motor revolutions per min [rpm]": QLineEdit("2000"),
            "Battery to shaft efficiency [%]": QLineEdit("92"),
            "System voltage [V]": QLineEdit("1200"),
            "Depth of discharge [%]": QLineEdit("80"),
            "Battery EOL State of Charge [%]": QLineEdit("80"),
            # Add more inputs as needed
        }

        eps_tooltip_data = {
            "Battery specific energy [kWh/kg]": "Specify the specific energy of the battery in kWh/kg.",
            "Battery specific power [kW/kg]": "Specify the specific power of the battery in kW/kg.",
            "Specific power (electronics) [kW/kg]": "Specify the specific power of the electronics in kW/kg.",
            "Specific power (motors) [kW/kg]": "Specify the specific power of the motors in kW/kg.",
            "Number of electric motors [-]" : "Specify the number of electric motors.",
            "Electric motor revolutions per min [rpm]": "Specify the revolutions per minute of the electric motor.",
            "Battery to shaft efficiency [%]": "Specify the efficiency from battery to shaft as a percentage (e.g., 92 for 92%).",
            "System voltage [V]": "Specify the system voltage in volts.",
            "Depth of discharge [%]": "Specify the depth of discharge as a percentage (e.g., 80 for 80%).",
            "Battery EOL State of Charge [%]": "Specify the end-of-life state of charge for the battery as a percentage (e.g., 80 for 80%).",
            # Add more inputs as needed
        }

        row = 0
        for key, input_widget in self.eps_inputs.items():
            eps_inputs_layout.addWidget(QLabel(key), row, 0)
            input_widget.setToolTip(eps_tooltip_data[key])
            input_widget.setEnabled(False)
            eps_inputs_layout.addWidget(input_widget, row, 1)
            row += 1

        eps_inputs_group.setLayout(eps_inputs_layout)
        grid_layout.addWidget(eps_inputs_group, 0, 1)

    def create_checkboxes_group(self, grid_layout):
        checkboxes_group = QGroupBox("Options")
        checkboxes_layout = QGridLayout()

        checkboxes_layout.addWidget(QLabel("Select aircraft propulsion configuration"), 0, 0)

        self.configuration_selection = QComboBox()
        # self.configuration_selection.addItems(["Conventional", "Parallel", "Series", "Series/Parallel"])
        self.configuration_selection.addItems(["Conventional", "Parallel", "Series"])
        self.configuration_selection.setCurrentIndex(0)
        self.configuration_selection.currentIndexChanged.connect(self.update_input_fields)
        checkboxes_layout.addWidget(self.configuration_selection, 0, 1)

        show_configuration = QPushButton("Show configuration")
        show_configuration.clicked.connect(self.show_aircraft_configuration)
        checkboxes_layout.addWidget(show_configuration)

        set_operating_modes = QPushButton("Define Operational Modes")
        set_operating_modes.clicked.connect(self.launch_operational_mode_configurator)
        checkboxes_layout.addWidget(set_operating_modes)

        self.allow_charging_checkbox = QCheckBox("Allow Charging")
        self.allow_charging_checkbox.setEnabled(False)
        self.advanced_materials_checkbox = QCheckBox("Advanced Materials")
        self.constrain_empty_mass = QCheckBox("Constrain OEM")

        acsizing_settings = QPushButton("Advanced Settings")
        acsizing_settings.clicked.connect(self.launch_acsizing_settings)
        checkboxes_layout.addWidget(acsizing_settings, 4, 1)

        checkboxes_layout.addWidget(self.allow_charging_checkbox, 2, 0)
        checkboxes_layout.addWidget(self.constrain_empty_mass, 3, 0)
        checkboxes_layout.addWidget(self.advanced_materials_checkbox, 4, 0)

        checkboxes_group.setLayout(checkboxes_layout)
        grid_layout.addWidget(checkboxes_group, 1, 0)

    def create_powertrain_group(self, grid_layout):
        self.powertrain_group = QGroupBox("Powertrain Specifications")
        self.powertrain_layout = QGridLayout()

        self.powertrain_specs_defaults = {
            "Fuel to Total Energy ratio" : QLineEdit("0.8"),
            "Electric to Total Power ratio" : QLineEdit("0.2"),
            "Gas Generator power output [kW]" : QLineEdit("1600"),
            "Gas Turbine SFC reduction compared to EIS 2014 [%]" : QLineEdit("20"),
            "Thermal Management System Mass [kg]" : QLineEdit("95"),
        }

        i = 0
        for key, item in self.powertrain_specs_defaults.items():
            self.powertrain_layout.addWidget(QLabel(key), i, 0)
            self.powertrain_layout.addWidget(item, i, 1)
            i += 1

        self.powertrain_specs_defaults["Fuel to Total Energy ratio"].setDisabled(True)
        self.powertrain_specs_defaults["Fuel to Total Energy ratio"].setText("1")
        self.powertrain_specs_defaults["Electric to Total Power ratio"].setDisabled(True)
        self.powertrain_specs_defaults["Electric to Total Power ratio"].setText("0")
        self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setDisabled(True)
        self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setText("0")
        self.powertrain_specs_defaults["Gas Generator power output [kW]"].setDisabled(True)
        self.powertrain_specs_defaults["Gas Generator power output [kW]"].setText("0")
        self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("0")
        self.launch_gg = QPushButton("Configure Gas Generator")
        self.launch_gg.setToolTip("Launch the Gas Generator Configurator.")
        self.launch_gg.clicked.connect(self.launch_GG_configurator)
        self.launch_gg.setEnabled(False)
        self.powertrain_layout.addWidget(self.launch_gg, 2, 2)
        
        self.launch_gt = QPushButton("Configure EIS 2014 GT")
        self.launch_gt.setToolTip("Launch the GT Configurator.")
        self.launch_gt.clicked.connect(self.launch_GT_configurator)
        self.powertrain_layout.addWidget(self.launch_gt, 3, 2)

        self.launch_prop = QPushButton("Configure Propeller")
        self.launch_prop.setToolTip("Launch the propeller efficiency configurator.")
        self.launch_prop.clicked.connect(self.launch_prop_configurator)
        self.powertrain_layout.addWidget(self.launch_prop, 3, 3)

        self.launch_tms = QPushButton("Calculate TMS System Mass")
        self.launch_tms.setToolTip("Launch TMS Configurator to Calculate the TMS system mass.")
        self.launch_tms.clicked.connect(self.launch_TMS_configurator)
        self.launch_tms.setEnabled(False)
        self.powertrain_layout.addWidget(self.launch_tms, 4, 2)

        self.powertrain_group.setLayout(self.powertrain_layout)
        grid_layout.addWidget(self.powertrain_group, 1, 1)

    def create_buttons(self, grid_layout):
        button_layout = QGridLayout()

        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.perform_acsizing)
        self.calculate_button.setDisabled(True)
        self.view_aircraft_button = QPushButton("Generate Aircraft Geometry")
        self.view_aircraft_button.clicked.connect(self.view_aircraft)
        self.view_aircraft_button.setDisabled(True)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.calculate_button, 0, 0)
        button_layout.addWidget(self.view_aircraft_button, 0, 1)
        button_layout.addWidget(ok_button, 1, 0)
        button_layout.addWidget(cancel_button, 1, 1)

        grid_layout.addLayout(button_layout, 2, 0, 1, 2)

    def launch_acsizing_settings(self):
        if not self.acsizing_settings:
            self.acsizing_settings = AircraftSizingSettings()
        self.acsizing_settings.show()

    def launch_operational_mode_configurator(self):
        self.get_configuration()
        if not self.operational_mode_configurator:
            self.operational_mode_configurator = OperationModeDialog(self.ac_configuration)
        if self.ac_configuration not in self.operational_mode_configurator.aircraft_configuration:
            self.operational_mode_configurator = OperationModeDialog(self.ac_configuration)
        self.operational_mode_configurator.ok_button.clicked.connect(self.enable_calculate_button)
        self.operational_mode_configurator.show()        

    def get_user_inputs(self):

        for key, item in self.tlars_window.tlar_data.items():
            print("Value for %s is %s" %(key, item))

        for key, item in self.eps_inputs.items():
            print("Value for %s is %s" %(key, item.text()))

        for key, item in self.powertrain_specs_defaults.items():
            print("Value for %s is %s" %(key, item.text()))

        print(self.allow_charging_checkbox.isChecked())
        print(self.advanced_materials_checkbox.isChecked())

    def update_input_fields(self):

        self.calculate_button.setDisabled(True)
        self.operational_mode_configurator = False
        self.tlars_window = None

        current_index = int(self.configuration_selection.currentIndex())
        
        if current_index == 0:
            self.launch_tms.setEnabled(False)
            self.allow_charging_checkbox.setEnabled(False)
            self.allow_charging_checkbox.setChecked(False)
            self.constrain_empty_mass.setChecked(False)
            self.advanced_materials_checkbox.setChecked(False)
            self.launch_gg.setEnabled(False)
            self.launch_gt.setEnabled(True)
            self.powertrain_specs_defaults["Fuel to Total Energy ratio"].setDisabled(True)
            self.powertrain_specs_defaults["Fuel to Total Energy ratio"].setText("1")
            self.powertrain_specs_defaults["Electric to Total Power ratio"].setDisabled(True)
            self.powertrain_specs_defaults["Electric to Total Power ratio"].setText("0")
            self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setDisabled(True)
            self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setText("0")
            self.powertrain_specs_defaults["Gas Generator power output [kW]"].setDisabled(True)
            self.powertrain_specs_defaults["Gas Generator power output [kW]"].setText("0")
            self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(False)
            self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("0")
            for key, item in self.eps_inputs.items():
                item.setEnabled(False)
        elif current_index == 1:
            self.powertrain_specs_defaults["Fuel to Total Energy ratio"].setDisabled(False)
            self.powertrain_specs_defaults["Fuel to Total Energy ratio"].setText("0.8")
            self.powertrain_specs_defaults["Electric to Total Power ratio"].setDisabled(False)
            self.powertrain_specs_defaults["Electric to Total Power ratio"].setText("0.2")
            self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setDisabled(False)
            self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setText("95")
            self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(False)
            self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("20")
            self.launch_tms.setEnabled(True)
            self.launch_gg.setEnabled(False)
            self.launch_gt.setEnabled(True)
            self.powertrain_specs_defaults["Gas Generator power output [kW]"].setDisabled(True)
            self.powertrain_specs_defaults["Gas Generator power output [kW]"].setText("0")
            self.allow_charging_checkbox.setEnabled(False)
            self.allow_charging_checkbox.setChecked(False)
            self.constrain_empty_mass.setChecked(False)
            self.advanced_materials_checkbox.setChecked(False)
            for key, item in self.eps_inputs.items():
                item.setEnabled(True)
        elif current_index == 2:
            self.powertrain_specs_defaults["Fuel to Total Energy ratio"].setDisabled(False)
            self.powertrain_specs_defaults["Fuel to Total Energy ratio"].setText("0.8")
            self.powertrain_specs_defaults["Electric to Total Power ratio"].setDisabled(True)
            self.powertrain_specs_defaults["Electric to Total Power ratio"].setText("0.2")
            self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setDisabled(False)
            self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setText("95")
            self.launch_tms.setEnabled(True)
            self.launch_gt.setEnabled(False)
            self.launch_gg.setEnabled(True)
            self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(True)
            self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("0")
            self.powertrain_specs_defaults["Gas Generator power output [kW]"].setEnabled(True)
            self.powertrain_specs_defaults["Gas Generator power output [kW]"].setText("1600")
            self.allow_charging_checkbox.setEnabled(True)
            self.allow_charging_checkbox.setChecked(False)
            self.constrain_empty_mass.setChecked(False)
            self.advanced_materials_checkbox.setChecked(False)
            for key, item in self.eps_inputs.items():
                item.setEnabled(True)
            self.eps_inputs["Number of electric motors [-]"].setText("4")
        else:
            self.powertrain_specs_defaults["Fuel to Total Energy ratio"].setDisabled(False)
            self.powertrain_specs_defaults["Fuel to Total Energy ratio"].setText("0.8")
            self.powertrain_specs_defaults["Electric to Total Power ratio"].setDisabled(False)
            self.powertrain_specs_defaults["Electric to Total Power ratio"].setText("0.2")
            self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setDisabled(False)
            self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setText("95")
            self.powertrain_specs_defaults["Gas Generator power output [kW]"].setEnabled(True)
            self.powertrain_specs_defaults["Gas Generator power output [kW]"].setText("1600")
            self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(False)
            self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("20")
            self.launch_tms.setEnabled(True)
            self.launch_gt.setEnabled(True)
            self.launch_gg.setEnabled(True)
            self.allow_charging_checkbox.setEnabled(True)
            self.allow_charging_checkbox.setChecked(False)
            self.constrain_empty_mass.setChecked(False)
            self.advanced_materials_checkbox.setChecked(False)
            for key, item in self.eps_inputs.items():
                item.setEnabled(True)

    def get_configuration(self):

        configuration = int(self.configuration_selection.currentIndex())

        if configuration == 0:
            configuration_name = "Conventional"
        elif configuration == 1:
            configuration_name = "Parallel"
        elif configuration == 2:
            configuration_name = "Series"
        elif configuration == 3:
            configuration_name = "Series_Parallel"
        else:
            configuration_name = "Undefined"

        self.ac_configuration = configuration_name

    def override_TMS_default_value(self):
        self.powertrain_specs_defaults["Thermal Management System Mass [kg]"] = QLineEdit(str(round(self.TMS_window.TMS_mass, 2)))
        self.powertrain_layout.addWidget(QLineEdit(str(round(self.TMS_window.TMS_mass, 2))), 3, 1)

    def launch_TLARS(self):
        ### Note to self: you can access the tlars after submitting the form via self.tlars_window.tlar_data
        if not self.tlars_window:
            self.tlars_window = TopLevelAircraftRequirementsForm()
        self.tlars_window.ok_button.clicked.connect(self.enable_calculate_button)
        self.tlars_window.show()
        self.mission_button.setEnabled(True)        

    def launch_TMS_configurator(self):
        if not self.TMS_window:
            self.TMS_window = TMSConfigApp()
        self.TMS_window.confirm_button.clicked.connect(self.override_TMS_default_value)
        self.TMS_window.show()

    def launch_GG_configurator(self):
        if not self.nested_GG_window:
            self.nested_GG_window = NestedGGlauncher()
        self.nested_GG_window.show()        

    def launch_GT_configurator(self):
        if not self.nested_GT_window:
            self.nested_GT_window = NestedGTlauncher()
        self.nested_GT_window.show()

    def launch_prop_configurator(self):
        if not self.nested_prop_window:
            self.nested_prop_window = NestedProplauncher()
        self.nested_prop_window.show()

    def show_aircraft_configuration(self):

        configuration = int(self.configuration_selection.currentIndex())

        if configuration == 0:
            config_path = "Conventional_p.png"
        elif configuration == 1:
            config_path = "Parallel_p.png"
        elif configuration == 2:
            config_path = "Series_p.png"
        elif configuration == 3:
            config_path = "Series_Parallel_p.png"
        else:
            config_path = None

        self.image_viewer = ImageViewer(os.path.join(os.getcwd(), "img", config_path))
        self.image_viewer.show()

    def plot_mission_profile(self):

        os.chdir(self.output_dir)
        self.define_target_mission()
        self.target_mission.plot_misison_profile(True)

        os.chdir(self.home_dir)

    def view_aircraft(self):
        os.chdir(self.output_dir)
        build_aircraft("vsp_aircraft_input_file")
        vsp.ClearVSPModel()
        os.chdir(self.home_dir)
        launch_openvsp(os.path.join(self.output_dir, "Assembly.vsp3"))

    def perform_acsizing(self):

        os.chdir(self.output_dir)

        self.view_aircraft_button.setEnabled(True)
        
        self.define_target_mission()

        configuration = int(self.configuration_selection.currentIndex())

        if configuration == 2:
            nested_gasturbine = self.nested_GG_window
        else:
            nested_gasturbine = self.nested_GT_window
        
        total_mission_time = 0
        for key, item in self.target_mission.timetable.items():
            total_mission_time = total_mission_time + item

        if not self.acsizing_settings:
            self.acsizing_settings = AircraftSizingSettings()

        propeller = Propeller(self.nested_prop_window)
        eps = EPS(self.eps_inputs)
        propulsion = Propulsion(self.powertrain_specs_defaults, eps, propeller, nested_gasturbine)
        settings = Settings(int(self.configuration_selection.currentIndex()), bool(self.advanced_materials_checkbox.isChecked()),
                            bool(self.allow_charging_checkbox.isChecked()), bool(self.constrain_empty_mass.isChecked()), self.operational_mode_configurator,
                            self.acsizing_settings.settings)
        acsizing = aircraft_sizing_wrapper(self)
        acsizing.run_acsizing_wrapper(self.target_mission, propulsion, settings, self.tlars_window.tlar_data)

        message = f"Calculation completed. Outputs exported to:\n{os.getcwd()}"
        QMessageBox.information(self, "Calculation Completed", message, QMessageBox.Ok)

        os.chdir(self.home_dir)

    def define_target_mission(self):

        mission_range = float(self.tlars_window.tlar_data["Mission range [nm]"])*1852 # nmi to m
        mission_reserves = float(self.tlars_window.tlar_data["Reserves range [nm]"])*1852 # nmi to m
        loiter_alt = float(self.tlars_window.tlar_data["Loiter Altitude [ft]"])*0.3048
        end_takeoff = float(self.tlars_window.tlar_data["End of Take-Off Altitude [ft]"])*0.3048
        loiter_mach = float(self.tlars_window.tlar_data["Loiter Mach Number [-]"])
        max_cl_angle = float(self.tlars_window.tlar_data["Max Climb Angle [deg]"])
        max_d_angle = float(self.tlars_window.tlar_data["Max Dive Angle [deg]"])
        cruise_alt = float(self.tlars_window.tlar_data["Cruise Altitude [ft]"])*0.3048
        reserves_alt = float(self.tlars_window.tlar_data["Diversion Altitude [ft]"])*0.3048
        climb_alt_60 = cruise_alt*0.6
        cruise_mach = float(self.tlars_window.tlar_data["Cruise Mach Number [-]"])
        climb_mach = float(self.tlars_window.tlar_data["Climb Mach Number [-]"])
        climb_angle = float(self.tlars_window.tlar_data["Target Climb Angle [deg]"])
        dive_angle = -float(self.tlars_window.tlar_data["Target Dive Angle [deg]"])
        
        self.target_mission = mission_profile()
        self.target_mission.load_mission_inputs(climb_alt_60, climb_mach, cruise_alt, cruise_mach,
                            loiter_alt, loiter_mach, reserves_alt, mission_range, mission_reserves, end_takeoff, 
                            max_cl_angle, max_d_angle, climb_angle, dive_angle)
        self.target_mission.define_mision()
        self.target_mission.build_mission()

        self.mission_calculated = True

    def enable_calculate_button(self):
        flag_1 = False
        flag_2 = False

        if self.operational_mode_configurator:
            if len(self.operational_mode_configurator.el_mode) != 0 or len(self.operational_mode_configurator.conv_mode) != 0:
                flag_1 = True

        if self.tlars_window:
            if len(self.tlars_window.tlar_data) > 0:
                flag_2 = True

        if flag_1 and flag_2:
            self.calculate_button.setEnabled(True)

class ImageViewer(QWidget):
    def __init__(self, image_path, resolution = "wide"):
        super().__init__()

        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        image_label = QLabel()
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            raise ValueError("Image not found. Check original installation folder path ./img/...")
        if resolution == "wide":
            image_label.setPixmap(pixmap.scaled(1280, 720))
        else:
            image_label.setPixmap(pixmap.scaled(960, 720))
        image_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(image_label)

        self.setLayout(layout)

class Propulsion(object):
    def __init__(self, powertrain_specs, eps, propeller, gt_from_GUI):
        self.powertrain_specs = powertrain_specs
        self.eps = eps
        self.propeller = propeller
        self.gt_from_GUI = gt_from_GUI

class EPS(object):
    def __init__(self, eps_inputs):
        self.eps_inputs = eps_inputs

class Propeller(object):
    def __init__(self, opened_GUI):
        if opened_GUI:
            self.efficiency = opened_GUI.eta_p_inputs_GUI
        else:
            self.efficiency = {
                                'Taxi-out' : 0.8,
                                'Take-off' : 0.8,
                                'Climb' : 0.77,
                                'Cruise' : 0.78,
                                'Descent' : 0.8,
                                'Approach and Landing' : 0.66,
                                'Taxi-in' : 0.8,
                                'Overshoot' : 0.8,
                                'DivClimb' : 0.77,
                                'DivCruise' : 0.78,
                                'DivDescent' : 0.8,
                                'Hold' : 0.66,
                                'Div Approach and Landing' : 0.66,
                                }

class Settings(object):
    def __init__(self, configuration, advanced_materials, allow_charging, constrain_OEM, operational_modes, advanced_settings):
        
        if configuration == 0:
            configuration_name = "Conventional"
        elif configuration == 1:
            configuration_name = "Parallel"
        elif configuration == 2:
            configuration_name = "Series"
        elif configuration == 3:
            configuration_name = "Series_Parallel"
        else:
            configuration_name = "Undefined"

        self.configuration = configuration_name
        self.advanced_materials = advanced_materials
        self.allow_charging = allow_charging
        self.el_mode = operational_modes.el_mode
        self.conv_mode = operational_modes.conv_mode
        self.advanced_settings = advanced_settings
        self.constrain_OEM = constrain_OEM

class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Loading...")
        self.progress_bar = QProgressBar(self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.progress_bar)
        self.setLayout(self.layout)


def main():
    app = QApplication(sys.argv)
    dialog = AircraftSizingDialog()
    result = dialog.exec_()
    sys.exit(result)

if __name__ == "__main__":
    main()
