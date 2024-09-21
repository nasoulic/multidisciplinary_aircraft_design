import sys, os
from tlars.tlars import TopLevelAircraftRequirementsForm
from tms.tms_modeler_launcher import TMSConfigApp
from aircraft_visualization.launch_openvsp import launch_openvsp
from aircraft_visualization.VSP_Objects import export2CAD
from doc.doc_launcher import AircraftCostCalculator
from lca.lca_launcher import AircraftLifeCycleEval
from acsizing.acsizing_launcher import AircraftSizingDialog
from flight_envelope.flight_envelope_launcher import FlightEnvelopeCalculator
from eps.eps_launcher import EPSConfigurator
from gasturbine.gas_turbine_launcher import GasTurbineConfigurator
from onepass_design.onepass_launcher import OnePassDialog
from uncertainty_analysis.uncertainty_analysis_launcher import UncertaintyAnalysisDialog
from doe.doe_launcher import DoEDialog
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QFrame,
    QAction, QFileDialog, QMessageBox, QShortcut, QTabWidget, QDesktopWidget)
from PyQt5.QtGui import QPixmap, QKeySequence
from PyQt5.QtCore import Qt, QSize
import openvsp as vsp
from aircraft_visualization.create_aircraft import build_aircraft

class AircraftDesignMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multidisciplinary Novel Aircraft Design")  
        self.setGeometry(100, 100, 800, 600)

        # save home directory
        self.home_dir = os.getcwd()

        # Create a tab widget
        self.tab_widget = QTabWidget()

        # Create a widget for the "Standalone Tools" tab
        standalone_tools_tab = QWidget()

        # Create a widget for the "One Pass Design" tab
        one_pass_design_tab = QWidget()

        # Create a widget for the "Uncertainty Quantification Analysis" tab
        uncertainty_analysis_tab = QWidget()

        # Create a widget for the "Design of Experiment" tab
        doe_tab = QWidget()

        # Set up the layout for the "Standalone Tools" tab
        standalone_layout = QHBoxLayout()
        
        self.general_info_label = QLabel("Welcome to the <b>Multidisciplinary Novel Aircraft Design</b> tool!")
        self.general_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.general_info_label.setWordWrap(True)
        # standalone_layout.addWidget(self.general_info_label)

        # self.layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.general_info_label)

        self.figure_placeholder = QLabel()
        self.figure_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Load the image using QPixmap and set it to the QLabel
        original_pixmap = QPixmap("./img/framework.png")
        target_size = QSize(1200, 1200)
        scaled_pixmap = original_pixmap.scaled(target_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
        self.figure_placeholder.setPixmap(scaled_pixmap)
        # standalone_layout.addWidget(self.figure_placeholder)

        left_layout.addWidget(self.figure_placeholder)

        left_container = QFrame()
        left_container.setLayout(left_layout)
        # self.layout.addWidget(left_container)
        standalone_layout.addWidget(left_container)

        button_layout = QVBoxLayout()
        self.button_names = [
            "TLARs Configurator", "GT Configurator", "EPS Configurator", "TMS Configurator",
            "Aircraft Sizing Configurator", "LCA Calculator", "DOC Calculator", "Flight Envelope Calculator", "Aircraft Builder",
            "Aircraft Viewer", "Export Aircraft CAD", ]
            # "Aircraft Stability Calculator"
            # ]

        self.button_tooltips = {
            'TLARs Configurator': 'Click this button to open the TLARs (Top-Level\nAircraft Requirements) Configurator. This tool\n allows you to configure and manage the top-level\nrequirements for your aircraft. You can load\nexisting TLARs from a JSON file, import TLARs\nmanually, edit them, and export them back to\nJSON.It also provides helpful tooltips for each\ninput field to guide you in providing the\nnecessary information.',
            'Flight Envelope Calculator' : 'Click this button to launch the aircraft Flght\nEnvelope configurator of an existing \naircraft design.',
            'GT Configurator': 'Click this button to open the GT (Gas Turbine) Configurator.\n This tool allows you to configure the gas turbine engine for your aircraft.\n You can specify engine parameters, performance characteristics, and more.',
            'EPS Configurator': 'Click this button to open the EPS (Electrical Power System) Configurator.\n This tool allows you to configure the electrical power system for your aircraft.\n You can specify power generation, distribution, and management options.',
            'TMS Configurator': 'The main application window for configuring and analyzing a\nThermal Management System (TMS) and a Heat Exchanger (HEX).\nUsers can configure branches and the HEX, toggle forced\nconvection and laminar flow, and trigger an analysis.',
            'Aircraft Sizing Configurator': 'Click this button to perform aircraft sizing calculations.\n You can specify design parameters and constraints to determine the optimal size of your aircraft.',
            'LCA Calculator': 'Click this button to evaluate the Life Cycle Assessment (LCA) of your aircraft design.\n LCA considers environmental impacts throughout the aircraft life cycle.',
            'DOC Calculator': 'This application allows you to calculate\nthe annual operating costs of an aircraft\nbased on various input parameters. You\n can enter details related to general\n operating conditions, energy costs, labor costs,\n aircraft specifications, and capital costs. After\n inputting the necessary data, you can use\n the "Calculate" button to compute\n the operating costs. Additionally, you can\n load input data from a JSON file\n using the "Read Inputs from File" button\n or export your input data as\n a JSON file using the "Export Inputs" button.',
            'Aircraft Builder' : 'This function creates and exports the aircaft geometry files\nfrom the aircraft sizing output file\nand opens it is OpenVSP',
            'Aircraft Viewer': 'Click this button to view the current aircraft design.\n You can visualize the configuration and design components.',
            'Export Aircraft CAD': 'Click this button to export the aircraft design in various file formats.\n Supported formats include IGS and STEP for 3D modeling and exchange.',
            }
            # 'Aircraft Stability Calculator' : "Click this button to launch the aircraft stability calcualtor\n. Calculate the aircraft's neutral point, static marging, and perform the trim analysis.",
            # }

        self.buttons = {}                           # Dictionary to store button objects
        for button_name in self.button_names:
            button = QPushButton(button_name)
            button.setToolTip(self.button_tooltips.get(button_name, ""))
            button.setEnabled(False)                # Disable buttons initially
            button_layout.addWidget(button)
            self.buttons[button_name] = button      # Store the button object

        standalone_layout.addLayout(button_layout)

        self.buttons["TLARs Configurator"].clicked.connect(self.launch_tlars)
        self.buttons["Flight Envelope Calculator"].clicked.connect(self.launch_flight_envelope_configurator)
        self.buttons["TMS Configurator"].clicked.connect(self.configure_tms)
        self.buttons["Aircraft Viewer"].clicked.connect(self.launch_openvsp)
        self.buttons["DOC Calculator"].clicked.connect(self.launch_doc_calculator)
        self.buttons["LCA Calculator"].clicked.connect(self.launch_lca_calculator)
        self.buttons["Aircraft Sizing Configurator"].clicked.connect(self.launch_acsizing)
        self.buttons["Export Aircraft CAD"].clicked.connect(self.launch_export_cad_file)
        self.buttons["GT Configurator"].clicked.connect(self.launch_GT_modeler)
        self.buttons["EPS Configurator"].clicked.connect(self.launch_EPS_modeler)
        self.buttons["Aircraft Builder"].clicked.connect(self.build_aircraft_from_file)

        # Set the layout for the "Standalone Tools" tab
        standalone_tools_tab.setLayout(standalone_layout)

        # Add the "Standalone Tools" tab to the tab widget
        self.tab_widget.addTab(standalone_tools_tab, "Standalone Tools")

        # Add the "One Pass Design" tab to the tab widget
        self.tab_widget.addTab(one_pass_design_tab, "One Pass Design")

        # Add the "Uncertainty Analysis" tab to the tab widget
        self.tab_widget.addTab(uncertainty_analysis_tab, "Uncertainty Analysis")

        # Add the "Design of Experiment" tab to the tab widget
        self.tab_widget.addTab(doe_tab, "Design of Experiment")

        # Add the tab widget as the central widget of the main window
        self.setCentralWidget(self.tab_widget)

        one_pass_design_tab_layout = QVBoxLayout()
        one_pass_design_tab.setLayout(one_pass_design_tab_layout)

        one_pass_design_tab_layout.addWidget(OnePassDialog())

        uncertainty_analysis_tab_layout = QVBoxLayout()
        uncertainty_analysis_tab.setLayout(uncertainty_analysis_tab_layout)

        uncertainty_analysis_tab_layout.addWidget(UncertaintyAnalysisDialog())

        doe_tab_layout = QVBoxLayout()
        doe_tab.setLayout(doe_tab_layout)

        doe_tab_layout.addWidget(DoEDialog())

        # button_container = QFrame()
        # button_container.setLayout(button_layout)
        # self.layout.addWidget(button_container)

        # container = QWidget()
        # container.setLayout(self.layout)
        # self.setCentralWidget(container)

        self.init_menu_bar()

        self.file_opened = False                    # Flag to track whether a file is currently open
        self.tms_config_window = None               # Reference to TMSConfigApp instance
        self.tlars_window = None                    # Reference to TLARs instance
        self.doc_config_window = None               # Reference to DOC instance
        self.lca_config_window = None               # Reference to LCA instance
        self.acsizing_config_window = None          # Reference to acsizing instance
        self.flight_envelope_window = None          # Reference to flight envelope instance
        self.eps_config_window = None               # Reference to EPS instance
        self.gasturbine_config_window = None        # Reference to GT intsance

    def init_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        new_file_action = QAction("New File         (Ctrl + N)", self)
        open_file_action = QAction("Open File       (Ctrl + O)", self)
        save_file_action = QAction("Save File         (Ctrl + S)", self)
        export_file_action = QAction("Export File      (Ctrl + E)", self)
        exit_action = QAction("Exit                 (Ctrl + Q)", self)

        file_menu.addAction(new_file_action)
        file_menu.addAction(open_file_action)
        file_menu.addAction(save_file_action)
        file_menu.addAction(export_file_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("Help")
        info_action = QAction("Info", self)
        copyright_action = QAction("Copyright", self)

        help_menu.addAction(info_action)
        help_menu.addAction(copyright_action)

        exit_action.triggered.connect(self.close)
        info_action.triggered.connect(self.show_info)
        copyright_action.triggered.connect(self.show_copyright)

        open_file_action.triggered.connect(self.open_file_dialog)
        save_file_action.triggered.connect(self.save_file_dialog)
        export_file_action.triggered.connect(self.export_file_dialog)
        new_file_action.triggered.connect(self.new_file_dialog)

    def show_info(self):
        info_text = """
        Multidisciplinary Novel Aircraft Design Application
        
        Welcome to the Multidisciplinary Novel Aircraft Design application.
        This application provides a user-friendly interface to assist in various
        stages of aircraft design, configuration, and evaluation.
        
        Features:
        - Configure different components of the aircraft.
        - Perform sizing calculations for the aircraft.
        - Evaluate Life Cycle Assessment (LCA) and Direct Operating Costs (DOC).
        - View the aircraft design and export designs in different formats.
        - Configure the Thermal Management System (TMS).
        
        Explore the different menus and buttons to make the most of
        this application.
        For more detailed information, consult the user manual
        or help documentation.
        """
        QMessageBox.information(self, "Information", info_text)


    def show_copyright(self):
        msg = """
        Copyright © 2023
        Laboratory of Fluid Mechanics and Turbomachinery
        Aristotle University of Thessaloniki
        All rights reserved.

        Developer: Christos P. Nasoulis
        Contact e-mail: nasoulic@meng.auth.gr

        The author(s) disclaims all warranties with regard to this software,
        including all implied warranties of merchantability and fitness.
        In no event the author(s) shall be held liable for any special, indirect
        or consequential damages or any damages whatsoever resulting from
        loss of use, data or profits, either in an action of contract,
        negligence or other tortious action, arising out of or in connection
        with the use or performance of this software.

        This software has been developed as a partial fulfilment of the Developer's PhD.

        Data produced with this software may not be published or disclosed to
        any third party without the written authorisation of the author(s).        
        """
        QMessageBox.information(self, "Copyright", msg)

    def new_file_dialog(self):
        
        if not self.file_opened:
            self.file_opened = True         # File Opened for the first time
            self.enable_buttons()
        else:
            # If a file is already opened, prompt the user for confirmation.
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "Are you sure you want to start a new file? "
                "All unsaved changes will be lost.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.No:
                return  # User chose not to start a new file
            
            self.file_opened = False                    # Flag to track whether a file is currently open
            self.tms_config_window = None               # Reference to TMSConfigApp instance
            self.tlars_window = None                    # Reference to TLARs instance
            self.doc_config_window = None               # Reference to DOC instance
            self.lca_config_window = None               # Reference to LCA instance
            self.acsizing_config_window = None          # Reference to acsizing instance
            self.flight_envelope_window = None          # Reference to flight envelope instance
            self.eps_config_window = None               # Reference to EPS instance
            self.gasturbine_config_window = None        # Reference to GT intsance
            

    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            print(f"Opened file: {file_name}")
            self.file_opened = True         # Set the flag to True
            self.enable_buttons()           # Enable buttons

    def save_file_dialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save JSON File", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            print(f"Saved file: {file_name}")

    def export_file_dialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Export File", "", "IGS Files (*.igs);;STEP Files (*.step);;All Files (*)", options=options)
        if file_name:
            print(f"Exported file: {file_name}")

    def enable_buttons(self):
        for button_name, button in self.buttons.items():
            button.setEnabled(True)

    def configure_tms(self):
        self.navigate2path(["results", "standalone", "tms"])
        if not self.tms_config_window:
            self.tms_config_window = TMSConfigApp(self.home_dir, os.getcwd())
        self.tms_config_window.show()
        os.chdir(self.home_dir)

    def launch_tlars(self):
        ### Note to self: you can access the tlars after submitting the form via self.tlars_window.tlar_data
        if not self.tlars_window:
            self.tlars_window = TopLevelAircraftRequirementsForm()
        self.tlars_window.show()

    def build_aircraft_from_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Open VSP Input File", "", "dat files (*.dat);;All Files (*)", options=options)
        if file_name:
            path_comp = file_name.split("/")
            new_path = "/".join(path_comp[:-1])
            os.chdir(new_path)
            build_aircraft(file_name.replace(".dat", ""))
            vsp.ClearVSPModel()
            os.chdir(self.home_dir)
            launch_openvsp(os.path.join(new_path, "Assembly.vsp3"))

    def launch_openvsp(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Open VSP File", "", "VSP Files (*.vsp3);;All Files (*)", options=options)
        if file_name:
            launch_openvsp(os.path.relpath(file_name, self.home_dir))
            self.file_opened = True         # Set the flag to True

    def launch_doc_calculator(self):
        self.navigate2path(["results", "standalone", "doc"])
        if not self.doc_config_window:
            self.doc_config_window = AircraftCostCalculator(self.home_dir, os.getcwd())
        self.doc_config_window.show()
        os.chdir(self.home_dir)

    def launch_lca_calculator(self):
        self.navigate2path(["results", "standalone", "lca"])
        if not self.lca_config_window:
            self.lca_config_window = AircraftLifeCycleEval(self.home_dir, os.getcwd())
        self.lca_config_window.show()
        os.chdir(self.home_dir)

    def launch_acsizing(self):
        self.navigate2path(["results", "standalone", "acsizing"])
        if not self.acsizing_config_window:
            self.acsizing_config_window = AircraftSizingDialog(self.home_dir, os.getcwd())
        self.acsizing_config_window.show()
        os.chdir(self.home_dir)

    def launch_flight_envelope_configurator(self):
        self.navigate2path(["results", "standalone", "flight_envelope"])
        if not self.flight_envelope_window:
            self.flight_envelope_window = FlightEnvelopeCalculator(self.home_dir, os.getcwd())
        self.flight_envelope_window.show()
        os.chdir(self.home_dir)

    def launch_export_cad_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Open VSP File", "", "VSP Files (*.vsp3);;All Files (*)", options=options)
        if file_name:
            export2CAD(os.path.relpath(file_name, self.home_dir))
            self.file_exported = True         # Set the flag to True
            message = f"Conversion to STEP file completed. File exported to:\n{self.home_dir}"
            QMessageBox.information(self, "Export Completed", message, QMessageBox.Ok)

    def launch_GT_modeler(self):
        self.navigate2path(["results", "standalone", "gt"])
        if not self.gasturbine_config_window:
            self.gasturbine_config_window = GasTurbineConfigurator(self.home_dir, os.getcwd())
        self.gasturbine_config_window.show()
        os.chdir(self.home_dir)

    def launch_EPS_modeler(self):
        self.navigate2path(["results", "standalone", "eps"])
        if not self.eps_config_window:
            self.eps_config_window = EPSConfigurator(self.home_dir, os.getcwd())
        self.eps_config_window.show()
        os.chdir(self.home_dir)

    def navigate2path(self, folders):

        os.chdir(self.home_dir)

        for folder in folders:
            if not os.path.exists(os.path.join(os.getcwd(), folder)):
                os.mkdir(os.path.join(os.getcwd(), folder))
            os.chdir(os.path.join(os.getcwd(), folder))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    monitor = QDesktopWidget().screenGeometry(0)
    main_window = AircraftDesignMainWindow()
    shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_N), main_window)
    shortcut.activated.connect(main_window.new_file_dialog)
    shortcut1 = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_O), main_window)
    shortcut1.activated.connect(main_window.open_file_dialog)
    shortcut2 = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_S), main_window)
    shortcut2.activated.connect(main_window.save_file_dialog)
    shortcut3 = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_E), main_window)
    shortcut3.activated.connect(main_window.export_file_dialog)
    shortcut4 = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Q), main_window)
    shortcut4.activated.connect(main_window.close)
    main_window.move(monitor.left(), monitor.top())
    main_window.show()
    sys.exit(app.exec_())
