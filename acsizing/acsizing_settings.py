import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel, QLineEdit, QPushButton, QComboBox

class AircraftSizingSettings(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aircraft Sizing Settings")
        self.setGeometry(100, 100, 800, 600)

        GEOMETRY = {'Main_Wing' : {
                                        'Taper' : "0.7",
                                        'Sweep' : "5.0",
                                        'Twist' : "-3.0",
                                        'Incidence' : "1.0", 
                                        'Dihedral' : "1.0",
                                        'Profile' : '"NACA4415"', 
                                        'Thickness' : "0.15",
                                        'Wetted2Reference_area_ratio' : "4.0",
                                        'KLD' : "11.0",
                                        'Moving Parts' : "2", 
                                        'ChordRatio' : "[0.2, 0.15]", 
                                        'SpanRatio' : "[0.5, 0.3]",
                                        },
                         'Horizontal_Tail' : {
                                        'AR' : "4.0",
                                        'Taper' : "0.9",
                                        'Sweep' : "10.0",
                                        'Twist' : "0.0",
                                        'Incidence' : "-3.0", 
                                        'Dihedral' : "0.0",
                                        'Profile' : '"NACA0012"', 
                                        'Thickness' : "0.15",
                                        'Moving Parts' : "1", 
                                        'ChordRatio' : "[0.25]", 
                                        'SpanRatio' : "[0.8]",
                                        },
                         'Vertical_Tail' : {
                                        'AR' : "1.0",
                                        'Taper' : "0.8",
                                        'Sweep' : "45.0",
                                        'Twist' : "0.0",
                                        'Incidence' : "0.0", 
                                        'Dihedral' : "0.0",
                                        'Profile' : '"NACA0012"', 
                                        'Thickness' : "0.15",
                                        'Moving Parts' : "1", 
                                        'ChordRatio' : "[0.3]", 
                                        'SpanRatio' : "[0.8]",
                                        },
                         'Fuselage' :   {
                                        'a_fus' : "0.169",
                                        'c_fus' : "0.51",
                                        'f' : "7",
                                        'cvt' : "0.05",
                                        'cht' : "0.9",
                                        'Fuselage XSection' : '"Ellipse"',
                                        },
                         'Landing_Gear' : {
                                        'No_wheels_fr' : "1",
                                        'No_wheels_r' : "2",
                                        'fr2r_wheels_ratio' : "0.9",
                                        'A' : "5.3",
                                        'B' : "0.315",
                                        'C' : "0.39",
                                        'D' : "0.48",
                                        },
                        'General Settings' : {
                                        "rho_at_denver_mks" : "0.974",
                                        "tail" : "0", # 0 for T - Tail, 1 for inverted T - Tail
                                        "Vtakeoff_Vstall" : "1.1",
                                        "W_S_typical" : "195.0",
                                        "load_factor" : "3.1",
                                        "g" : "9.81",
                                        },
                        'Power Loading Parameters' : {
                                        'a' : "0.016",
                                        'c' : "0.5",
                                        'P_W_table' : "0.33",
                                        'S_a' : "183.0",
                                        }
                        }

        # Map inner keys to more readable labels
        label_mapping = {
            'AR': 'Aspect Ratio',
            'Taper': 'Taper Ratio',
            'Twist' : 'Wing Twist angle',
            'Incidence' : 'Wing Incidence angle',
            'Dihedral' : 'Wing Dihedral angle',
            'Profile' : 'NACA Airfoil Proifile',
            'Sweep': 'Sweep Angle',
            'Thickness': 'Thickness Ratio',
            'Wetted2Reference_area_ratio': 'Wetted Area Ratio',
            'KLD': 'Lift to Drag ratio K-Value',
            'Moving Parts': 'Number of Moving Parts',
            'ChordRatio': 'Chord Ratio',
            'SpanRatio': 'Span Ratio',
            'Relative Position X': 'Relative Position X',
            'Relative Position Z': 'Relative Position Z',
            'Weight': 'Weight',
            'No_GT': 'Number of Gearboxes',
            'Engine Length': 'Engine Length',
            'Engine Diameter': 'Engine Diameter',
            'Relative Position X Eng': 'Relative Position X (Engine)',
            'Relative Position Y Eng': 'Relative Position Y (Engine)',
            'Relative Position Z Eng': 'Relative Position Z (Engine)',
            'Relative Position X': 'Relative Position X',
            'Relative Position Z': 'Relative Position Z',
            'rho_at_denver_mks' : 'Air density @ Denver',
            'tail' : 'Empennage shape',
            'Vtakeoff_Vstall' : 'Take-off to stall speed ratio',
            'W_S_typical' : 'Typical wing loading value [kg/m2]',
            'g' : 'Gravitational acceleration [m/s2]',
            'No_wheels_fr' : 'Number of wheels in front mechanism',
            'No_wheels_r' : 'Number of wheels in rear mechanism',
            'fr2r_wheels_ratio' : 'Front wheels to Rear wheels ratio [0.6 - 1]',
            'A' : 'Landing gear diameter regression factor A',
            'B' : 'Landing gear diameter regression factor B',
            'C' : 'Landing gear width regression factor C',
            'D' : 'Landing gear width regression factor D',
            'a' : 'Power loading regression factor a',
            'c' : 'Power loading regression factor c',
            'P_W_table' : 'Empirical power loading from data',
            'S_a' : 'Obstacle clearance distance [m]',
            'a_fus' : 'Fuselage regression factor a',
            'c_fus' : 'Fuselage regression factor c',
            'f' : 'Fuselage fitness factor',
            'cvt' : 'Vertical tail volume factor',
            'cht' : 'Horizontal tail volume factor',
            'load_factor' : 'Structural load factor',
            'Fuselage XSection' : "Fuselage Cross-Sectional Shape"
        }

        self.settings = GEOMETRY
        self.unsaved_changes = False  # Track if changes are made

        layout = QVBoxLayout(self)

        # Create a tab widget to hold the tabs
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Create tabs for each key in the dictionary
        for key, inner_dict in self.settings.items():
            tab = QWidget()
            self.tab_widget.addTab(tab, key)

            tab_layout = QVBoxLayout(tab)

            # Add input fields based on inner dictionary items
            for inner_key, default_value in inner_dict.items():
                input_layout = QHBoxLayout()
                tab_layout.addLayout(input_layout)

                # Create labels based on the inner key and use a more readable label if available
                label_text = inner_key
                if inner_key in label_mapping:
                    label_text = label_mapping[inner_key]

                label = QLabel(label_text)
                label.setFixedWidth(300)
                input_layout.addWidget(label)

                if "tail" in inner_key:
                    input_field = QComboBox()
                    input_field.setObjectName(inner_key)
                    input_field.addItems(["T-Tail", "Inverted T-Tail"])
                    input_field.setCurrentIndex(0)
                    # Connect a signal to track changes in the input fields
                    input_field.currentIndexChanged.connect(self.enable_apply_button)  
                else:
                    input_field = QLineEdit(str(default_value))
                    input_field.setObjectName(inner_key)
                    # Connect a signal to track changes in the input fields
                    input_field.textChanged.connect(self.enable_apply_button)

                input_layout.addWidget(input_field)           

        # Create a bottom layout for buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.apply_button = QPushButton("Apply")  # Create a class-level variable

        # Initially disable the Apply button
        self.apply_button.setEnabled(False)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.apply_changes)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)

    def enable_apply_button(self):
        # Enable Apply button when any changes are made
        self.unsaved_changes = True
        self.apply_button.setEnabled(True)

    def apply_changes(self):
        for tab_index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(tab_index)
            tab_name = self.tab_widget.tabText(tab_index)

            for inner_key, default_value in self.settings[tab_name].items():
                input_field = tab.findChild(QLineEdit, inner_key)
                if input_field:
                    # Update the value in the settings dictionary
                    new_value = input_field.text()
                    # Update the value in the settings dictionary
                    self.settings[tab_name][inner_key] = new_value
                input_field_1 = tab.findChild(QComboBox, inner_key)
                if input_field_1:
                    new_value = input_field_1.currentIndex()
                    self.settings[tab_name][inner_key] = str(new_value)

        self.unsaved_changes = False
        self.apply_button.setEnabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)    
    dialog = AircraftSizingSettings()
    dialog.show()
    sys.exit(app.exec_())
