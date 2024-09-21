import sys
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, QHBoxLayout

class NestedProplauncher(QDialog):
    def __init__(self):
        super().__init__()

        # Initialize the propeller efficiency dictionary here
        self.eta_p = {
            'Taxi-out' : "80",
            'Take-off' : "80",
            'Climb' : "77",
            'Cruise' : "78",
            'Descent' : "80",
            'Approach and Landing' : "66",
            'Taxi-in' : "80",
            'Overshoot' : "80",
            'DivClimb' : "77",
            'DivCruise' : "78",
            'DivDescent' : "80",
            'Hold' : "66",
            'Div Approach and Landing' : "66",
            }

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Configure GT Propeller Efficiency')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # Create labels and input fields for the bsfc dictionary
        etap_label = QLabel("Propeller efficiency [%]")
        # layout.addWidget(bsfc_label)
        self.eta_p_inputs = {}
        for key, value in self.eta_p.items():
            my_str = key
            if "Div" in key:
                my_str = key.replace("Div", "Diversion ")
            self.createInputField(layout, "{1} @ {0}".format(my_str, etap_label.text()), f"etap_{key}", value)


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
        self.eta_p_inputs_GUI = {}
        for key in self.eta_p:
            self.eta_p_inputs_GUI[key] = float(getattr(self, f"etap_{key}").text())/100

        self.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NestedProplauncher()
    window.show()
    sys.exit(app.exec_())
