import ctypes
from ctypes import wintypes
import sys
import datetime

# Enable Data Execution Prevention (DEP) for the process
ctypes.windll.kernel32.SetProcessDEPPolicy(1)

def set_system_time_windows(time_str):
    # Convert string time to SYSTEMTIME structure
    try:
        # Parse the time string to datetime object
        dt = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        # Convert to UTC
        local_tz = datetime.datetime.now().astimezone().tzinfo
        dt = dt.replace(tzinfo=local_tz)
        dt = dt.astimezone(datetime.timezone.utc)

        # Define SYSTEMTIME Structure
        class SYSTEMTIME(ctypes.Structure):
            _fields_ = [
                ("wYear", wintypes.WORD),
                ("wMonth", wintypes.WORD),
                ("wDayOfWeek", wintypes.WORD),
                ("wDay", wintypes.WORD),
                ("wHour", wintypes.WORD),
                ("wMinute", wintypes.WORD),
                ("wSecond", wintypes.WORD),
                ("wMilliseconds", wintypes.WORD),
            ]

        # Create SYSTEMTIME object
        system_time = SYSTEMTIME(
            wYear=dt.year,
            wMonth=dt.month,
            wDay=dt.day,
            wHour=dt.hour,
            wMinute=dt.minute,
            wSecond=dt.second,
            wMilliseconds=0,
        )

        # Set system time
        set_time = ctypes.windll.kernel32.SetSystemTime
        set_time.argtypes = [ctypes.POINTER(SYSTEMTIME)]

    except Exception:
        return



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: set_time_windows.py <time_str>")
    else:
        set_system_time_windows(sys.argv[1])
