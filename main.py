import sys
import configparser
import socket
import threading
import datetime
import subprocess
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

def load_port():
    config = configparser.ConfigParser()
    config.read("config.toml")
    try:
        port = int(config["SERVER"]["port"])
        if 1024 <= port <= 65535:
            return port
        else:
            raise ValueError("Port number must be between 1024 and 65535")
    except Exception as e:
        print(f"Invalid port number: {port}. {e}")
        print("Using default port 12345")
        return 12345

class TimeDisplayApp(QWidget):
    def __init__(self, port):
        super().__init__()
        self.setWindowTitle("NetworkClock")
        self.setup_ui()
        self.timer.start()
        self.start_tcp_server(port)

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
        if "linux" in sys.platform:
            subprocess.run(["python3", "utils/set_time_linux.py", time_str], check=True)
        elif "win" in sys.platform:
            subprocess.run(["powershell", "Start-Process", "python", "-ArgumentList", f"'utils/set_time_windows.py \"{time_str}\"'"], check=True)


    def update_time_display(self):
        format_string = self.format_input.text() or "%Y-%m-%d %H:%M:%S"
        formatted_time = self.get_formatted_time(format_string)
        if formatted_time:
            self.result_label.setText(f"Current time: {formatted_time}")
        else:
            self.result_label.setText("Invalid format string")

    @staticmethod
    def get_formatted_time(format_string):
        try:
            current_time = datetime.datetime.now()
            test_time = current_time.strftime(
                format_string
            )  # Test formatting with the current time
            return test_time
        except ValueError:
            return None

    def start_tcp_server(self, port):
        def process_message(buffer):
            print(rf"Buffer: {buffer}")
            if buffer.endswith("\n"):
                buffer = buffer[:-1]
                formatted_time = self.get_formatted_time(buffer)
                if formatted_time:
                    return formatted_time
                else:
                    return "Invalid format string"
            else:
                return ""
            
        def handle_client(client_socket):
            buffer = ""
            while True:
                try:
                    data = client_socket.recv(1024).decode("utf-8")
                    if not data:
                        break

                    buffer += data
                    response = process_message(buffer)

                    # Clear buffer up to the last newline character
                    while "\n" in buffer:
                        newline_pos = buffer.index("\n")
                        buffer = buffer[newline_pos + 1:]

                    client_socket.send(response.encode("utf-8"))
                except Exception as e:
                    print(f"Error handling client: {e}")
                    break
            client_socket.close()

        def server_thread():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind(('', port))
                server_socket.listen()
                print(f"Server listening on localhost:{port}")
                
                while True:
                    client, addr = server_socket.accept()
                    print(f"Accepted connection from {addr}")
                    client_handler = threading.Thread(target=handle_client, args=(client,))
                    client_handler.start()

        threading.Thread(target=server_thread, daemon=True).start()


if __name__ == "__main__":
    port = load_port()

    app = QApplication([])
    window = TimeDisplayApp(port)
    window.show()
    app.exec()
