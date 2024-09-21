import sys, os
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QWidget
from PyQt5.QtGui import QPixmap
from flight_envelope.flight_envelope import Flight_Envelope, plot_flight_envelope

class FlightEnvelopeCalculator(QDialog):
    def __init__(self, home_dir, output_dir):
        super().__init__()

        self.window1 = None

        self.home_dir = home_dir
        self.output_dir = output_dir
        self.inputs = {
                        'MTOW': "8489.0",
                        'Sref': "24.61",
                        'Cruise Speed': "115",
                        'Sea level density': "1.225",
                        'CLmax': "2.8",
                        'CLmin': "-1.0",
                        'Limit load factor': "3.1",
                        'Gravity': "9.81",
                        'Lift curve slope': "5.8",
                        'Wing MAC': "1.47",
                        'Cruise Altitude': "10000.0"
                    }

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Flight Envelope Calculator")
        self.setGeometry(100, 100, 400, 400)

        layout = QVBoxLayout()

        label_descriptions = {
            'MTOW': 'Maximum Takeoff Weight (kg):',
            'Sref': 'Reference Wing Area (m^2):',
            'Cruise Speed': 'Cruise Speed (m/s):',
            'Sea level density': 'Sea Level Air Density (kg/m^3):',
            'CLmax': 'Maximum Lift Coefficient:',
            'CLmin': 'Minimum Lift Coefficient:',
            'Limit load factor': 'Limit Load Factor:',
            'Gravity': 'Gravitational acceleration (m/s^2):',
            'Lift curve slope': 'Lift Curve Slope (1/rad):',
            'Wing MAC': 'Wing Mean Aerodynamic Chord (m):',
            'Cruise Altitude': 'Cruise Altitude (ft):'
        }

        self.line_edits = {}

        for key, description in label_descriptions.items():
            label = QLabel(description)
            line_edit = QLineEdit()
            line_edit.setText(str(self.inputs[key]))
            layout.addWidget(label)
            layout.addWidget(line_edit)
            self.line_edits[key] = line_edit

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)

        self.calculate_envelope = QPushButton("Calculate")
        self.calculate_envelope.clicked.connect(self.calculate_flight_envelope)

        self.show_envelope = QPushButton("Show Envelope")
        self.show_envelope.setEnabled(False)
        self.show_envelope.clicked.connect(self.show_flight_envelope)

        button_layout_1 = QHBoxLayout()
        button_layout_1.addWidget(self.calculate_envelope)
        button_layout_1.addWidget(self.show_envelope)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout_1)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def calculate_flight_envelope(self):
        # Retrieve the values from the QLineEdit widgets
        for key, line_edit in self.line_edits.items():
            self.inputs[key] = float(line_edit.text())

        # Perform flight envelope calculation here
        # You can access the updated values in self.inputs
        self.flight_envelope = Flight_Envelope(self.inputs)
        self.envelope = self.flight_envelope.get_flight_envelope()
        self.show_envelope.setEnabled(True)


    def show_flight_envelope(self):
        
        os.chdir(self.output_dir)

        plot_flight_envelope(self.envelope, plot_gust = True, plot_verticals = True, print_labels = False)
        if not self.window1:
            self.window1 = ImageLoader()
            self.window1.load_image("envelope.png")
        self.window1.show()

        os.chdir(self.home_dir)

        # image_view = ImageViewer(os.path.join(self.home_dir, "results", "standalone", "flight_envelope", "envelope.png"),
        #                                 resolution = "narrow")
        # image_view.show()

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
    window = FlightEnvelopeCalculator()
    window.show()
    sys.exit(app.exec_())
