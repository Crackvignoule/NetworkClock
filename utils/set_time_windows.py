import ctypes
from ctypes import wintypes
import sys
import datetime

def set_system_time_windows(time_str):
    # Convert string time to SYSTEMTIME structure
    try:
        # Parse the time string to datetime object
        dt = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        
        # Define SYSTEMTIME Structure
        class SYSTEMTIME(ctypes.Structure):
            _fields_ = [("wYear", wintypes.WORD),
                        ("wMonth", wintypes.WORD),
                        ("wDayOfWeek", wintypes.WORD),
                        ("wDay", wintypes.WORD),
                        ("wHour", wintypes.WORD),
                        ("wMinute", wintypes.WORD),
                        ("wSecond", wintypes.WORD),
                        ("wMilliseconds", wintypes.WORD)]
        
        # Create SYSTEMTIME object
        system_time = SYSTEMTIME(wYear=dt.year, wMonth=dt.month, wDay=dt.day,
                                wHour=dt.hour, wMinute=dt.minute, wSecond=dt.second,
                                wMilliseconds=0)
        
        # Set system time
        set_time = ctypes.windll.kernel32.SetSystemTime
        set_time.argtypes = [ctypes.POINTER(SYSTEMTIME)]
        
        if set_time(ctypes.byref(system_time)):
            print(f"System time set to {time_str}")
        else:
            print("Failed to set system time")
    except Exception as e:
        print(f"Error setting system time: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: set_time_windows.py <time_str>")
    else:
        set_system_time_windows(sys.argv[1])