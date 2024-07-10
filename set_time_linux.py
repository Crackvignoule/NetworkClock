import subprocess
import sys

def set_system_time_linux(time_str):
    try:
        subprocess.run(["sudo", "timedatectl", "set-time", time_str], check=True)
        print(f"System time set to {time_str}")
    except subprocess.CalledProcessError:
        print("Failed to set system time")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: set_time_linux.py <time_str>")
    else:
        set_system_time_linux(sys.argv[1])
