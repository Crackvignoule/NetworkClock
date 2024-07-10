import subprocess
import sys

# TODO
# ADMIN TERMINAL WORKS:
# python .\set_time_windows.py '2024-07-04 10:15:22'

# NORMAL TERMINAL DONT:
# Start-Process -FilePath "python" -ArgumentList "set_time_windows.py", '2024-06-26 10:37:33' -Verb RunAs

def set_system_time_windows(time_str):
    try:
        subprocess.run(["powershell", f"Set-Date -Date '{time_str}'"], check=True)
        print(f"System time set to {time_str}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to set system time: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: set_time_windows.py <time_str>")
    else:
        set_system_time_windows(sys.argv[1])
