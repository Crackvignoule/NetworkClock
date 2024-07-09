from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
import datetime

class TimeDisplayApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Display Time App")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # UI Components
        self.prompt_label = QLabel("Enter the date/time format string:")
        self.format_input = QLineEdit()
        self.display_button = QPushButton("Display Time")
        self.result_label = QLabel("Current time will be shown here.")

        # Add components to layout
        layout.addWidget(self.prompt_label)
        layout.addWidget(self.format_input)
        layout.addWidget(self.display_button)
        layout.addWidget(self.result_label)

        # Connect button click to action
        self.display_button.clicked.connect(self.display_time)

    def display_time(self):
        format_string = self.format_input.text()
        formatted_time = self.get_formatted_time(format_string)
        if formatted_time:
            self.result_label.setText(f"Current time: {formatted_time}")
        else:
            self.result_label.setText("Invalid format string")

    @staticmethod
    def get_formatted_time(format_string):
        try:
            current_time = datetime.datetime.now()
            return current_time.strftime(format_string)
        except ValueError:
            return None

if __name__ == "__main__":
    app = QApplication([])
    window = TimeDisplayApp()
    window.show()
    app.exec()