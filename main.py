import ctypes
import sys
from PySide6.QtCore import QTimer, QDateTime
from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDateTimeEdit,
)
from utils import TCPServer, get_formatted_time, get_port

# Enable Data Execution Prevention (DEP) for the process
ctypes.windll.kernel32.SetProcessDEPPolicy(1)

class TimeDisplayApp(QWidget):
    def __init__(self, port):
        super().__init__()
        self.setWindowTitle("NetworkClock")
        self.setup_ui()
        self.timer.start()
        tcp_server = TCPServer(port)
        tcp_server.start()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # UI Components
        self.prompt_label = QLabel(
            "Enter the date/time format string:"
        )
        self.format_input = QLineEdit()
        self.format_input.setPlaceholderText(
            "%Y-%m-%d %H:%M:%S"
        )  # Default format as placeholder
        self.examples_label = QLabel(
            "Examples: '%Y-%m-%d', '%H:%M:%S', '%m/%d/%Y %I:%M %p'"
        )
        self.dateTimeEdit = QDateTimeEdit(QDateTime.currentDateTime())
        self.dateTimeEdit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.dateTimeEdit.setCalendarPopup(True)
        self.setTimeBtn = QPushButton("Set System Time")
        set_time = QHBoxLayout()
        set_time.addWidget(self.dateTimeEdit)
        set_time.addWidget(self.setTimeBtn)

        self.result_label = QLabel("Current time will be shown here.")

        # Add components to layout
        layout.addWidget(self.prompt_label)
        layout.addWidget(self.format_input)
        layout.addWidget(self.examples_label)
        layout.addLayout(set_time)
        layout.addWidget(self.result_label)

        # Connect button to set system time
        self.setTimeBtn.clicked.connect(self.set_system_time)

        # Timer setup
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_time_display)

        # Update time display whenever the format input changes
        self.format_input.textChanged.connect(self.update_time_display)

    def set_system_time(self):
        time_str = self.dateTimeEdit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        print(f"GUI setting system time to: {time_str}")
        if "win" in sys.platform:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f"utils/set_time_windows.py \"{time_str}\"", None, 1)
        else:
            print("Setting system time is not supported on this platform")

    def update_time_display(self):
        format_string = self.format_input.text() or "%Y-%m-%d %H:%M:%S"
        formatted_time = get_formatted_time(format_string)
        if formatted_time:
            self.result_label.setText(f"Current time: {formatted_time}")
        else:
            self.result_label.setText("Invalid format string")


if __name__ == "__main__":
    port = get_port()
    app = QApplication([])
    window = TimeDisplayApp(port)
    window.show()
    app.exec()
