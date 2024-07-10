import subprocess
import sys

def set_system_time_windows(time_str):
    try:
        subprocess.run(["powershell", f"Set-Date -Date \"{time_str}\""], check=True)
        print(f"System time set to {time_str}")
    except subprocess.CalledProcessError:
        print("Failed to set system time")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: set_time_windows.py <time_str>")
    else:
        set_system_time_windows(sys.argv[1])
