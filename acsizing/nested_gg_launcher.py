import sys
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, QHBoxLayout, QCheckBox

class NestedGGlauncher(QDialog):
    def __init__(self):
        super().__init__()

        # Initialize the bsfc dictionary here
        self.operating_points = ['Taxi-out', 'Take-off', 'Climb', 'Cruise', 'Descent', 'Approach and Landing', 
                'Taxi-in', 'Overshoot', 'DivClimb', 'DivCruise', 'DivDescent',
                'Hold', 'Div Approach and Landing']

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Configure Gas Generator')
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()

        # Create labels and input fields for each input
        self.createInputField("Fuel Lower Heating Value (kJ/kg):", "fuel_LHV", "43e3")
        self.createInputField("Core Mass (kg):", "mass", "256")
        self.createInputField("Fuel Density (kg/L):", "fuel_rho", "0.804")
        self.createInputField("Fuel Energy Density (kWh/L):", "fuel_energy_density", "9.6")
        self.createInputField("Design Point Efficiency [-]", "efficiency", "0.4")
        # checkbox_layout = QHBoxLayout()
        # self.const_eff = QCheckBox("Constant Efficiency")
        # self.var_eff = QCheckBox("Specify Efficiency for each point")
        # checkbox_layout.addWidget(self.const_eff)
        # checkbox_layout.addWidget(self.var_eff)

        # self.layout.addLayout(checkbox_layout)

        # self.const_eff.toggled.connect(self.constant_efficiency_inputs)
        # self.var_eff.toggled.connect(self.variable_efficiency_inputs)

        self.confirm_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        self.confirm_button.clicked.connect(self.on_accept)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

    def constant_efficiency_inputs(self):
        self.createInputField("Efficiency", "const_efficiency", "0.4")

    def variable_efficiency_inputs(self):
        for key in self.operating_points:
            self.createInputField("Efficiency @ {0}".format(key), f"efficiency_{key}", "0.4")

    def createInputField(self, label_text, attribute_name, default_value=""):
        label = QLabel(label_text)
        input_field = QLineEdit()
        input_field.setText(default_value)
        setattr(self, attribute_name, input_field)
        self.layout.addWidget(label)
        self.layout.addWidget(input_field)

    def on_accept(self):
        # Retrieve values from input fields
        self.fuel_LHV_GUI = float(self.fuel_LHV.text())
        self.mass_GUI = float(self.mass.text())
        self.fuel_rho_GUI = float(self.fuel_rho.text())
        self.fuel_energy_density_GUI = float(self.fuel_energy_density.text())
        self.efficiency_GUI = float(self.efficiency.text())

        self.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NestedGGlauncher()
    window.show()
    sys.exit(app.exec_())
