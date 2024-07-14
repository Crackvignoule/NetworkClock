
![NetworkClock](https://i.imgur.com/860WSwn.png)

# NetworkClock

NetworkClock is a Python application designed to display the current time in a custom user defined format. It also allow users to set the system time through a graphical user interface (GUI). Additionally, a remote user can get the time with a custom format via TCP/IP. It supports both Linux and Windows platforms.

## Features

- Display the current time in a custom format.
- Set the system time from the GUI.
- User-friendly GUI
- Cross-platform support for Linux and Windows.

## Requirements

- Python 3.x
- PySide6

## Getting Started

To install and run NetworkClock, clone the repository and install dependencies with the following commands:

```sh
git clone https://github.com/Crackvignoule/NetworkClock
cd NetworkClock
pip install -r requirements.txt
python main.py
```

## Getting Time via TCP

NetworkClock allows users to retrieve the current time in a custom format over TCP/IP. To use this feature, ensure the NetworkClock app is running, then connect to it using the configured port (default is 12345).

### Example using netcat:

```sh
echo "%Y-%m-%d %H:%M:%S" | nc <server-ip> 12345
```

You can refer to the [strftime.org](https://strftime.org/) website. It provides a comprehensive list of formatting options that you can use to customize the time output according to your needs.