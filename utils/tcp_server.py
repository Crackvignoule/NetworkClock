import socket
import threading
from utils import get_formatted_time

class TCPServer:
    def __init__(self, port):
        self.port = port

    def process_message(self, buffer):
        if buffer.endswith("\n"):
            buffer = buffer[:-1]
            formatted_time = get_formatted_time(buffer)
            if formatted_time:
                return formatted_time
            else:
                return "Invalid format string"
        else:
            return ""

    def handle_client(self, client_socket):
        buffer = ""
        while True:
            try:
                data = client_socket.recv(1024).decode("utf-8")
                if not data:
                    break

                buffer += data

                # Process each message that ends with a newline character
                while "\n" in buffer:
                    newline_pos = buffer.index("\n")
                    complete_message = buffer[:newline_pos]
                    buffer = buffer[newline_pos + 1:]  # Retain incomplete message

                    response = self.process_message(complete_message + "\n")  # Add back the newline for processing
                    client_socket.send(response.encode("utf-8"))
            except Exception as e:
                print(f"Error handling client: {e}")
                break
        client_socket.close()

    def server_thread(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(('', self.port))
            server_socket.listen()
            print(f"Server listening on localhost:{self.port}")
            
            while True:
                client, addr = server_socket.accept()
                print(f"Accepted connection from {addr}")
                client_handler = threading.Thread(target=self.handle_client, args=(client,))
                client_handler.start()

    def start(self):
        threading.Thread(target=self.server_thread, daemon=True).start()

if __name__ == "__main__":
    server = TCPServer(port=12345)
    server.start()
    input("Press Enter to exit...\n")