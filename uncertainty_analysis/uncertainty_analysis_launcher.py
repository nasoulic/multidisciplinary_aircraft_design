import sys, os
from PyQt5.QtWidgets import (QApplication, QDialog, QGridLayout, QWidget, QPushButton,
                             QGroupBox, QCheckBox, QLabel, QLineEdit, QComboBox,
                             QVBoxLayout, QProgressBar, QMessageBox, QFileDialog)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from tlars.tlars import TopLevelAircraftRequirementsForm
from acsizing.operating_modes_launcher import OperationModeDialog
from acsizing.acsizing_settings import AircraftSizingSettings
from acsizing.nested_gt_launcher import NestedGTlauncher
from acsizing.nested_gg_launcher import NestedGGlauncher
from acsizing.nested_propeller_launcher import NestedProplauncher
from tms.tms_modeler_launcher import TMSConfigApp
from acsizing.mission_profile import mission_profile
from acsizing.acsizing_wrapper import aircraft_sizing_wrapper
from doc.doc_launcher import AircraftCostCalculator
from lca.lca_launcher import AircraftLifeCycleEval
from acsizing.centre_of_mass_wrapper import getCoG
from acsizing.static_margin_wrapper import getStaticMargin
from acsizing.trim_analysis_wrapper import trimAnalysisWrapper
from aircraft_visualization.launch_openvsp import launch_openvsp
from aircraft_visualization.create_aircraft import build_aircraft
import openvsp as vsp

class UncertaintyAnalysisDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.run = 0

        self.home_dir = os.getcwd()
        self.navigate2path(['results', "uncertainty_analysis", "resultsRun_{0}".format(self.run)])
        self.output_dir = os.getcwd()
        os.chdir(self.home_dir)

        self.setWindowTitle("Uncertainty Analysis")
        self.setGeometry(100, 100, 800, 600)

        self.tlars_window = None                        # Reference to TLARs instance
        self.TMS_window = None                          # Reference to TMS instance
        self.nested_GT_window = None                    # Reference to nested GT instance
        self.nested_prop_window = None                  # Reference to nested propeller instance
        self.mission_calculated = False                 # Reference to Plot Mission button
        self.operational_mode_configurator = False      # Reference to Set Operational Modes button
        self.acsizing_settings = None                   # Reference to acsizing advanced settings
        self.doc_window = None                          # Reference to doc manu
        self.lca_window = None                          # Reference to lca menu
        self.nested_GG_window = None                    # Reference to nested GG instance

        grid_layout = QGridLayout(self)
        self.create_tlars_group(grid_layout)
        self.create_eps_inputs_group(grid_layout)
        self.create_checkboxes_group(grid_layout)
        self.create_powertrain_group(grid_layout)
        self.create_additional_disciplines(grid_layout)
        self.create_uncertainty_analysis_group(grid_layout)
        self.create_buttons(grid_layout)

    def create_uncertainty_analysis_group(self, grid_layout):
        
        uncertainty_analysis_group = QGroupBox("Uncertainty Analysis Setup")
        uncertainty_analysis_group_layout = QGridLayout()

        uncertainty_analysis_group_layout.addWidget(QLabel("Evaluation method"), 0, 0)

        # Add dropdown menu with Monte Carlo Simulation option only
        self.method_selection = QComboBox()
        self.method_selection.addItems(["Monte Carlo Simulation", "More..."])
        self.method_selection.setCurrentIndex(0)
        uncertainty_analysis_group_layout.addWidget(self.method_selection, 0, 1)

        uncertainty_analysis_group_layout.addWidget(QLabel("Number of samples"), 1, 0)
        self.mc_nsamples = QLineEdit("100")
        uncertainty_analysis_group_layout.addWidget(self.mc_nsamples, 1, 1)

        uncertainty_analysis_group.setLayout(uncertainty_analysis_group_layout)
        grid_layout.addWidget(uncertainty_analysis_group, 2, 1)

    def create_additional_disciplines(self, grid_layout):

        additional_disciplines_group = QGroupBox("Additional Disciplines")
        additional_disciplines_group_layout = QGridLayout()

        self.include_doc = QCheckBox("Enable Direct Operating Cost Calculation")
        self.include_doc.stateChanged.connect(self.on_state_changed_doc)
        self.include_lca = QCheckBox("Enable Life Cycle Assessment Calculation")
        self.include_lca.stateChanged.connect(self.on_state_changed_lca)
        self.include_stability = QCheckBox("Check Aircraft Stability")
        self.include_stability.stateChanged.connect(self.on_state_changed_stability)
        self.include_trim = QCheckBox("Aircraft Trim Analysis")
        self.include_trim.stateChanged.connect(self.on_state_changed_trim)

        self.configure_DOC = QPushButton("Configure DOC Inputs")
        self.configure_DOC.setEnabled(False)
        self.configure_DOC.clicked.connect(self.launch_doc_inputs)
        self.configure_LCA = QPushButton("Configure LCA Inputs")
        self.configure_LCA.setEnabled(False)
        self.configure_LCA.clicked.connect(self.launch_lca_inputs)
        self.configure_stability = QLineEdit("7")
        self.configure_stability.setEnabled(False)
        self.configure_trim_angle = QLineEdit("0")
        self.configure_trim_angle.setEnabled(False)
        self.configure_trim_elevator = QLineEdit("0")
        self.configure_trim_elevator.setEnabled(False)

        additional_disciplines_group_layout.addWidget(self.configure_DOC, 0, 1)
        additional_disciplines_group_layout.addWidget(self.include_doc, 0, 0)
        additional_disciplines_group_layout.addWidget(self.include_lca, 1, 0)
        additional_disciplines_group_layout.addWidget(self.configure_LCA, 1, 1)
        additional_disciplines_group_layout.addWidget(QLabel("Static Margin [%]"), 2, 1)
        additional_disciplines_group_layout.addWidget(self.include_stability, 2, 0)
        additional_disciplines_group_layout.addWidget(self.configure_stability, 2, 2)
        additional_disciplines_group_layout.addWidget(QLabel("Aircraft Mission Angle [deg]"), 4, 1)
        additional_disciplines_group_layout.addWidget(self.include_trim, 4, 0)
        additional_disciplines_group_layout.addWidget(self.configure_trim_angle, 5, 1)
        additional_disciplines_group_layout.addWidget(QLabel("Aircraft Elevator Deflection [deg]"), 4, 2)
        additional_disciplines_group_layout.addWidget(self.configure_trim_elevator, 5, 2)

        additional_disciplines_group.setLayout(additional_disciplines_group_layout)
        grid_layout.addWidget(additional_disciplines_group, 2, 0)


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

        self.eps_inputs_lb = {
            "Battery specific energy [kWh/kg]"  : QLineEdit("0.55"),
            "Battery specific power [kW/kg]"    : QLineEdit("0.55"),
            "Specific power (electronics) [kW/kg]": QLineEdit("15"),
            "Specific power (motors) [kW/kg]": QLineEdit("8"),
            "Number of electric motors [-]" : QLineEdit(""),
            "Electric motor revolutions per min [rpm]": QLineEdit(""),
            "Battery to shaft efficiency [%]": QLineEdit("90"),
            "System voltage [V]": QLineEdit("1190"),
            "Depth of discharge [%]": QLineEdit("78"),
            "Battery EOL State of Charge [%]": QLineEdit("78"),
            # Add more inputs as needed
        }

        self.eps_inputs_ub = {
            "Battery specific energy [kWh/kg]"  : QLineEdit("0.75"),
            "Battery specific power [kW/kg]"    : QLineEdit("0.75"),
            "Specific power (electronics) [kW/kg]": QLineEdit("20"),
            "Specific power (motors) [kW/kg]": QLineEdit("12"),
            "Number of electric motors [-]" : QLineEdit(""),
            "Electric motor revolutions per min [rpm]": QLineEdit(""),
            "Battery to shaft efficiency [%]": QLineEdit("95"),
            "System voltage [V]": QLineEdit("1210"),
            "Depth of discharge [%]": QLineEdit("82"),
            "Battery EOL State of Charge [%]": QLineEdit("82"),
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

        eps_inputs_layout.addWidget(QLabel("Nominal Value"), 0, 1)
        eps_inputs_layout.addWidget(QLabel("Lower Bound"), 0, 2)
        eps_inputs_layout.addWidget(QLabel("Upper Bound"), 0, 3)

        row = 1
        for key, input_widget in self.eps_inputs.items():
            eps_inputs_layout.addWidget(QLabel(key), row, 0)
            input_widget.setToolTip(eps_tooltip_data[key])
            input_widget.setEnabled(False)
            self.eps_inputs_lb[key].setEnabled(False)
            self.eps_inputs_ub[key].setEnabled(False)
            eps_inputs_layout.addWidget(input_widget, row, 1)
            eps_inputs_layout.addWidget(self.eps_inputs_lb[key], row, 2)
            eps_inputs_layout.addWidget(self.eps_inputs_ub[key], row, 3)
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

        self.powertrain_specs_defaults_lb = {
            "Fuel to Total Energy ratio" : QLineEdit("0.7"),
            "Electric to Total Power ratio" : QLineEdit("0.1"),
            "Gas Generator power output [kW]" : QLineEdit("1600"),
            "Gas Turbine SFC reduction compared to EIS 2014 [%]" : QLineEdit("15"),
            "Thermal Management System Mass [kg]" : QLineEdit("50"),
        }

        self.powertrain_specs_defaults_ub = {
            "Fuel to Total Energy ratio" : QLineEdit("0.9"),
            "Electric to Total Power ratio" : QLineEdit("0.3"),
            "Gas Generator power output [kW]" : QLineEdit("1600"),
            "Gas Turbine SFC reduction compared to EIS 2014 [%]" : QLineEdit("25"),
            "Thermal Management System Mass [kg]" : QLineEdit("150"),
        }

        self.powertrain_layout.addWidget(QLabel("Nominal Value"), 0, 1)
        self.powertrain_layout.addWidget(QLabel("Lower Bound"), 0, 2)
        self.powertrain_layout.addWidget(QLabel("Upper Bound"), 0, 3)

        i = 1
        for key, item in self.powertrain_specs_defaults.items():
            self.powertrain_layout.addWidget(QLabel(key), i, 0)
            self.powertrain_layout.addWidget(item, i, 1)
            self.powertrain_layout.addWidget(self.powertrain_specs_defaults_lb[key], i, 2)
            self.powertrain_layout.addWidget(self.powertrain_specs_defaults_ub[key], i, 3)
            i += 1

        self.powertrain_specs_defaults["Fuel to Total Energy ratio"].setDisabled(True)
        self.powertrain_specs_defaults["Fuel to Total Energy ratio"].setText("1")
        self.powertrain_specs_defaults_lb["Fuel to Total Energy ratio"].setDisabled(True)
        self.powertrain_specs_defaults_lb["Fuel to Total Energy ratio"].setText("1")
        self.powertrain_specs_defaults_ub["Fuel to Total Energy ratio"].setDisabled(True)
        self.powertrain_specs_defaults_ub["Fuel to Total Energy ratio"].setText("1")
        self.powertrain_specs_defaults["Electric to Total Power ratio"].setDisabled(True)
        self.powertrain_specs_defaults["Electric to Total Power ratio"].setText("0")
        self.powertrain_specs_defaults_lb["Electric to Total Power ratio"].setDisabled(True)
        self.powertrain_specs_defaults_lb["Electric to Total Power ratio"].setText("0")
        self.powertrain_specs_defaults_ub["Electric to Total Power ratio"].setDisabled(True)
        self.powertrain_specs_defaults_ub["Electric to Total Power ratio"].setText("0")
        self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setDisabled(True)
        self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setText("0")
        self.powertrain_specs_defaults_lb["Thermal Management System Mass [kg]"].setDisabled(True)
        self.powertrain_specs_defaults_lb["Thermal Management System Mass [kg]"].setText("0")
        self.powertrain_specs_defaults_ub["Thermal Management System Mass [kg]"].setDisabled(True)
        self.powertrain_specs_defaults_ub["Thermal Management System Mass [kg]"].setText("0")
        self.powertrain_specs_defaults["Gas Generator power output [kW]"].setDisabled(True)
        self.powertrain_specs_defaults["Gas Generator power output [kW]"].setText("0")
        self.powertrain_specs_defaults_lb["Gas Generator power output [kW]"].setDisabled(True)
        self.powertrain_specs_defaults_lb["Gas Generator power output [kW]"].setText("0")
        self.powertrain_specs_defaults_ub["Gas Generator power output [kW]"].setDisabled(True)
        self.powertrain_specs_defaults_ub["Gas Generator power output [kW]"].setText("0")
        self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(False)
        self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("0")
        self.powertrain_specs_defaults_lb["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(False)
        self.powertrain_specs_defaults_lb["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("0")
        self.powertrain_specs_defaults_ub["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(False)
        self.powertrain_specs_defaults_ub["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("0")

        self.launch_gg = QPushButton("Configure Gas Generator")
        self.launch_gg.setToolTip("Launch the Gas Generator Configurator.")
        self.launch_gg.clicked.connect(self.launch_GG_configurator)
        self.launch_gg.setEnabled(False)
        self.powertrain_layout.addWidget(self.launch_gg, 3, 4)
        
        self.launch_gt = QPushButton("Configure EIS 2014 GT")
        self.launch_gt.setToolTip("Launch the GT Configurator.")
        self.launch_gt.clicked.connect(self.launch_GT_configurator)
        self.powertrain_layout.addWidget(self.launch_gt, 4, 4)

        self.launch_prop = QPushButton("Configure Propeller")
        self.launch_prop.setToolTip("Launch the propeller efficiency configurator.")
        self.launch_prop.clicked.connect(self.launch_prop_configurator)
        self.powertrain_layout.addWidget(self.launch_prop, 4, 5)

        self.launch_tms = QPushButton("Calculate TMS System Mass")
        self.launch_tms.setToolTip("Launch TMS Configurator to Calculate the TMS system mass.")
        self.launch_tms.clicked.connect(self.launch_TMS_configurator)
        self.launch_tms.setEnabled(False)
        self.powertrain_layout.addWidget(self.launch_tms, 5, 4)

        self.powertrain_group.setLayout(self.powertrain_layout)
        grid_layout.addWidget(self.powertrain_group, 1, 1)

    def create_buttons(self, grid_layout):
        button_layout = QGridLayout()

        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.perform_uncertainty_analysis)
        self.calculate_button.setDisabled(True)
        self.view_aircraft_button = QPushButton("Generate Aircraft Geometry")
        self.view_aircraft_button.clicked.connect(self.view_aircraft)
        self.view_aircraft_button.setDisabled(True)

        button_layout.addWidget(self.calculate_button, 0, 0)
        button_layout.addWidget(self.view_aircraft_button, 0, 1)

        grid_layout.addLayout(button_layout, 3, 0, 1, 2)

    def on_state_changed_doc(self):
        if self.include_doc.isChecked():
            self.configure_DOC.setEnabled(True)
        else:
            self.configure_DOC.setEnabled(False)

    def on_state_changed_lca(self):
        if self.include_lca.isChecked():
            self.configure_LCA.setEnabled(True)
        else:
            self.configure_LCA.setEnabled(False)

    def launch_doc_inputs(self):
        self.navigate2path(['results', "uncertainty_analysis", "resultsRun_{0}".format(self.run)])
        if not self.doc_window:
            self.doc_window = AircraftCostCalculator(self.home_dir, os.getcwd())
            self.doc_window.calculate_button.setDisabled(True)
        self.doc_window.show()
        os.chdir(self.home_dir)

    def on_state_changed_trim(self):
        if self.include_trim.isChecked():
            self.configure_trim_angle.setEnabled(True)
            self.configure_trim_elevator.setEnabled(True)
        else:
            self.configure_trim_angle.setEnabled(False)
            self.configure_trim_elevator.setEnabled(False)

    def on_state_changed_stability(self):
        if self.include_stability.isChecked():
            self.configure_stability.setEnabled(True)
        else:
            self.configure_stability.setEnabled(False)

    def launch_lca_inputs(self):
        self.navigate2path(['results', "uncertainty_analysis", "resultsRun_{0}".format(self.run)])
        if not self.lca_window:
            self.lca_window = AircraftLifeCycleEval(self.home_dir, os.getcwd())
            self.lca_window.calculate_button.setDisabled(True)
        self.lca_window.show()
        os.chdir(self.home_dir)

    def launch_TLARS(self):
        ### Note to self: you can access the tlars after submitting the form via self.tlars_window.tlar_data
        if not self.tlars_window:
            self.tlars_window = TopLevelAircraftRequirementsForm()
        self.tlars_window.ok_button.clicked.connect(self.enable_calculate_button)
        self.tlars_window.show()
        self.mission_button.setEnabled(True)

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

    def plot_mission_profile(self):

        self.navigate2path(['results', "uncertainty_analysis", "resultsRun_{0}".format(self.run)])

        self.define_target_mission()
        self.target_mission.plot_misison_profile(True)

        os.chdir(self.home_dir)

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
            self.powertrain_specs_defaults_lb["Fuel to Total Energy ratio"].setDisabled(True)
            self.powertrain_specs_defaults_lb["Fuel to Total Energy ratio"].setText("1")
            self.powertrain_specs_defaults_ub["Fuel to Total Energy ratio"].setDisabled(True)
            self.powertrain_specs_defaults_ub["Fuel to Total Energy ratio"].setText("1")
            self.powertrain_specs_defaults["Electric to Total Power ratio"].setDisabled(True)
            self.powertrain_specs_defaults["Electric to Total Power ratio"].setText("0")
            self.powertrain_specs_defaults_lb["Electric to Total Power ratio"].setDisabled(True)
            self.powertrain_specs_defaults_lb["Electric to Total Power ratio"].setText("0")
            self.powertrain_specs_defaults_ub["Electric to Total Power ratio"].setDisabled(True)
            self.powertrain_specs_defaults_ub["Electric to Total Power ratio"].setText("0")
            self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setDisabled(True)
            self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setText("0")
            self.powertrain_specs_defaults_lb["Thermal Management System Mass [kg]"].setDisabled(True)
            self.powertrain_specs_defaults_lb["Thermal Management System Mass [kg]"].setText("0")
            self.powertrain_specs_defaults_ub["Thermal Management System Mass [kg]"].setDisabled(True)
            self.powertrain_specs_defaults_ub["Thermal Management System Mass [kg]"].setText("0")
            self.powertrain_specs_defaults["Gas Generator power output [kW]"].setDisabled(True)
            self.powertrain_specs_defaults["Gas Generator power output [kW]"].setText("0")
            self.powertrain_specs_defaults_lb["Gas Generator power output [kW]"].setDisabled(True)
            self.powertrain_specs_defaults_lb["Gas Generator power output [kW]"].setText("0")
            self.powertrain_specs_defaults_ub["Gas Generator power output [kW]"].setDisabled(True)
            self.powertrain_specs_defaults_ub["Gas Generator power output [kW]"].setText("0")
            self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(False)
            self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("0")
            self.powertrain_specs_defaults_lb["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(False)
            self.powertrain_specs_defaults_lb["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("0")
            self.powertrain_specs_defaults_ub["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(False)
            self.powertrain_specs_defaults_ub["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("0")
            for key, item in self.eps_inputs.items():
                item.setEnabled(False)
                self.eps_inputs_lb[key].setEnabled(False)
                self.eps_inputs_ub[key].setEnabled(False)
        elif current_index == 1:
            self.powertrain_specs_defaults["Fuel to Total Energy ratio"].setDisabled(False)
            self.powertrain_specs_defaults["Fuel to Total Energy ratio"].setText("0.8")
            self.powertrain_specs_defaults_lb["Fuel to Total Energy ratio"].setDisabled(False)
            self.powertrain_specs_defaults_lb["Fuel to Total Energy ratio"].setText("0.75")
            self.powertrain_specs_defaults_ub["Fuel to Total Energy ratio"].setDisabled(False)
            self.powertrain_specs_defaults_ub["Fuel to Total Energy ratio"].setText("0.85")
            self.powertrain_specs_defaults["Electric to Total Power ratio"].setDisabled(False)
            self.powertrain_specs_defaults["Electric to Total Power ratio"].setText("0.2")
            self.powertrain_specs_defaults_lb["Electric to Total Power ratio"].setDisabled(False)
            self.powertrain_specs_defaults_lb["Electric to Total Power ratio"].setText("0.15")
            self.powertrain_specs_defaults_ub["Electric to Total Power ratio"].setDisabled(False)
            self.powertrain_specs_defaults_ub["Electric to Total Power ratio"].setText("0.25")
            self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setDisabled(False)
            self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setText("95")
            self.powertrain_specs_defaults_lb["Thermal Management System Mass [kg]"].setDisabled(False)
            self.powertrain_specs_defaults_lb["Thermal Management System Mass [kg]"].setText("50")
            self.powertrain_specs_defaults_ub["Thermal Management System Mass [kg]"].setDisabled(False)
            self.powertrain_specs_defaults_ub["Thermal Management System Mass [kg]"].setText("150")
            self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(False)
            self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("20")
            self.powertrain_specs_defaults_lb["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(False)
            self.powertrain_specs_defaults_lb["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("15")
            self.powertrain_specs_defaults_ub["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(False)
            self.powertrain_specs_defaults_ub["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("25")
            self.launch_tms.setEnabled(True)
            self.launch_gg.setEnabled(False)
            self.launch_gt.setEnabled(True)
            self.powertrain_specs_defaults["Gas Generator power output [kW]"].setDisabled(True)
            self.powertrain_specs_defaults["Gas Generator power output [kW]"].setText("0")
            self.powertrain_specs_defaults_lb["Gas Generator power output [kW]"].setDisabled(True)
            self.powertrain_specs_defaults_lb["Gas Generator power output [kW]"].setText("0")
            self.powertrain_specs_defaults_lb["Gas Generator power output [kW]"].setDisabled(True)
            self.powertrain_specs_defaults_lb["Gas Generator power output [kW]"].setText("0")
            self.allow_charging_checkbox.setEnabled(False)
            self.allow_charging_checkbox.setChecked(False)
            self.constrain_empty_mass.setChecked(False)
            self.advanced_materials_checkbox.setChecked(False)
            for key, item in self.eps_inputs.items():
                item.setEnabled(True)
                if key != "Number of electric motors [-]" and key != "Electric motor revolutions per min [rpm]":
                    self.eps_inputs_lb[key].setEnabled(True)
                    self.eps_inputs_ub[key].setEnabled(True)
        elif current_index == 2:
            self.powertrain_specs_defaults["Fuel to Total Energy ratio"].setDisabled(False)
            self.powertrain_specs_defaults["Fuel to Total Energy ratio"].setText("0.8")
            self.powertrain_specs_defaults_lb["Fuel to Total Energy ratio"].setDisabled(False)
            self.powertrain_specs_defaults_lb["Fuel to Total Energy ratio"].setText("0.75")
            self.powertrain_specs_defaults_ub["Fuel to Total Energy ratio"].setDisabled(False)
            self.powertrain_specs_defaults_ub["Fuel to Total Energy ratio"].setText("0.85")
            self.powertrain_specs_defaults["Electric to Total Power ratio"].setDisabled(True)
            self.powertrain_specs_defaults["Electric to Total Power ratio"].setText("0.2")
            self.powertrain_specs_defaults_lb["Electric to Total Power ratio"].setDisabled(True)
            self.powertrain_specs_defaults_lb["Electric to Total Power ratio"].setText("0.2")
            self.powertrain_specs_defaults_ub["Electric to Total Power ratio"].setDisabled(True)
            self.powertrain_specs_defaults_ub["Electric to Total Power ratio"].setText("0.2")
            self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setDisabled(False)
            self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setText("95")
            self.powertrain_specs_defaults_lb["Thermal Management System Mass [kg]"].setDisabled(False)
            self.powertrain_specs_defaults_lb["Thermal Management System Mass [kg]"].setText("50")
            self.powertrain_specs_defaults_ub["Thermal Management System Mass [kg]"].setDisabled(False)
            self.powertrain_specs_defaults_ub["Thermal Management System Mass [kg]"].setText("150")
            self.launch_tms.setEnabled(True)
            self.launch_gt.setEnabled(False)
            self.launch_gg.setEnabled(True)
            self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(True)
            self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("0")
            self.powertrain_specs_defaults_lb["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(True)
            self.powertrain_specs_defaults_lb["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("0")
            self.powertrain_specs_defaults_ub["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(True)
            self.powertrain_specs_defaults_ub["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("0")
            self.powertrain_specs_defaults["Gas Generator power output [kW]"].setEnabled(True)
            self.powertrain_specs_defaults["Gas Generator power output [kW]"].setText("1600")
            self.powertrain_specs_defaults_lb["Gas Generator power output [kW]"].setEnabled(False)
            self.powertrain_specs_defaults_lb["Gas Generator power output [kW]"].setText("1600")
            self.powertrain_specs_defaults_ub["Gas Generator power output [kW]"].setEnabled(False)
            self.powertrain_specs_defaults_ub["Gas Generator power output [kW]"].setText("1600")
            self.allow_charging_checkbox.setEnabled(True)
            self.allow_charging_checkbox.setChecked(False)
            self.constrain_empty_mass.setChecked(False)
            self.advanced_materials_checkbox.setChecked(False)
            for key, item in self.eps_inputs.items():
                item.setEnabled(True)
                if key != "Number of electric motors [-]" and key != "Electric motor revolutions per min [rpm]":
                    self.eps_inputs_lb[key].setEnabled(True)
                    self.eps_inputs_ub[key].setEnabled(True)
        else:
            self.powertrain_specs_defaults["Fuel to Total Energy ratio"].setDisabled(False)
            self.powertrain_specs_defaults["Fuel to Total Energy ratio"].setText("0.8")
            self.powertrain_specs_defaults_lb["Fuel to Total Energy ratio"].setDisabled(False)
            self.powertrain_specs_defaults_lb["Fuel to Total Energy ratio"].setText("0.75")
            self.powertrain_specs_defaults_ub["Fuel to Total Energy ratio"].setDisabled(False)
            self.powertrain_specs_defaults_ub["Fuel to Total Energy ratio"].setText("0.85")
            self.powertrain_specs_defaults["Electric to Total Power ratio"].setDisabled(False)
            self.powertrain_specs_defaults["Electric to Total Power ratio"].setText("0.2")
            self.powertrain_specs_defaults_lb["Electric to Total Power ratio"].setDisabled(False)
            self.powertrain_specs_defaults_lb["Electric to Total Power ratio"].setText("0.15")
            self.powertrain_specs_defaults_ub["Electric to Total Power ratio"].setDisabled(False)
            self.powertrain_specs_defaults_ub["Electric to Total Power ratio"].setText("0.25")
            self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setDisabled(False)
            self.powertrain_specs_defaults["Thermal Management System Mass [kg]"].setText("95")
            self.powertrain_specs_defaults_lb["Thermal Management System Mass [kg]"].setDisabled(False)
            self.powertrain_specs_defaults_lb["Thermal Management System Mass [kg]"].setText("50")
            self.powertrain_specs_defaults_ub["Thermal Management System Mass [kg]"].setDisabled(False)
            self.powertrain_specs_defaults_ub["Thermal Management System Mass [kg]"].setText("150")
            self.powertrain_specs_defaults["Gas Generator power output [kW]"].setEnabled(True)
            self.powertrain_specs_defaults["Gas Generator power output [kW]"].setText("1600")
            self.powertrain_specs_defaults_lb["Gas Generator power output [kW]"].setEnabled(False)
            self.powertrain_specs_defaults_lb["Gas Generator power output [kW]"].setText("1600")
            self.powertrain_specs_defaults_ub["Gas Generator power output [kW]"].setEnabled(False)
            self.powertrain_specs_defaults_ub["Gas Generator power output [kW]"].setText("1600")
            self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(False)
            self.powertrain_specs_defaults["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("20")
            self.powertrain_specs_defaults_lb["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(False)
            self.powertrain_specs_defaults_lb["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("20")
            self.powertrain_specs_defaults_ub["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setDisabled(False)
            self.powertrain_specs_defaults_ub["Gas Turbine SFC reduction compared to EIS 2014 [%]"].setText("20")
            self.launch_tms.setEnabled(True)
            self.launch_gt.setEnabled(True)
            self.launch_gg.setEnabled(True)
            self.allow_charging_checkbox.setEnabled(True)
            self.allow_charging_checkbox.setChecked(False)
            self.constrain_empty_mass.setChecked(False)
            self.advanced_materials_checkbox.setChecked(False)
            for key, item in self.eps_inputs.items():
                item.setEnabled(True)
                if key != "Number of electric motors [-]" and key != "Electric motor revolutions per min [rpm]":
                    self.eps_inputs_lb[key].setEnabled(True)
                    self.eps_inputs_ub[key].setEnabled(True)

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
            config_path = "Undefined"

        self.image_viewer = ImageViewer(os.path.join(os.getcwd(), "img", config_path))
        self.image_viewer.show()

    def launch_operational_mode_configurator(self):
        self.get_configuration()
        if not self.operational_mode_configurator:
            self.operational_mode_configurator = OperationModeDialog(self.ac_configuration)
        if self.ac_configuration not in self.operational_mode_configurator.aircraft_configuration:
            self.operational_mode_configurator = OperationModeDialog(self.ac_configuration)
        self.operational_mode_configurator.ok_button.clicked.connect(self.enable_calculate_button)
        self.operational_mode_configurator.show()

    def launch_acsizing_settings(self):
        if not self.acsizing_settings:
            self.acsizing_settings = AircraftSizingSettings()
        self.acsizing_settings.show()

    def launch_TMS_configurator(self):
        self.navigate2path(['results', "uncertainty_analysis", "resultsRun_{0}".format(self.run)])
        if not self.TMS_window:
            self.TMS_window = TMSConfigApp(self.home_dir, os.getcwd())
        self.TMS_window.confirm_button.clicked.connect(self.override_TMS_default_value)
        self.TMS_window.show()
        os.chdir(self.home_dir)

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

    def view_aircraft(self):
        self.navigate2path(['results', "uncertainty_analysis", "resultsRun_{0}".format(self.run - 1)])
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Open VSP Input File", "", "dat files (*.dat);;All Files (*)", options=options)
        if file_name:
            path_comp = file_name.split("/")
            new_path = "/".join(path_comp[:-1])
            os.chdir(new_path)
            build_aircraft(file_name.replace(".dat", ""), self.ac_configuration)
            vsp.ClearVSPModel()
            os.chdir(self.home_dir)
            launch_openvsp(os.path.join(new_path, "Assembly.vsp3"))

    def override_TMS_default_value(self):
        self.powertrain_specs_defaults["Thermal Management System Mass [kg]"] = QLineEdit(str(round(self.TMS_window.TMS_mass, 2)))
        self.powertrain_layout.addWidget(QLineEdit(str(round(self.TMS_window.TMS_mass, 2))), 3, 1)

    def get_configuration(self):

        configuration = int(self.configuration_selection.currentIndex())

        if configuration == 0:
            configuration_name = "Conventional"
        elif configuration == 1:
            configuration_name = "Parallel"
        elif configuration == 2:
            configuration_name = "Series"
        else:
            configuration_name = "Series_Parallel"

        self.ac_configuration = configuration_name

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

    def perform_uncertainty_analysis(self):

        if not int(self.method_selection.currentIndex()) ==  0:
            message = "More evaluation methods will be added soon. Switching back to Monte Carlo Simulation."
            QMessageBox.information(self, "Info", message, QMessageBox.Ok)

        for iter in range(int(self.mc_nsamples.text())):

            self.navigate2path(['results', "uncertainty_analysis", "resultsRun_{0}".format(self.run)])

            self.view_aircraft_button.setEnabled(True)
            
            self.define_target_mission()
            
            total_mission_time = 0
            for key, item in self.target_mission.timetable.items():
                total_mission_time = total_mission_time + item

            if not self.acsizing_settings:
                self.acsizing_settings = AircraftSizingSettings()

            propeller = Propeller(self.nested_prop_window)
            eps = EPS(self.eps_inputs,
                      self.eps_inputs_lb,
                      self.eps_inputs_ub)
            propulsion = Propulsion(self.powertrain_specs_defaults,
                                    eps,
                                    propeller,
                                    self.nested_GT_window,
                                    self.powertrain_specs_defaults_lb,
                                    self.powertrain_specs_defaults_ub)
            settings = Settings(int(self.configuration_selection.currentIndex()),
                                bool(self.advanced_materials_checkbox.isChecked()),
                                bool(self.allow_charging_checkbox.isChecked()),
                                bool(self.constrain_empty_mass.isChecked()),
                                self.operational_mode_configurator,
                                self.acsizing_settings.settings)
            acsizing = aircraft_sizing_wrapper(self)
            acsizing.run_acsizing_wrapper(self.target_mission,
                                          propulsion,
                                          settings,
                                          self.tlars_window.tlar_data,
                                          uncertainty = True)

            os.chdir(self.home_dir)

            if bool(self.include_doc.isChecked()):
                self.navigate2path(["results", "uncertainty_analysis", "resultsRun_{0}".format(self.run)])
                # call DOC class
                if not self.doc_window:
                    self.doc_window = AircraftCostCalculator(self.home_dir, os.getcwd())
                self.doc_window.getInputData()
                self.doc_window.input_data["block_time_input"] = acsizing.to_DOC["Block_Time"]
                self.doc_window.input_data["block_fuel_input"] = acsizing.to_DOC["Fuel_Burn"]
                self.doc_window.input_data["battery_energy_input"] = acsizing.to_DOC["Battery_Energy"]
                self.doc_window.input_data["payload_input"] = acsizing.to_DOC["Payload"]
                self.doc_window.input_data["max_takeoff_mass_input"] = acsizing.to_DOC["MTOW"]
                self.doc_window.input_data["mission_range_input"] = acsizing.to_DOC["Range"]
                self.doc_window.input_data["empty_mass_input"] = acsizing.to_DOC["Empty_Weight"]
                self.doc_window.input_data["propulsion_mass_input"] = acsizing.to_DOC["Propulsion_Weight"]
                self.doc_window.input_data["wing_span_input"] = acsizing.to_DOC["Wing_Span"]
                self.doc_window.input_data["fuselage_length_input"] = acsizing.to_DOC["Fuselage_Length"]
                self.doc_window.input_data["max_total_gt_power_input"] = acsizing.to_DOC["P_GT_max"]
                self.doc_window.input_data["max_em_power_input"] = acsizing.to_DOC["P_EM_max"]
                self.doc_window.input_data["v1_velocity_input"] = acsizing.to_DOC["Vtakeoff"]
                
                self.doc_window.calculate_costs(output_dir = os.getcwd(), export_msg = False)
                self.doc_window.export_result_plots(output_dir = os.getcwd(), export_msg = False)
                
                os.chdir(self.home_dir)

            if bool(self.include_lca.isChecked()):
                self.navigate2path(["results", "uncertainty_analysis", "resultsRun_{0}".format(self.run)])
                # call LCA class
                if not self.lca_window:
                    self.lca_window = AircraftLifeCycleEval(self.home_dir, os.getcwd())
                self.lca_window.retreive_input_data()
                res = set(self.lca_window.inputData).intersection(acsizing.to_lca)
                for key in res:
                    self.lca_window.inputData[key] = acsizing.to_lca[key]

                self.lca_window.perform_lca(output_dir = os.getcwd(), export_msg = False)
                self.lca_window.export_result_plots(output_dir = os.getcwd(), export_msg = False)

                os.chdir(self.home_dir)

            if bool(self.include_stability.isChecked()):
                self.navigate2path(["results", "uncertainty_analysis", "resultsRun_{0}".format(self.run)])
                # evaluate CoG
                aircraft_CoG = getCoG(acsizing.aircraft)
                aircraft_CoG.evaluate_CoG()
                
                # evaluate Static Margin
                acSM = getStaticMargin(acsizing.aircraft, self.home_dir, os.getcwd())
                acSM.evaluate_stability(float(self.configure_stability.text()))
                acSM.overwrite_vsp_input_file()
                acSM.exportStaticMaringReport()
                os.chdir(self.home_dir)

            if bool(self.include_trim.isChecked()):
                self.navigate2path(["results", "uncertainty_analysis", "resultsRun_{0}".format(self.run)])
                # evaluate CoG
                aircraft_CoG = getCoG(acsizing.aircraft)
                aircraft_CoG.evaluate_CoG()

                # Evaluate Trim
                acTrim = trimAnalysisWrapper(acsizing.aircraft, aircraft_CoG, self.home_dir, os.getcwd())
                acTrim.evaluateTrim(float(self.configure_trim_angle.text()), float(self.configure_trim_elevator.text()))
                os.chdir(self.home_dir)

            self.navigate2path(["results", "uncertainty_analysis", "resultsRun_{0}".format(self.run)])
            
            os.chdir(self.home_dir)
            
            self.run +=1
            self.acsizing_settings = None
            self.lca_window = None
            self.doc_window = None

        message = "Calculation completed. Results can be found in the following path:\n {0}resultsRun_{1} - {2}".format("./results/uncertainty_analysis/", self.run - int(self.mc_nsamples.text()) , self.run - 1)
        QMessageBox.information(self, "Calculation Completed", message, QMessageBox.Ok)

    def navigate2path(self, folders):

        os.chdir(self.home_dir)

        for folder in folders:
            if not os.path.exists(os.path.join(os.getcwd(), folder)):
                os.mkdir(os.path.join(os.getcwd(), folder))
            os.chdir(os.path.join(os.getcwd(), folder))
    
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
    def __init__(self, powertrain_specs, eps, propeller, gt_from_GUI, powertrain_specs_lb = None, powertrain_specs_ub = None):
        self.powertrain_specs = powertrain_specs
        self.powertrain_specs_lb = powertrain_specs_lb
        self.powertrain_specs_ub = powertrain_specs_ub
        self.eps = eps
        self.propeller = propeller
        self.gt_from_GUI = gt_from_GUI

class EPS(object):
    def __init__(self, eps_inputs, eps_inputs_lb = None, eps_inputs_ub = None):
        self.eps_inputs = eps_inputs
        self.eps_inputs_lb = eps_inputs_lb
        self.eps_inputs_ub = eps_inputs_ub

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

def main():
    app = QApplication(sys.argv)
    dialog = UncertaintyAnalysisDialog()
    result = dialog.exec_()
    sys.exit(result)

if __name__ == "__main__":
    main()