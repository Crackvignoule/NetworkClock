import subprocess
import sys

def set_system_time_linux(time_str):
    try:
        # Disable NTP synchronization
        subprocess.run(["sudo", "timedatectl", "set-ntp", "false"], check=True)
        
        # Set the system time
        subprocess.run(["sudo", "timedatectl", "set-time", time_str], check=True)
        print(f"System time set to {time_str}")
        
        # to re-enable NTP synchronization
        # subprocess.run(["sudo", "timedatectl", "set-ntp", "true"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to set system time: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: set_time_linux.py <time_str>")
    else:
        set_system_time_linux(sys.argv[1])