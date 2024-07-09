import configparser
import socket
import threading
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit
from PySide6.QtCore import QTimer
import datetime

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
        self.prompt_label = QLabel("Enter the date/time format string (e.g., '%Y-%m-%d %H:%M:%S'):")
        self.format_input = QLineEdit()
        self.format_input.setPlaceholderText("%Y-%m-%d %H:%M:%S")  # Default format as placeholder
        self.examples_label = QLabel("Examples: '%Y-%m-%d', '%H:%M:%S', '%m/%d/%Y %I:%M %p'")
        self.result_label = QLabel("Current time will be shown here.")

        # Add components to layout
        layout.addWidget(self.prompt_label)
        layout.addWidget(self.format_input)
        layout.addWidget(self.examples_label)  # Add examples label
        layout.addWidget(self.result_label)

        # Timer setup
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # Update every second
        self.timer.timeout.connect(self.update_time_display)

        # Update time display whenever the format input changes
        self.format_input.textChanged.connect(self.update_time_display)

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
            test_time = current_time.strftime(format_string)  # Test formatting with the current time
            return test_time
        except ValueError:
            return None
    
    def start_tcp_server(self, port):
        def handle_client_connection(client_socket):
            while True:
                try:
                    format_string = client_socket.recv(1024).decode('utf-8')
                    if not format_string:
                        break
                    formatted_time = self.get_formatted_time(format_string)
                    response = formatted_time if formatted_time else "Invalid format string"
                    client_socket.send(response.encode('utf-8'))
                except Exception as e:
                    print(f"Error handling client: {e}")
                    break
            client_socket.close()

        def server_thread():
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                    server_socket.bind(('', port))
                    server_socket.listen()
                    while True:
                        client_socket, _ = server_socket.accept()
                        threading.Thread(target=handle_client_connection, args=(client_socket,)).start()

        threading.Thread(target=server_thread, daemon=True).start()

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.toml')
    port = int(config['DEFAULT']['Port'])

    app = QApplication([])
    window = TimeDisplayApp(port)
    window.show()
    app.exec()