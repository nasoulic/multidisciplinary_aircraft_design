import sys
import json
from PyQt5.QtWidgets import QWidget, QApplication, QDialog, QVBoxLayout, QPushButton, QFileDialog, QLabel, QLineEdit, QHBoxLayout, QScrollArea
from PyQt5.QtCore import Qt, QSize

class TopLevelAircraftRequirementsForm(QDialog):
    def __init__(self):
        super().__init__()
        self.tlar_data = {}
        self.tlar_notes = {
                        'PAX' : 'The maximun number of passengers',
                        'Crew' : 'Crew members number',
                        'Passenger weight [kg]' : 'The weight per passenger, including luggage. Typically 100kg are 87kg plus 13kg luggage.',
                        'Mission range [nm]': 'The mission range refers to the distance the aircraft should be able to travel\n in nautical miles without needing to refuel. Enter the desired mission\n range in nautical miles.',
                        'Reserves range [nm]': 'The reserves range represents additional distance in nautical miles that the\n aircraft should be capable of traveling as a safety buffer. Enter the\n desired reserves range in nautical miles.',
                        'End of Take-Off Altitude [ft]': 'This is the altitude, in feet, at which the take-off phase of the flight\n ends. Enter the desired end of take-off altitude in feet.',
                        'Take-Off Field Length [m]' : 'Set the minimum take-off field length in meters at which the aircraft\nwill be able to take-off',
                        'Landing Field Length [m]' : 'Set the minimum landing field length in meters at which the aircraft\nwill be able to land',
                        'Cruise Altitude [ft]': 'The cruise altitude is the optimal or typical altitude at which the aircraft will\n operate during its main cruising phase. Enter the desired cruise altitude in feet.',
                        'Diversion Altitude [ft]': 'The cruise altitude is the optimal or typical altitude at which the aircraft will\n operate during its diversion cruising phase. Enter the desired cruise altitude in feet.',
                        'Loiter Altitude [ft]': 'Loiter altitude is the altitude at which the aircraft will hold or loiter during\n specific mission phases. Enter the desired loiter altitude in feet.',
                        'Climb Mach Number [-]': 'The climb Mach number represents the speed of the aircraft during its climb phase.\n Enter the desired climb Mach number.',
                        'Cruise Mach Number [-]': 'The cruise Mach number represents the speed of the aircraft during its main cruising\n phase. Enter the desired cruise Mach number.',
                        'Descend Mach Number [-]': 'The descend Mach number represents the speed of the aircraft during its Descend phase.\n Enter the desired Descend Mach number.',
                        'Loiter Mach Number [-]': 'The loiter Mach number represents the speed of the aircraft during loitering phases.\n Enter the desired loiter Mach number.',
                        'Max Climb Angle [deg]': 'This is the maximum angle at which the aircraft can climb relative to the horizontal plane,\n expressed in degrees. Enter the maximum climb angle in degrees.',
                        'Max Dive Angle [deg]': 'The maximum dive angle is the steepest angle of Descend that the aircraft can\n safely achieve, expressed in degrees. Enter the maximum dive angle in degrees.',
                        'Target Climb Angle [deg]': 'This is the target angle at which the aircraft can climb relative to the horizontal plane,\n expressed in degrees. Enter the target climb angle in degrees.',
                        'Target Dive Angle [deg]': 'The target dive angle is the steepest angle of Descend that the aircraft can\n safely achieve, expressed in degrees. Enter the target dive angle in degrees.',
                        'Target Aspect Ratio [-]': "The aspect ratio is a measure of the wing's efficiency and is calculated as\n the wingspan divided by the mean chord length. Enter the target aspect ratio.",
                        'Target Max Lift Coefficient [-]': "The maximum lift coefficient is a measure of the wing's lifting\n capability. Enter the target maximum lift coefficient.",
                        }
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Top-Level Aircraft Requirements')
        self.setGeometry(100, 100, 400, 800)
        
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        self.label = QLabel('Choose an option:')
        self.layout.addWidget(self.label)

        self.button_load_json = QPushButton('Load TLARs from JSON')
        self.button_load_json.clicked.connect(self.load_json)
        self.button_load_json.setToolTip("Load existing TLARs file.")
        self.layout.addWidget(self.button_load_json)

        # self.button_import_manually = QPushButton('Import TLARs Manually')
        # self.button_import_manually.clicked.connect(self.import_manually)
        # self.button_import_manually.setToolTip("Import manually the TLARs.")
        # self.layout.addWidget(self.button_import_manually)

        self.button_export_json = QPushButton('Export to JSON')
        self.button_export_json.clicked.connect(self.export_json)
        self.button_export_json.setToolTip("Export TLARs to file.")
        self.layout.addWidget(self.button_export_json)
        self.button_export_json.setEnabled(False)

        self.tlar_data = {
            'PAX' : str(19),
            'Crew' : str(1),
            'Passenger weight [kg]' : str(100),
            'Mission range [nm]': str(400.),
            'Reserves range [nm]': str(100.),
            'End of Take-Off Altitude [ft]': str(1500.),
            'Take-Off Field Length [m]' : str(1000.),
            'Landing Field Length [m]' : str(900.),
            'Cruise Altitude [ft]': str(10000.),
            'Diversion Altitude [ft]': str(10000.),
            'Loiter Altitude [ft]': str(2000.),
            'Climb Mach Number [-]': str(0.186),
            'Cruise Mach Number [-]': str(0.35),
            'Descend Mach Number [-]': str(0.186),
            'Loiter Mach Number [-]': str(0.165),
            'Max Climb Angle [deg]': str(10.),
            'Max Dive Angle [deg]': str(10.),
            'Target Climb Angle [deg]': str(7.),
            'Target Dive Angle [deg]': str(2.),
            'Target Aspect Ratio [-]': str(11.),
            'Target Max Lift Coefficient [-]': str(2.4),
        }
        self.display_tlar_data(self.tlar_data)
        self.button_export_json.setEnabled(True)

        self.central_widget.setLayout(self.layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.central_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.on_ok_clicked)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)
        

    def load_json(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        json_file, _ = QFileDialog.getOpenFileName(self, 'Load TLARs from JSON', '', 'JSON Files (*.json);;All Files (*)', options=options)
        
        if json_file:
            with open(json_file, 'r') as f:
                self.tlar_data = json.load(f)
                self.display_tlar_data(self.tlar_data)
                self.button_export_json.setEnabled(True)

    def import_manually(self):
        self.tlar_data = {
            'Mission range [nm]': str(400.),
            'Reserves range [nm]': str(100.),
            'End of Take-Off Altitude [ft]': str(1500.),
            'Cruise Altitude [ft]': str(10000.),
            'Diversion Altitude [ft]': str(10000.),
            'Loiter Altitude [ft]': str(2000.),
            'Climb Mach Number [-]': str(0.186),
            'Cruise Mach Number [-]': str(0.35),
            'Descend Mach Number [-]': str(0.186),
            'Loiter Mach Number [-]': str(0.165),
            'Max Climb Angle [deg]': str(10.),
            'Max Dive Angle [deg]': str(10.),
            'Target Climb Angle [deg]': str(7.),
            'Target Dive Angle [deg]': str(2.),
            'Target Aspect Ratio [-]': str(11.),
            'Target Max Lift Coefficient [-]': str(2.4),
        }
        self.display_tlar_data(self.tlar_data)
        self.button_export_json.setEnabled(True)

    def export_json(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        json_file, _ = QFileDialog.getSaveFileName(self, 'Export TLARs to JSON', '', 'JSON Files (*.json);;All Files (*)', options=options)
        
        if json_file:
            with open(json_file, 'w') as f:
                json.dump(self.tlar_data, f, indent=4)

    def display_tlar_data(self, tlar_data):
        # self.clear_layout()
        for key, value in tlar_data.items():
            label = QLabel(key)
            line_edit = QLineEdit(value)
            note = self.tlar_notes.get(key, "")
            line_edit.textChanged.connect(lambda text, key=key: self.update_tlar_data(key, text))
            line_edit.setToolTip(note)
            self.layout.addWidget(label)
            self.layout.addWidget(line_edit)

    def on_ok_clicked(self):
        self.accept() # Close the dialog and return QDialog.Accepted

    def on_cancel_clicked(self):
        self.reject() # Close the dialog and return QDialog.Rejected

    def update_tlar_data(self, key, value):
        self.tlar_data[key] = value

    def clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TopLevelAircraftRequirementsForm()
    window.show()
    sys.exit(app.exec_())
