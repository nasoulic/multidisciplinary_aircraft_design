import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton

class OperationModeDialog(QDialog):
    def __init__(self, ac_config):
        super().__init__()
        self.setWindowTitle("Operational Modes Configurator")
        self.setGeometry(100, 100, 600, 400)  # Increased window size

        self.el_mode = []
        self.conv_mode = []

        # Create a mapping dictionary for mission data labels
        self.mission_data_mapping = {
            'Taxi-out': 'Taxi Out',
            'Take-off': 'Takeoff',
            'Climb': 'Climb',
            'Cruise': 'Cruise',
            'Descent': 'Descent',
            'Approach and Landing': 'Approach and Landing',
            'Overshoot': 'Overshoot',
            'DivClimb': 'Diversion Climb',
            'DivCruise': 'Diversion Cruise',
            'DivDescent': 'Diversion Descent',
            'Hold': 'Hold',
            'Div Approach and Landing': 'Diversion Approach and Landing',
            'Taxi-in': 'Taxi In',
        }

        self.aircraft_configuration = ac_config  # Initialize aircraft configuration

        layout = QVBoxLayout(self)

        # Add "Load Default Strategy" button
        load_default_button = QPushButton("Load Default Strategy")
        layout.addWidget(load_default_button)

        # Connect the button to the load_default_strategy method
        load_default_button.clicked.connect(self.load_default_strategy)

        # Create the header row
        header_layout = QHBoxLayout()
        layout.addLayout(header_layout)
        header_labels = ["Mission Phase", "Conventional Mode", "Electric Mode", "Hybrid Mode"]
        for label_text in header_labels:
            header_label = QLabel(label_text)
            header_layout.addWidget(header_label)

        # Add mission phases and checkboxes with unique names
        for name, phase_data in self.mission_data_mapping.items():
            row_layout = QHBoxLayout()
            layout.addLayout(row_layout)

            # Mission Phase Name
            mission_phase_label = QLabel(phase_data)  # Use the mapped label
            mission_phase_label.setFixedWidth(200)  # Set a fixed width for the label
            row_layout.addWidget(mission_phase_label)

            # Checkboxes for Conventional, Electric, and Hybrid Modes
            for mode in ["Conventional", "Electric", "Hybrid"]:
                checkbox = QCheckBox()
                checkbox.setObjectName(f"checkbox_{name}_{mode}")  # Set unique names
                row_layout.addWidget(checkbox)

        # Add OK and Cancel buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")

        self.ok_button.clicked.connect(self.on_ok_button)
        self.cancel_button.clicked.connect(self.on_cancel_button)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

    def load_default_strategy(self):
        if self.aircraft_configuration == "Parallel":
            el_mode = []
            conv_mode = ['Taxi-out', 'Descent', 'Approach and Landing', 'Taxi-in', 'DivDescent', 'Div Approach and Landing']
        elif self.aircraft_configuration == "Series":
            el_mode = ['Taxi-out', 'Taxi-in']
            conv_mode = ['Descent', 'Approach and Landing', 'DivDescent', 'Hold', 'Div Approach and Landing']
        elif "Parallel" in self.aircraft_configuration and "Series" in self.aircraft_configuration:
            el_mode = ['Taxi-out', 'Taxi-in']
            conv_mode = ['Descent', 'Approach and Landing', 'DivDescent', 'Hold', 'Div Approach and Landing']

        for name in self.mission_data_mapping.keys():
            for mode in ["Conventional", "Electric", "Hybrid"]:
                checkbox = self.findChild(QCheckBox, f"checkbox_{name}_{mode}")
                checkbox.setChecked(False)
        
        convmode = "Conventional"
        elmode = "Electric"
        hmode = 'Hybrid'
        # Iterate through the checkboxes and check/uncheck them based on the strategy
        for name, phase_data in self.mission_data_mapping.items():
            if self.aircraft_configuration == "Conventional":
                checkbox = self.findChild(QCheckBox, f"checkbox_{name}_{convmode}")
                checkbox.setChecked(True)
            else:
                if name in el_mode:
                    checkbox = self.findChild(QCheckBox, f"checkbox_{name}_{elmode}")
                    checkbox.setChecked(True)
                elif name in conv_mode:
                    checkbox = self.findChild(QCheckBox, f"checkbox_{name}_{convmode}")
                    checkbox.setChecked(True)
                else:
                    checkbox = self.findChild(QCheckBox, f"checkbox_{name}_{hmode}")
                    checkbox.setChecked(True)

    def on_cancel_button(self):
        self.close()
    
    def on_ok_button(self):
        self.el_mode = []
        self.conv_mode = []
        convmode = "Conventional"
        elmode = "Electric"
        if "Conventional" not in self.aircraft_configuration:
            for name, phase_data in self.mission_data_mapping.items():        
                checkbox = self.findChild(QCheckBox, f"checkbox_{name}_{convmode}")
                if bool(checkbox.isChecked()):
                    self.conv_mode.append(name)
                checkbox = self.findChild(QCheckBox, f"checkbox_{name}_{elmode}")
                if bool(checkbox.isChecked()):
                    self.el_mode.append(name)
        else:
            for name in self.mission_data_mapping.keys():
                self.conv_mode.append(name)

        self.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = OperationModeDialog("Conventional")
    dialog.show()
    sys.exit(app.exec_())
