<div align="center">
    <img src="https://i.imgur.com/860WSwn.png" alt="NetworkClock">
</div>

# NetworkClock

NetworkClock is a Python application designed to display the current time in a custom user defined format. It also allow users to set the system time through a graphical user interface (GUI). Additionally, a remote user can get the time with a custom format via TCP/IP. Developed by Killian PAVY

## Features

- Display the current time in a custom format.
- Set the system time from the GUI.
- User-friendly GUI

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

NetworkClock allows users to retrieve the current time in a custom format over TCP/IP. To use this feature, ensure the NetworkClock app is running, then connect to it using the right port (default is 12345). You can edit the listening port in %USERPROFILE%/AppData/Local/Clock/config.toml
Type your format string and press enter. The app will respond with the current time in the format you specified.

### Example using netcat:

```sh
echo "%Y-%m-%d %H:%M:%S" | nc <server-ip> 12345
```

You can refer to [strftime.org](https://strftime.org/) or [https://strftime.org](https://www.strfti.me/). It provides a comprehensive list of formatting options that you can use to customize the time output according to your needs.

## Additional Information

NetworkClock is using windll.kernel32.SetProcessDEPPolicy(1) to enable Data Execution Prevention (DEP) for the process. This is a security feature that helps prevent code execution from data pages.

In utils/set_time_windows.py, only the necessary commands are executed with elevated privileges, ensuring that the rest of the script runs with normal user privileges to minimize security risks.

Port number is stored in %USERPROFILE%/AppData/Local/Clock/config.toml which is a secure location on Windows systems because it is only accessible by the user who installed the application.