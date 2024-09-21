import sys, os
import numpy as np
from gasturbine.compressor_map import map_builder
from gasturbine.map_scaling import Map_Scaling
from gasturbine.gas_turbine_cycle import gas_turbine_cycle_builder
from gasturbine.propeller import Propeller
from PyQt5.QtWidgets import (
    QDialog, QApplication, QVBoxLayout, QTabWidget, QPushButton,
    QGroupBox, QFormLayout, QLineEdit, QHBoxLayout, QWidget, QMessageBox,
    QScrollArea, QLabel
)
from PyQt5.QtGui import QPixmap

class GasTurbineConfigurator(QDialog):
    def __init__(self, home_dir, output_dir):
        super().__init__()

        self.home_dir = home_dir
        self.output_dir = output_dir

        self.lpc_map_loaded = False
        self.hpc_map_loaded = False
        self.scaled_map_lpc_loaded = False
        self.scaled_map_hpc_loaded = False
        self.design_point_evaluated = False
        self.propeller_loaded = False

        self.setWindowTitle("Gas Turbine Configurator")
        self.setGeometry(100, 100, 600, 850)

        self.layout = QVBoxLayout()

        tabs = QTabWidget()
        self.layout.addWidget(tabs)

        # Design Point Evaluation Tab
        design_point_tab = QWidget()
        design_point_layout = QVBoxLayout()
        design_point_tab.setLayout(design_point_layout)

        design_parameters_group = QGroupBox("Design Parameters")
        design_parameters_layout = QFormLayout()
        design_parameters_group.setLayout(design_parameters_layout)

        self.design_params = {
            "Power": 1800,
            "PR": 14,
            "mc": 8.0,
            "TET": 1400,
            "Alt": 0,
            "Vinf" : 60,
            "LPC_PR" : 3.6,
        }

        self.design_params_line_edits = {}  # Store line edits for later reference

        design_params_labels = {
            "Power": "Equivalent Shaft Power [kW]",
            "PR": "Overall Pressure Ratio [-]",
            "mc": "Compressor Mass Flow [kg/s]",
            "TET": "Turbine Entry Temperature [K]",
            "Alt" : "Design Point Altitude [m]",
            "Vinf" : "Free stream velocity [m/s]",
            "LPC_PR" : "Low pressure turbine pressure ratio [-]",
        }

        self.dp_name = {"DPname": QLineEdit("Take-Off")}

        design_parameters_layout.addRow("Design Point Name", self.dp_name["DPname"])

        for param, value in self.design_params.items():
            line_edit = QLineEdit(str(value))
            self.design_params_line_edits[param] = line_edit
            design_parameters_layout.addRow(design_params_labels[param], line_edit)

        design_point_layout.addWidget(design_parameters_group)

        general_inputs_group = QGroupBox("General Inputs")
        general_inputs_layout = QFormLayout()
        general_inputs_group.setLayout(general_inputs_layout)

        self.general_inputs = {
            "Hf": 43.3,  # Lower Heating Value in [MJ/kg]
            "nHPT_pol": 0.8,  # Polytropic Efficiency of High Pressure Turbine [-]
            "nLPT_pol": 0.8,  # Polytropic Efficiency of Low Pressure Turbine [-]
            "nPT": 0.81,  # Adiabatic Efficiency of Power Turbine [-]
            "ngb": 0.99,  # Gearbox Efficiency [-]
            "bleed": 0.03,  # Compressed Air Bleeding [-]
            "delta_P_CC": 0.05,  # Combustion Chamber Pressure Losses [-]
            "delta_P_intake": 0.01,  # Intake Pressure Losses [-]
            "delta_P_c": 0.02,  # Pressure Losses between Compressors [-]
            "delta_P_T": 0.02,  # Pressure Losses between Turbines [-]
            "delta_P_N": 0.01,  # Nozzle Pressure Losses [-]
            "nn": 1,  # Isentropic Nozzle Efficiency [-]
            "ncc": 0.995,  # Combustion Chamber Efficiency [-]
            "nmech_HPS": 0.995,  # Mechanical Efficiency of High Pressure Shaft [-]
            "nmech_LPS": 0.995,  # Mechanical Efficiency of Low Pressure Shaft [-]
            "nmech_PS": 0.995,  # Mechanical Efficiency of Power Shaft [-]
            "ninlet": 1  # Isentropic intake Efficiency
        }

        self.general_inputs_line_edits = {}  # Store line edits for later reference

        general_inputs_labels = {
            "Hf": "Jet-A lower Heating Value in [MJ/kg]",
            "nHPT_pol": "Polytropic Efficiency of High Pressure Turbine [-]",
            "nLPT_pol": "Polytropic Efficiency of Low Pressure Turbine [-]",
            "nPT": "Adiabatic Efficiency of Power Turbine [-]",
            "ngb": "Gearbox Efficiency [-]",
            "bleed": "Compressed Air Bleed [-]",
            "delta_P_CC": "Combustion Chamber Pressure Losses [-]",
            "delta_P_intake": "Intake Pressure Losses [-]",
            "delta_P_c": "Pressure Losses between Compressors [-]",
            "delta_P_T": "Pressure Losses between Turbines [-]",
            "delta_P_N": "Nozzle Pressure Losses [-]",
            "nn": "Nozzle Isentropic Efficiency [-]",
            "ncc": "Combustion Chamber Efficiency [-]",
            "nmech_HPS": "Mechanical Efficiency of High Pressure Shaft [-]",
            "nmech_LPS": "Mechanical Efficiency of Low Pressure Shaft [-]",
            "nmech_PS": "Mechanical Efficiency of Power Shaft [-]",
            "ninlet": "Intake Isentropic Efficiency",
        }

        for input_name, value in self.general_inputs.items():
            line_edit = QLineEdit(str(value))
            self.general_inputs_line_edits[input_name] = line_edit
            general_inputs_layout.addRow(general_inputs_labels[input_name], line_edit)

        design_point_layout.addWidget(general_inputs_group)

        calculate_button = QPushButton("Calculate")
        calculate_button.clicked.connect(self.on_dp_calculate_button_clicked)
        export_report_button = QPushButton("View Open Brayton Cycle")
        export_report_button.clicked.connect(self.on_dp_export_report_clicked)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(calculate_button)
        buttons_layout.addWidget(export_report_button)
        design_point_layout.addLayout(buttons_layout)

        tabs.addTab(design_point_tab, "Design Point Evaluation")

        # Compressor Maps Tab
        compressor_maps_tab = QWidget()
        compressor_maps_layout = QHBoxLayout()
        compressor_maps_tab.setLayout(compressor_maps_layout)

        low_pressure_group = QGroupBox("Low Pressure Compressor")
        low_pressure_layout = QVBoxLayout()
        low_pressure_group.setLayout(low_pressure_layout)

        reference_map_info_low = QGroupBox("Reference Map Info")
        reference_map_info_layout_low = QFormLayout()

        reference_map_info_low.setDisabled(True)  # Disable inputs

        self.reference_map_low = {
            "Pressure Ratio [-]": QLineEdit("3.92"),
            "Corrected Mass flow rate [-]": QLineEdit("0.95"),
            "Mass Flow Rate [kg/s]": QLineEdit("4.5"),
            "Inlet Temperature [K]" : QLineEdit("248.76"),
            "Inlet Pressure [Pa]" : QLineEdit("43089"),
            "Reference Rotational Speed [rpm]" : QLineEdit("28000"),            
        }

        for param, value in self.reference_map_low.items():
            # line_edit = QLineEdit(str(value))
            reference_map_info_layout_low.addRow(param, value)

        low_pressure_layout.addWidget(reference_map_info_low)
        reference_map_info_low.setLayout(reference_map_info_layout_low)

        buttons_layout_low = QVBoxLayout()
        plot_ref_map_button_low = QPushButton("Plot Reference Map")
        plot_ref_map_button_low.clicked.connect(self.lpc_ref_map_plot)
        calculate_ref_map_button_low = QPushButton("Calculate Reference Map")
        calculate_ref_map_button_low.clicked.connect(self.lpc_ref_map_calc)
        buttons_layout_low.addWidget(plot_ref_map_button_low)
        buttons_layout_low.addWidget(calculate_ref_map_button_low)
        low_pressure_layout.addLayout(buttons_layout_low)

        new_design_point_group_low = QGroupBox("New Design Point")
        new_design_point_layout_low = QFormLayout()
        new_design_point_group_low.setLayout(new_design_point_layout_low)

        self.new_design_point_low = {
            "Pressure Ratio [-]": QLineEdit("4.1"),
            "Mass flow rate [kg/s]": QLineEdit("8"),
            "Inlet Temperature [K]": QLineEdit("248.76"),
            "Inlet Pressure [Pa]": QLineEdit("43089"),
        }

        for param, line_edit in self.new_design_point_low.items():
            new_design_point_layout_low.addRow(param, line_edit)

        low_pressure_layout.addWidget(new_design_point_group_low)
        
        new_design_point_group_low_res = QGroupBox("Results")
        new_design_point_layout_low_res = QFormLayout()
        new_design_point_group_low_res.setLayout(new_design_point_layout_low_res)
        
        self.new_design_point_low_res = {
            "New Efficiency [-]" : QLineEdit(),
            "New Rotational Speed [rpm]" : QLineEdit(),
        }
        
        for param, line_edit in self.new_design_point_low_res.items():
            new_design_point_layout_low_res.addRow(param, line_edit)
            line_edit.setDisabled(True)
            
        low_pressure_layout.addWidget(new_design_point_group_low_res)

        buttons_layout_low_scaled = QVBoxLayout()
        self.scale_map_button_low = QPushButton("Scale Map")
        self.scale_map_button_low.clicked.connect(self.scale_lpc_map)
        self.scale_map_button_low.setEnabled(False)
        self.plot_scaled_map_button_low = QPushButton("Plot Scaled Map")
        self.plot_scaled_map_button_low.clicked.connect(self.plot_scaled_map_low)
        self.plot_scaled_map_button_low.setEnabled(False)
        buttons_layout_low_scaled.addWidget(self.scale_map_button_low)
        buttons_layout_low_scaled.addWidget(self.plot_scaled_map_button_low)
        low_pressure_layout.addLayout(buttons_layout_low_scaled)

        compressor_maps_layout.addWidget(low_pressure_group)

        # High Pressure Compressor
        high_pressure_group = QGroupBox("High Pressure Compressor")
        self.high_pressure_layout = QVBoxLayout()
        high_pressure_group.setLayout(self.high_pressure_layout)

        reference_map_info_high = QGroupBox("Reference Map Info")
        reference_map_info_layout_high = QFormLayout()
        reference_map_info_high.setLayout(reference_map_info_layout_high)

        reference_map_info_high.setDisabled(True)  # Disable inputs
        
        self.reference_map_high = {
            "Pressure Ratio [-]": QLineEdit("2.85"),
            "Corrected Mass flow rate [-]": QLineEdit("0.97"),
            "Mass Flow Rate [kg/s]": QLineEdit("4.5"),
            "Inlet Temperature [K]" : QLineEdit("419.68"),
            "Inlet Pressure [Pa]" : QLineEdit("188847"),
            "Reference Rotational Speed [rpm]" : QLineEdit("38000"),            
        }

        for param, value in self.reference_map_high.items():
            # line_edit = QLineEdit(str(value))
            reference_map_info_layout_high.addRow(param, value)

        self.high_pressure_layout.addWidget(reference_map_info_high)

        buttons_layout_high = QVBoxLayout()
        plot_ref_map_button_high = QPushButton("Plot Reference Map")
        plot_ref_map_button_high.clicked.connect(self.hpc_ref_map_plot)
        calculate_ref_map_button_high = QPushButton("Calculate Reference Map")
        calculate_ref_map_button_high.clicked.connect(self.hpc_ref_map_calc)
        buttons_layout_high.addWidget(plot_ref_map_button_high)
        buttons_layout_high.addWidget(calculate_ref_map_button_high)
        self.high_pressure_layout.addLayout(buttons_layout_high)

        new_design_point_group_high = QGroupBox("New Design Point")
        new_design_point_layout_high = QFormLayout()
        new_design_point_group_high.setLayout(new_design_point_layout_high)

        self.new_design_point_high = {
            "Pressure Ratio [-]": QLineEdit("2.95"),
            "Mass flow rate [kg/s]": QLineEdit("8"),
            "Inlet Temperature [K]": QLineEdit("419.68"),
            "Inlet Pressure [Pa]": QLineEdit("188847"),
        }

        for param, line_edit in self.new_design_point_high.items():
            new_design_point_layout_high.addRow(param, line_edit)

        self.high_pressure_layout.addWidget(new_design_point_group_high)
        
        new_design_point_group_high_res = QGroupBox("Results")
        new_design_point_layout_high_res = QFormLayout()
        new_design_point_group_high_res.setLayout(new_design_point_layout_high_res)
        
        self.new_design_point_high_res = {
            "New Efficiency [-]" : QLineEdit(),
            "New Rotational Speed [rpm]" : QLineEdit(),
        }
        
        for param, line_edit in self.new_design_point_high_res.items():
            new_design_point_layout_high_res.addRow(param, line_edit)
            line_edit.setDisabled(True)
            
        self.high_pressure_layout.addWidget(new_design_point_group_high_res)

        buttons_layout_high_scaled = QVBoxLayout()
        self.scale_map_button_high = QPushButton("Scale Map")
        self.scale_map_button_high.setEnabled(False)
        self.scale_map_button_high.clicked.connect(self.scale_hpc_map)
        self.plot_scaled_map_button_high = QPushButton("Plot Scaled Map")
        self.plot_scaled_map_button_high.setEnabled(False)
        self.plot_scaled_map_button_high.clicked.connect(self.plot_scaled_map_high)
        buttons_layout_high_scaled.addWidget(self.scale_map_button_high)
        buttons_layout_high_scaled.addWidget(self.plot_scaled_map_button_high)
        self.high_pressure_layout.addLayout(buttons_layout_high_scaled)

        compressor_maps_layout.addWidget(high_pressure_group)

        tabs.addTab(compressor_maps_tab, "Compressor Maps")

        # Propeller Map Tab
        propeller_map_tab = QWidget()
        propeller_map_layout = QVBoxLayout()
        propeller_map_tab.setLayout(propeller_map_layout)

        propeller_map_info_group = QGroupBox("Propeller Map Info")
        propeller_map_info_group_layout = QVBoxLayout()
        load_map_button = QPushButton("Load Reference Map")
        load_map_button.clicked.connect(self.load_propeller_map)
        show_map_button = QPushButton("Show Map")
        show_map_button.clicked.connect(self.plot_propeller_map)
        propeller_map_info_group_layout.addWidget(load_map_button)
        propeller_map_info_group_layout.addWidget(show_map_button)
        propeller_map_info_group.setLayout(propeller_map_info_group_layout)
        
        propeller_map_layout.addWidget(propeller_map_info_group)

        propeller_map_calculation_group = QGroupBox("Find propeller's efficiency")
        propeller_map_calculation_group_layout = QFormLayout()

        self.propeller_input_data = {
            "Freestream velocity [m/s]" : QLineEdit("50"),
            "Propeller rotational speed [rpm]" : QLineEdit("2000"),
            "Propeller diameter [m]" : QLineEdit("2.1"),
        }

        for key, item in self.propeller_input_data.items():
            propeller_map_calculation_group_layout.addRow(key, item)

        prop_calculate_button = QPushButton("Calculate Propeller Efficiency")
        prop_calculate_button.clicked.connect(self.calculate_propeller_efficiency)

        propeller_map_calculation_group_layout.addWidget(prop_calculate_button)

        propeller_map_calculation_group.setLayout(propeller_map_calculation_group_layout)

        propeller_map_layout.addWidget(propeller_map_calculation_group)

        propeller_map_results_group = QGroupBox("Results")
        propeller_map_results_group_layout = QFormLayout()

        self.propeller_eta_res = {
            "Propeller efficiency [-]" : QLineEdit()
        }

        for key, item in self.propeller_eta_res.items():
            propeller_map_results_group_layout.addRow(key, item)
            item.setEnabled(False)

        propeller_map_results_group.setLayout(propeller_map_results_group_layout)

        propeller_map_layout.addWidget(propeller_map_results_group)

        tabs.addTab(propeller_map_tab, "Propeller Map")

        # OK and Cancel buttons
        ok_cancel_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.on_ok_button_clicked)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.on_cancel_button_clicked)
        ok_cancel_layout.addWidget(ok_button)
        ok_cancel_layout.addWidget(cancel_button)
        self.layout.addLayout(ok_cancel_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(tabs)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

    def calculate_propeller_efficiency(self):

        if not self.propeller_loaded:
            self.load_propeller_map()

        V = float(self.propeller_input_data["Freestream velocity [m/s]"].text())
        n = float(self.propeller_input_data["Propeller rotational speed [rpm]"].text())
        D = float(self.propeller_input_data["Propeller diameter [m]"].text())

        eta_prop = self.propeller.propeller_eff(V, D, n)

        self.propeller_eta_res["Propeller efficiency [-]"].setText(str(np.round(eta_prop, 3)))

    def plot_propeller_map(self):

        if not self.propeller_loaded:
            self.load_propeller_map()

        os.chdir(self.output_dir)
        self.propeller.plot_nprop_curve()

        self.plot_window = ImageLoader()
        self.plot_window.load_image("propeller_efficiency.png")
        self.plot_window.show()

        os.chdir(self.home_dir)

    def load_propeller_map(self):

        self.propeller = Propeller()
        self.propeller.load_nprop_points()
        self.propeller_loaded = True

        message = f"Map Successfully Loaded."
        QMessageBox.information(self, "Load Successfull", message, QMessageBox.Ok)

    def plot_scaled_map_low(self):
        
        empty_strings = []
        for key, item in self.new_design_point_low.items():
            if not item.text():
                empty_strings.append(key)
                
        if empty_strings:
            empty_keys = ""
            for empkey in empty_strings:
                empty_keys = empty_keys + empkey + ", "
            msgbox = QMessageBox()
            msgbox.setIcon(QMessageBox.Warning)
            msgbox.setText("New Design Point Parameters %s are empty. Please add inputs and retry." % empty_keys)
            msgbox.setWindowTitle("Warning!")
            msgbox.exec_()
        else:
            if not self.scaled_map_lpc_loaded:
                self.scale_lpc_map()
            
            self.scaled_map_lpc.plot_map(show_original = False, filled = True)
            os.chdir(self.output_dir)
            self.scaled_map_lpc.save_map_fig("lpc_compressor_map_scaled.png")
            
            self.plot_window = ImageLoader()
            self.plot_window.load_image("lpc_compressor_map_scaled.png")
            self.plot_window.show()
            
            os.chdir(self.home_dir)

    def plot_scaled_map_high(self):
        
        empty_strings = []
        for key, item in self.new_design_point_high.items():
            if not item.text():
                empty_strings.append(key)
                
        if empty_strings:
            empty_keys = ""
            for empkey in empty_strings:
                empty_keys = empty_keys + empkey + ", "
            msgbox = QMessageBox()
            msgbox.setIcon(QMessageBox.Warning)
            msgbox.setText("New Design Point Parameters %s are empty. Please add inputs and retry." % empty_keys)
            msgbox.setWindowTitle("Warning!")
            msgbox.exec_()
        else:        
            if not self.scaled_map_hpc_loaded:
                self.scale_hpc_map()
            
            self.scaled_map_hpc.plot_map(show_original = False, filled = True)
            os.chdir(self.output_dir)
            self.scaled_map_hpc.save_map_fig("hpc_compressor_map_scaled.png")
            
            self.plot_window = ImageLoader()
            self.plot_window.load_image("hpc_compressor_map_scaled.png")
            self.plot_window.show()
        
            os.chdir(self.home_dir)

    def lpc_ref_map_plot(self):
        if  not self.lpc_map_loaded:
            self.lpc_ref_map_calc()
        
        os.chdir(self.output_dir)
        self.lpc_ref_map.plot_map(filled = True, save_map = True, fname = "lpc_centrifugal_map")
        
        self.plot_window = ImageLoader()
        self.plot_window.load_image("lpc_centrifugal_map.png")
        self.plot_window.show()

        os.chdir(self.home_dir)

    def lpc_ref_map_calc(self):
        
        self.plot_scaled_map_button_low.setEnabled(True)
        self.scale_map_button_low.setEnabled(True)
        
        self.lpc_ref_map = map_builder()
        self.lpc_ref_map.navigate_to_path(["gasturbine", "component_maps", "lpc_centrifugal"])
        self.lpc_ref_map.get_ref_info()
        self.lpc_ref_map.build_map('surge_line.map', 'rpm_lines.map', ["70eff.map", "75eff.map", "80eff.map", "82eff.map"], 50)
        self.lpc_ref_map.reset_path()
        os.chdir(self.output_dir)
        self.lpc_ref_map.export_map('lpc_centrifugal_ref.map')
        self.lpc_map_loaded = True
        self.export_msg()
        os.chdir(self.home_dir)

    def hpc_ref_map_calc(self):
        
        self.plot_scaled_map_button_high.setEnabled(True)
        self.scale_map_button_high.setEnabled(True)
        
        self.hpc_ref_map = map_builder()
        self.hpc_ref_map.navigate_to_path(["gasturbine", "component_maps", "hpc_centrifugal"])
        self.hpc_ref_map.get_ref_info()
        self.hpc_ref_map.build_map("surge_line.map", "rpm_lines.map", ["eff65.map", "eff70.map", "eff75.map", "eff80.map", "eff82.map", "eff84.map", "eff86.map"], 50)
        self.hpc_ref_map.reset_path()
        os.chdir(self.output_dir)        
        self.hpc_ref_map.export_map("hpc_centrifugal_ref.map")
        self.hpc_map_loaded = True
        self.export_msg()
        os.chdir(self.home_dir)
    
    def hpc_ref_map_plot(self):
        if not self.hpc_map_loaded:
            self.hpc_ref_map_calc()
        
        os.chdir(self.output_dir)
        self.hpc_ref_map.plot_map(filled = True, save_map = True, fname = "hpc_centrifugal_map")
        
        self.plot_window = ImageLoader()
        self.plot_window.load_image("hpc_centrifugal_map.png")
        self.plot_window.show()
        
        os.chdir(self.home_dir)

    def scale_map(self, map, PR, ctype):

        scaled_map = Map_Scaling(map)
        scaled_map.scale_map(PR, ctype)

        return scaled_map
    
    def scale_hpc_map(self):
        empty_strings = []
        if self.hpc_map_loaded:
            for key, item in self.new_design_point_high.items():
                if not item.text():
                    empty_strings.append(key)
            if empty_strings:
                empty_keys = ""
                for empkey in empty_strings:
                    empty_keys = empty_keys + empkey + ", "
                msgbox = QMessageBox()
                msgbox.setIcon(QMessageBox.Warning)
                msgbox.setText("New Design Point Parameters %s are empty. Please add inputs and retry." % empty_keys)
                msgbox.setWindowTitle("Warning!")
                msgbox.exec_()
            else:
                self.scaled_map_hpc = self.scale_map(self.hpc_ref_map, float(self.new_design_point_high["Pressure Ratio [-]"].text()), "centrifugal")
                os.chdir(self.output_dir)
                self.scaled_map_hpc.export_map("hpc_centrifugal_scaled.map")
                wc_new_hpc = float(self.new_design_point_high["Mass flow rate [kg/s]"].text())/self.hpc_ref_map.mc*np.sqrt(float(self.new_design_point_high["Inlet Temperature [K]"].text())/self.hpc_ref_map.Tin)/(float(self.new_design_point_high["Inlet Pressure [Pa]"].text())/self.hpc_ref_map.Pin)
                hpc_eta_is, Ncorr = self.scaled_map_hpc.find_point_on_map(wc_new_hpc, float(self.new_design_point_high["Pressure Ratio [-]"].text()))
                self.new_design_point_high_res["New Efficiency [-]"].setText(str(np.round(hpc_eta_is, 3)))
                T0 = float(self.new_design_point_high["Inlet Temperature [K]"].text())
                Tref = float(self.reference_map_high["Inlet Temperature [K]"].text())
                Nref = float(self.reference_map_high["Reference Rotational Speed [rpm]"].text())
                nnew = Ncorr*Nref*np.sqrt(T0/Tref)
                self.new_design_point_high_res["New Rotational Speed [rpm]"].setText(str(np.round(nnew, 2)))
                self.export_msg()
                self.scaled_map_hpc_loaded = True                
        else:
            msgbox = QMessageBox()
            msgbox.setIcon(QMessageBox.Warning)
            msgbox.setText("Reference Map not loaded. Please load map and retry.")
            msgbox.setWindowTitle("Warning!")
            msgbox.exec_()
            
        os.chdir(self.home_dir)
    
    def scale_lpc_map(self):
        empty_strings = []
        if self.lpc_map_loaded:
            for key, item in self.new_design_point_low.items():
                if not item.text():
                    empty_strings.append(key)
            if empty_strings:
                empty_keys = ""
                for empkey in empty_strings:
                    empty_keys = empty_keys + empkey + ", "
                msgbox = QMessageBox()
                msgbox.setIcon(QMessageBox.Warning)
                msgbox.setText("New Design Point Parameters %s are empty. Please add inputs and retry." % empty_keys)
                msgbox.setWindowTitle("Warning!")
                msgbox.exec_()
            else:
                self.scaled_map_lpc = self.scale_map(self.lpc_ref_map, float(self.new_design_point_low["Pressure Ratio [-]"].text()), "centrifugal")
                os.chdir(self.output_dir)
                self.scaled_map_lpc.export_map("lpc_centrifugal_scaled.map")
                wc_new_lpc = float(self.new_design_point_low["Mass flow rate [kg/s]"].text())/self.lpc_ref_map.mc*np.sqrt(float(self.new_design_point_low["Inlet Temperature [K]"].text())/self.lpc_ref_map.Tin)/(float(self.new_design_point_low["Inlet Pressure [Pa]"].text())/self.lpc_ref_map.Pin)
                lpc_eta_is, Ncorr = self.scaled_map_lpc.find_point_on_map(wc_new_lpc, float(self.new_design_point_low["Pressure Ratio [-]"].text()))
                self.new_design_point_low_res["New Efficiency [-]"].setText(str(np.round(lpc_eta_is, 3)))
                T0 = float(self.new_design_point_low["Inlet Temperature [K]"].text())
                Tref = float(self.reference_map_low["Inlet Temperature [K]"].text())
                Nref = float(self.reference_map_low["Reference Rotational Speed [rpm]"].text())
                nnew = Ncorr*Nref*np.sqrt(T0/Tref)
                self.new_design_point_low_res["New Rotational Speed [rpm]"].setText(str(np.round(nnew, 2)))
                self.export_msg()
                self.scaled_map_lpc_loaded = True
        else:
            msgbox = QMessageBox()
            msgbox.setIcon(QMessageBox.Warning)
            msgbox.setText("Reference Map not loaded. Please load map and retry.")
            msgbox.setWindowTitle("Warning!")
            msgbox.exec_()
            
        os.chdir(self.home_dir)

    def update_design_params(self):
        for param, line_edit in self.design_params_line_edits.items():
            self.design_params[param] = float(line_edit.text())

    def update_general_inputs(self):
        for input_name, line_edit in self.general_inputs_line_edits.items():
            self.general_inputs[input_name] = float(line_edit.text())

    def on_ok_button_clicked(self):
        self.update_design_params()
        self.update_general_inputs()
        self.accept()

    def on_cancel_button_clicked(self):
        self.reject()

    def on_dp_calculate_button_clicked(self):
        
        self.update_design_params()
        self.update_general_inputs()
        
        self.gas_turbine = gas_turbine_cycle_builder(self.general_inputs)
        self.gas_turbine.define_working_media()
        self.gas_turbine.load_design_point(self.design_params, self.dp_name["DPname"].text())
        self.gas_turbine.open_brayton_cycle()
        os.chdir(self.output_dir)
        self.gas_turbine.export_design_report()
        self.export_msg()
        os.chdir(self.home_dir)
        
        self.design_point_evaluated = True

    def on_dp_export_report_clicked(self):
        
        if not self.design_point_evaluated:
            self.on_dp_calculate_button_clicked()
        
        os.chdir(self.output_dir)
        self.gas_turbine.create_open_cycle_plot("{0}_open_cycle.png".format(self.dp_name["DPname"].text()))
        
        self.plot_window = ImageLoader()
        self.plot_window.load_image("{0}_open_cycle.png".format(self.dp_name["DPname"].text()))
        self.plot_window.show()
        
        os.chdir(self.home_dir)

    def export_msg(self):
        output_directory = os.getcwd() # Update with your actual output directory
        message = f"Calculation completed. Outputs exported to:\n{output_directory}"
        QMessageBox.information(self, "Calculation Completed", message, QMessageBox.Ok)

class ImageLoader(QDialog):
    def __init__(self):
        super().__init__()

        # Set the main window properties
        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and set it as the main window's central widget
        central_widget = QWidget(self)
        # self.setCentralWidget(central_widget)

        # Create a vertical layout for the central widget
        layout = QVBoxLayout(central_widget)

        # Create a QLabel to display the image
        self.image_label = QLabel()
        layout.addWidget(self.image_label)

    def load_image(self, image_path):

        # Load and display the image
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap.scaled(800, 600))
        self.image_label.setScaledContents(True)  # Scale the image to fit the label

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GasTurbineConfigurator()
    window.show()
    sys.exit(app.exec_())
