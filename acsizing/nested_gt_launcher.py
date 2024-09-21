import sys
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, QHBoxLayout

class NestedGTlauncher(QDialog):
    def __init__(self):
        super().__init__()

        # Initialize the bsfc dictionary here
        self.bsfc_defaults = {
            'Taxi-out': '0.4',
            'Take-off': '0.32607',
            'Climb': '0.3346',
            'Cruise': '0.3346',
            'Descent': '0.3954',
            'Approach and Landing': '0.3954',
            'Taxi-in': '0.4',
            'Overshoot': '0.32607',
            'DivClimb': '0.3346',
            'DivCruise': '0.3346',
            'DivDescent': '0.3954',
            'Hold': '0.3954',
            'Div Approach and Landing': '0.3954',
        }

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Configure EIS 2014 GT')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # Create labels and input fields for each input
        self.createInputField(layout, "Fuel Lower Heating Value (kJ/kg):", "fuel_LHV", "43e3")
        self.createInputField(layout, "Core Mass (kg):", "mass", "233.5")
        self.createInputField(layout, "Fuel Density (kg/L):", "fuel_rho", "0.804")
        self.createInputField(layout, "Fuel Energy Density (kWh/L):", "fuel_energy_density", "9.6")

        # Create labels and input fields for the bsfc dictionary
        bsfc_label = QLabel("Brake Specific Fuel Consumption (kg/kWh)")
        # layout.addWidget(bsfc_label)
        self.bsfc_inputs = {}
        for key, value in self.bsfc_defaults.items():
            my_str = key
            if "Div" in key:
                my_str = key.replace("Div", "Diversion ")
            self.createInputField(layout, "{1} @ {0}".format(my_str, bsfc_label.text()), f"bsfc_{key}", value)


        self.confirm_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        self.confirm_button.clicked.connect(self.on_accept)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def createInputField(self, layout, label_text, attribute_name, default_value=""):
        label = QLabel(label_text)
        input_field = QLineEdit()
        input_field.setText(default_value)
        setattr(self, attribute_name, input_field)
        layout.addWidget(label)
        layout.addWidget(input_field)

    def on_accept(self):
        # Retrieve values from input fields
        self.fuel_LHV_GUI = float(self.fuel_LHV.text())
        self.mass_GUI = float(self.mass.text())
        self.fuel_rho_GUI = float(self.fuel_rho.text())
        self.fuel_energy_density_GUI = float(self.fuel_energy_density.text())

        self.bsfc_GUI = {}
        for key in self.bsfc_defaults:
            self.bsfc_GUI[key] = float(getattr(self, f"bsfc_{key}").text())

        self.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NestedGTlauncher()
    window.show()
    sys.exit(app.exec_())
