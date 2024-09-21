from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton


class PromptWindow(QDialog):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Edit Battery Values")
        self.data = data
        self.input_fields = {}

        layout = QVBoxLayout()

        for key, value in data.items():
            label = QLabel(f"{key}: ")
            line_edit = QLineEdit(value)
            layout.addWidget(label)
            layout.addWidget(line_edit)
            self.input_fields[key] = line_edit

        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        ok_button = QPushButton("OK")
        cancel_button.clicked.connect(self.close)
        ok_button.clicked.connect(self.on_ok_clicked)
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def on_ok_clicked(self):
        for key, line_edit in self.input_fields.items():
            self.data[key] = line_edit.text()
        self.accept()