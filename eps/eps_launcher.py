import sys, os
import json
from PyQt5.QtWidgets import QHBoxLayout, QApplication, QDialog, QVBoxLayout, QGroupBox, QLabel, QLineEdit, QPushButton, QWidget, QGridLayout, QMessageBox
from PyQt5.QtGui import QPixmap
from acsizing.electric_motor_sizing import axial_flux_motor
from acsizing.cable_sizing import cables
from acsizing.battery_sizing import battery_pack
from eps.nested_battery_launcher import PromptWindow
from eps.electric_motor_map import ElectricMotor

class EPSConfigurator(QDialog):
    def __init__(self, home_dir, output_dir):
        super().__init__()

        self.nested_battery_window = False
        self.emotor_map_loaded = False
        self.battery_calculated = False
        self.cables_calculated = False
        self.motor_calculated = False
        self.configure_cell_input = []

        self.home_dir = home_dir
        self.output_dir = output_dir

        self.setWindowTitle("Electrical Powertrain System Configurator")
        self.setGeometry(100, 100, 800, 600)

        grid_layout = QGridLayout(self)
        self.create_emotor_group(grid_layout)
        self.create_cable_group(grid_layout)
        self.create_batteries_group(grid_layout)
        self.create_buttons(grid_layout)

    def create_emotor_group(self, grid_layout):
        
        emotor_group = QGroupBox("Axial Flux Electric Motor Sizing")
        emotor_layout = QGridLayout()

        self.emotor_sizing_inputs = {
            "Maximum Power [kW]" : QLineEdit("500"),
            "Nominal rotational speed [rpm]" : QLineEdit("2500"),
            "System's Voltage [V]" : QLineEdit("1000"),
        }

        emotor_tooltip_data = {
            "Maximum Power [kW]" : "Insert the motor's maximum power output in kW.",
            "Nominal rotational speed [rpm]" : "Insert the motor's target rotational speed in rpm.",
            "System's Voltage [V]" : "Insert the system's voltage.",
        }

        row = 0
        for key, input_widget in self.emotor_sizing_inputs.items():
            emotor_layout.addWidget(QLabel(key), row, 0)
            input_widget.setToolTip(emotor_tooltip_data[key])
            input_widget.setEnabled(True)
            emotor_layout.addWidget(input_widget, row, 1)
            row += 1

        calculate_button = QPushButton("Perform Motor Sizing")
        calculate_button.clicked.connect(self.calculate_motor)
        export_button = QPushButton("Export Motor Sizing Report")
        export_button.clicked.connect(self.export_motor_results)

        calculate_map_button = QPushButton("Calculate E-Motor Map")
        calculate_map_button.clicked.connect(self.calculate_emotor_map)
        show_map_button = QPushButton("Show E-Motor Map")
        show_map_button.clicked.connect(self.show_emotor_map)

        emotor_layout.addWidget(calculate_button, row, 0)
        emotor_layout.addWidget(export_button, row, 1)
        emotor_layout.addWidget(calculate_map_button, row + 1, 0)
        emotor_layout.addWidget(show_map_button, row + 1, 1)

        emotor_group.setLayout(emotor_layout)
        grid_layout.addWidget(emotor_group, 0, 1)

    def calculate_emotor_map(self):

        self.emotor_map = ElectricMotor()
        self.emotor_map.load_eff_points()
        self.emotor_map.load_power_points()

        os.chdir(self.output_dir)
        self.emotor_map.write_eff_csv()
        self.emotor_map.write_power_torque_csv()

        message = f"Calculation completed. Outputs exported to:\n{self.output_dir}"
        QMessageBox.information(self, "Calculation Completed", message, QMessageBox.Ok)

        self.emotor_map_loaded = True

        os.chdir(self.home_dir)

    def show_emotor_map(self):

        if not self.emotor_map_loaded:
            self.calculate_emotor_map()

        os.chdir(self.output_dir)
        self.emotor_map.plot_eff_map()
        self.emotor_map.plot_power_torque_curves()

        self.plot_window = ImageLoader()
        self.plot_window.load_image("motor_power_torque_eff.png")
        self.plot_window.show()

        self.plot_window1 = ImageLoader()
        self.plot_window1.load_image("motor_power_torque.png")
        self.plot_window1.show()

        os.chdir(self.home_dir)

    def create_cable_group(self, grid_layout):

        cable_group = QGroupBox("Cable Sizing")
        cable_layout = QGridLayout()

        cable_inputs_tooltips = {
            "Maximum Power [kW]" : "Insert the motor's maximum power output in kW.",
            "System's Voltage [V]" : "Insert the system's voltage.",
            "AC Cabling Length [m]" : "Insert the total AC cables length.",
            "DC Cabling Length [m]" : "Insert the total DC cables length.",
        }

        self.cable_inputs = {
            "Maximum Power [kW]" : QLineEdit("500"),
            "System's Voltage [V]" : QLineEdit("1000"),
            "AC Cabling Length [m]" : QLineEdit("4"),
            "DC Cabling Length [m]" : QLineEdit("40"),
        }

        row = 0
        for key, input_widget in self.cable_inputs.items():
            cable_layout.addWidget(QLabel(key), row, 0)
            input_widget.setToolTip(cable_inputs_tooltips[key])
            input_widget.setEnabled(True)
            cable_layout.addWidget(input_widget, row, 1)
            row += 1

        # self.current_type = QComboBox()
        # self.current_type.addItems(["AC", "DC"])
        # self.current_type.setCurrentIndex(0)

        # cable_layout.addWidget(QLabel("Current type:"), row, 0)
        # cable_layout.addWidget(self.current_type, row, 1)

        calculate_button = QPushButton("Perform Cable Sizing")
        calculate_button.clicked.connect(self.calculate_cables)
        export_button = QPushButton("Export Cable Sizing Report")
        export_button.clicked.connect(self.export_cable_results)

        cable_layout.addWidget(calculate_button, row + 1, 0)
        cable_layout.addWidget(export_button, row + 1, 1)

        cable_group.setLayout(cable_layout)
        grid_layout.addWidget(cable_group, 0, 2)

    def create_batteries_group(self, grid_layout):

        battery_group = QGroupBox("Battery Pack Sizing")
        battery_layout = QGridLayout()

        battery_inputs_tooltips = {
            "Maximum Power [kW]" : "Insert the motor's maximum power output in kW.",
            "System's Voltage [V]" : "Insert the system's voltage.",
            "Mission Energy [kWh]" : "Enter mission's electric energy requirements.",
            "Battery Gravimetric Energy Density [kWh/kg]" : "Enter the gravimetric specific energy of batteries.",
            "Maximum Depth of Discharge [%]" : "Enter the maximum allowable depth of discharge for the battery cells.",
            "Batteries End Of Life Capacity [%]" : "Enter the batteries' end-of-life capacity compared to their initial nominal capacity.",
            "Pack to Cell Gravimetric Energy Density Ratio [-]" : "Enter the gravimetric energy density reduction of the pack compared to the cell, due to the addition of extra components.",
            "Maximum Discharge Rate [C]" : "Enter the maximum allowable cell discharge rate.",
            "Maximum Charge Rate [C]" : "Enter the maximumm allowable cell charge rate.",
        }

        self.battery_inputs = {
            "Maximum Power [kW]" : QLineEdit("500"),
            "System's Voltage [V]" : QLineEdit("1000"),
            "Mission Energy [kWh]" : QLineEdit("750"),
            "Battery Gravimetric Energy Density [kWh/kg]" : QLineEdit("0.65"),
            "Maximum Depth of Discharge [%]" : QLineEdit("80"),
            "Batteries End Of Life Capacity [%]" : QLineEdit("80"),
            "Pack to Cell Gravimetric Energy Density Ratio [-]" : QLineEdit("0.85"),
            "Maximum Discharge Rate [C]" : QLineEdit("1"),
            "Maximum Charge Rate [C]" : QLineEdit("0.5")
        }

        row = 0
        for key, input_widget in self.battery_inputs.items():
            battery_layout.addWidget(QLabel(key), row, 0)
            input_widget.setToolTip(battery_inputs_tooltips[key])
            input_widget.setEnabled(True)
            battery_layout.addWidget(input_widget, row, 1)
            row += 1

        configure_batteries_button = QPushButton("Confugure Batteries")
        configure_batteries_button.clicked.connect(self.launch_battery_configurator)

        calculate_button = QPushButton("Perform Battery Pack Sizing")
        calculate_button.clicked.connect(self.calculate_battery)
        export_button = QPushButton("Export Battery Pack Sizing Report")
        export_button.clicked.connect(self.export_battery_results)

        battery_layout.addWidget(configure_batteries_button, row, 0)

        battery_layout.addWidget(calculate_button, row + 1, 0)
        battery_layout.addWidget(export_button, row + 1, 1)

        battery_group.setLayout(battery_layout)
        grid_layout.addWidget(battery_group, 0, 3)

    def launch_battery_configurator(self):

        self.cell_info = {
            "Cell_height": "0.11",                    # cell height                         [m]
            "Cell_thickness": "0.01",                 # cell thickness                      [m]
            "Cell_width": "0.08",                     # cell width                          [m]
            "cell_Vnom": "3.6",                       # cell nominal Voltage                [V]
            "Cell_Vmax": "4.12",                      # cell maximum Voltage                [V]
            "Efficiency_1C": "0.9525",                # cell efficiency at 1C               [-]
            "Efficiency_C2": "0.976",                 # cell efficiency at C/2              [-]
            "Efficiency_C3": "0.984",                 # cell efficiency at C/3              [-]
            "Efficiency_C4": "0.9885",                # cell efficiency at C/4              [-]
            "Efficiency_C5": "0.9915"                 # cell efficiency at C/5              [-]
        }

        if not self.nested_battery_window:
            self.nested_battery_window = PromptWindow(self.cell_info)
        # self.nested_battery_window.confirm_button.clicked.connect(self.override_defaults)
        self.nested_battery_window.show()

        if self.nested_battery_window.exec_():
            self.configure_cell_input = [float(self.nested_battery_window.data["Cell_height"]),
                                        float(self.nested_battery_window.data["Cell_thickness"]),
                                        float(self.nested_battery_window.data["Cell_width"]),
                                        float(self.nested_battery_window.data["cell_Vnom"]),
                                        float(self.nested_battery_window.data["Cell_Vmax"]),
                                        float(self.nested_battery_window.data["Efficiency_1C"]),
                                        float(self.nested_battery_window.data["Efficiency_C2"]),
                                        float(self.nested_battery_window.data["Efficiency_C3"]),
                                        float(self.nested_battery_window.data["Efficiency_C4"]),
                                        float(self.nested_battery_window.data["Efficiency_C5"]),]
        else:
            self.configure_cell_input = []

    def create_buttons(self, grid_layout):
        button_layout = QGridLayout()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(ok_button, 0, 0)
        button_layout.addWidget(cancel_button, 0, 1)

        grid_layout.addLayout(button_layout, 1, 3)

    def calculate_motor(self):
        # motor_inputs = {key: field.text() for key, field in self.emotor_sizing_inputs.items()}
        # print("Motor inputs:", motor_inputs)
        self.calculate_motor_clicked = True
        P = float(self.emotor_sizing_inputs["Maximum Power [kW]"].text())
        N = float(self.emotor_sizing_inputs["Nominal rotational speed [rpm]"].text())
        Vsys = float(self.emotor_sizing_inputs["System's Voltage [V]"].text())
        
        self.electric_motor = axial_flux_motor()
        self.results = self.electric_motor.size_motor(P, N, Vsys)

        message = f"Calculation Completed."
        QMessageBox.information(self, "Successfull Calculation", message, QMessageBox.Ok)
        self.motor_calculated = True

    def export_motor_results(self):
        if not self.motor_calculated:
            self.calculate_motor()
        self.emotor_output_dict = {
            "E-motor mass" : self.results[0],
            "Coldplate mass" : self.results[1],
            "Coldplate volume" : self.results[2],
            "Coldplate area" : self.results[3],
            "Tlim" : self.results[4],
            "Return value" : self.results[-1],
        }

        os.chdir(self.output_dir)

        with open("./e_motor_sizing_report.dat", "w") as myfile:
            json.dump(self.emotor_output_dict, myfile)
        myfile.close()

        self.export_msg()

        os.chdir(self.home_dir)

    def calculate_cables(self):
        # cable_inputs = {key: field.text() for key, field in self.cable_inputs.items()}
        # cable_inputs['Current Type'] = current_type
        # print("Cable inputs:", cable_inputs)
        # current_type = self.current_type.currentText()

        V = float(self.cable_inputs["System's Voltage [V]"].text())
        P = float(self.cable_inputs["Maximum Power [kW]"].text())
        l_ac = float(self.cable_inputs["AC Cabling Length [m]"].text())
        l_dc = float(self.cable_inputs["DC Cabling Length [m]"].text())

        self.cable_sizing = cables()
        self.cable_sizing.cable_characteristics()
        ac_res = self.cable_sizing.ac_cable_sizing(P, V)
        dc_res = self.cable_sizing.dc_cable_sizing(P, V)

        self.cabling_sizing_results = {
            "Total Cabling Mass [kg]" : l_ac*ac_res[0] + l_dc*dc_res[0],
            "AC Cabling Mass [kg]" : l_ac*ac_res[0],
            "DC Cabling Mass [kg]" : l_dc*dc_res[0],
            "AC Cable Cross-Section [mm^2]" : ac_res[-1],
            "DC Cable Cross-Section [mm^2]" : dc_res[-1],
        }

        message = f"Calculation Completed."
        QMessageBox.information(self, "Successfull Calculation", message, QMessageBox.Ok)

        self.cables_calculated = True

    def export_cable_results(self):
        if not self.cables_calculated:
            self.calculate_cables()
        os.chdir(self.output_dir)
        with open("./cabling_sizing_report.dat", "w") as myfile:
            json.dump(self.cabling_sizing_results, myfile)
        myfile.close()
        self.export_msg()
        os.chdir(self.home_dir)

    def calculate_battery(self):
        # battery_inputs = {key: field.text() for key, field in self.battery_inputs.items()}
        # print("Battery inputs:", battery_inputs)
        # # Add battery sizing calculation logic here

        p2cRatio = float(self.battery_inputs["Pack to Cell Gravimetric Energy Density Ratio [-]"].text())
        DoD = float(self.battery_inputs["Maximum Depth of Discharge [%]"].text())/100
        EoL = 1 - float(self.battery_inputs["Batteries End Of Life Capacity [%]"].text())/100
        P = float(self.battery_inputs["Maximum Power [kW]"].text())
        E = float(self.battery_inputs["Mission Energy [kWh]"].text())
        Se = float(self.battery_inputs["Battery Gravimetric Energy Density [kWh/kg]"].text())
        V = float(self.battery_inputs["System's Voltage [V]"].text())
        chrg_r = float(self.battery_inputs["Maximum Charge Rate [C]"].text())
        dis_r = float(self.battery_inputs["Maximum Discharge Rate [C]"].text())        

        self.battery_pack = battery_pack()

        if not self.configure_cell_input:
            self.battery_pack.cell_dimensions()
        else:
            self.battery_pack.cell_dimensions(*self.configure_cell_input)

        self.battery_pack.pack_dimensions(p2cRatio)
        self.battery_pack.operating_constraints(DoD, EoL)
        resAr = self.battery_pack.size_battery(P, E, Se, V, chrg_r, dis_r)

        pack_mass = resAr[0]
        pack_capacity = resAr[1]*resAr[2]*resAr[-3]*self.battery_pack.cell_V_nom*1e-3

        battery_pack_sizing_results = {
            "Pack Mass [kg]" : resAr[0],
            "Batteries in Series [-]" : resAr[1],
            "Batteries in Parallel [-]" : resAr[2],
            "Maximum Charging Power [kW]" : resAr[3],
            "Maximum Discharging Power [kW]" : resAr[4],
            "Time to fully charge a single cell [min]": resAr[5],
            "Time to fully discharge a single cell [min]": resAr[6],
            "Cell capacity [Ah]" : resAr[7],
            "Pack Gravimetric specific energy [kWh/kg]" : resAr[8],
            "Pack Capacity [kWh]" : pack_capacity,
            "Exit Code" : resAr[-1]
        }

        message = f"Calculation Completed."
        QMessageBox.information(self, "Successfull Calculation", message, QMessageBox.Ok)

        self.battery_calculated = True

        return battery_pack_sizing_results

    def export_battery_results(self):
        if not self.battery_calculated:     
            results = self.calculate_battery()

        os.chdir(self.output_dir)
        with open("battery_pack_sizing_report.dat", "w") as myfile:
            json.dump(results, myfile)
        myfile.close()
        self.export_msg()
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EPSConfigurator()
    window.show()
    sys.exit(app.exec_())
