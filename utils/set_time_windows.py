from __future__ import print_function
import ctypes
from ctypes import wintypes
import sys
import datetime

# Enable Data Execution Prevention (DEP) for the process
ctypes.windll.kernel32.SetProcessDEPPolicy(1)

def set_system_time_windows(time_str):
    # Convert string time to SYSTEMTIME structure
    try:
        # for privilege in get_privilege_information():
            # print(privilege)

        # Drop all unecessary privileges
        set_privilege("SeSystemtimePrivilege", True, drop_others=True)

        # print("\n After dropping:\n")
        # for privilege in get_privilege_information():
            # print(privilege)

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
        set_time(ctypes.byref(system_time))

    except Exception:
        return
    

GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess
GetCurrentProcess.restype = wintypes.HANDLE
OpenProcessToken = ctypes.windll.advapi32.OpenProcessToken
OpenProcessToken.argtypes = (wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE))
OpenProcessToken.restype = wintypes.BOOL

class LUID(ctypes.Structure):
    _fields_ = [
        ('low_part', wintypes.DWORD),
        ('high_part', wintypes.LONG),
        ]

    def __eq__(self, other):
        return (
            self.high_part == other.high_part and
            self.low_part == other.low_part
            )

    def __ne__(self, other):
        return not (self==other)

LookupPrivilegeValue = ctypes.windll.advapi32.LookupPrivilegeValueW
LookupPrivilegeValue.argtypes = (
    wintypes.LPWSTR, # system name
    wintypes.LPWSTR, # name
    ctypes.POINTER(LUID),
    )
LookupPrivilegeValue.restype = wintypes.BOOL

class TOKEN_INFORMATION_CLASS:
    TokenUser = 1
    TokenGroups = 2
    TokenPrivileges = 3
    # ... see http://msdn.microsoft.com/en-us/library/aa379626%28VS.85%29.aspx

SE_PRIVILEGE_ENABLED_BY_DEFAULT = (0x00000001)
SE_PRIVILEGE_ENABLED            = (0x00000002)
SE_PRIVILEGE_REMOVED            = (0x00000004)
SE_PRIVILEGE_USED_FOR_ACCESS    = (0x80000000)

class LUID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ('LUID', LUID),
        ('attributes', wintypes.DWORD),
        ]

    def is_enabled(self):
        return bool(self.attributes & SE_PRIVILEGE_ENABLED)

    def enable(self):
        self.attributes |= SE_PRIVILEGE_ENABLED

    def get_name(self):
        size = wintypes.DWORD(10240)
        buf = ctypes.create_unicode_buffer(size.value)
        res = LookupPrivilegeName(None, self.LUID, buf, size)
        if res == 0: raise RuntimeError
        return buf[:size.value]

    def __str__(self):
        res = self.get_name()
        if self.is_enabled(): res += ' (enabled)'
        return res

LookupPrivilegeName = ctypes.windll.advapi32.LookupPrivilegeNameW
LookupPrivilegeName.argtypes = (
    wintypes.LPWSTR, # lpSystemName
    ctypes.POINTER(LUID), # lpLuid
    wintypes.LPWSTR, # lpName
    ctypes.POINTER(wintypes.DWORD), #cchName
    )
LookupPrivilegeName.restype = wintypes.BOOL

class TOKEN_PRIVILEGES(ctypes.Structure):
    _fields_ = [
        ('count', wintypes.DWORD),
        ('privileges', LUID_AND_ATTRIBUTES*0),
        ]

    def get_array(self):
        array_type = LUID_AND_ATTRIBUTES*self.count
        privileges = ctypes.cast(self.privileges, ctypes.POINTER(array_type)).contents
        return privileges

    def __iter__(self):
        return iter(self.get_array())

PTOKEN_PRIVILEGES = ctypes.POINTER(TOKEN_PRIVILEGES)

GetTokenInformation = ctypes.windll.advapi32.GetTokenInformation
GetTokenInformation.argtypes = [
    wintypes.HANDLE, # TokenHandle
    ctypes.c_uint, # TOKEN_INFORMATION_CLASS value
    ctypes.c_void_p, # TokenInformation
    wintypes.DWORD, # TokenInformationLength
    ctypes.POINTER(wintypes.DWORD), # ReturnLength
    ]
GetTokenInformation.restype = wintypes.BOOL

# http://msdn.microsoft.com/en-us/library/aa375202%28VS.85%29.aspx
AdjustTokenPrivileges = ctypes.windll.advapi32.AdjustTokenPrivileges
AdjustTokenPrivileges.restype = wintypes.BOOL
AdjustTokenPrivileges.argtypes = [
    wintypes.HANDLE,                 # TokenHandle
    wintypes.BOOL,                   # DisableAllPrivileges
    PTOKEN_PRIVILEGES,               # NewState (optional)
    wintypes.DWORD,                  # BufferLength of PreviousState
    PTOKEN_PRIVILEGES,               # PreviousState (out, optional)
    ctypes.POINTER(wintypes.DWORD),  # ReturnLength
]


def get_process_token():
    """
    Get the current process token
    """
    token = wintypes.HANDLE()
    TOKEN_ALL_ACCESS = 0xf01ff
    res = OpenProcessToken(GetCurrentProcess(), TOKEN_ALL_ACCESS, token)
    if not res > 0:
        raise RuntimeError("Couldn't get process token")
    return token


def get_luid(name):
    """
    Get the LUID for the SeCreateSymbolicLinkPrivilege
    """
    luid = LUID()
    res = LookupPrivilegeValue(None, name, luid)
    if not res > 0:
        raise RuntimeError("Couldn't lookup privilege value")
    return luid


def set_privilege(name, enable=True, drop_others=False):
    """
    Try to assign the privilege to the current process token.
    Optionally, disable all privileges except the specified one if enable_only is True.
    Return True if the assignment is successful.
    """
    # create a space in memory for a TOKEN_PRIVILEGES structure
    #  with one element
    size = ctypes.sizeof(TOKEN_PRIVILEGES)
    if drop_others:
        # If enabling only a specific privilege, first disable all
        token = get_process_token()
        # Set the privileges to all disabled
        res = AdjustTokenPrivileges(token, True, None, 0, None, None)
        if res == 0:
            raise RuntimeError("Error in AdjustTokenPrivileges when disabling all")
    else:
        size += ctypes.sizeof(LUID_AND_ATTRIBUTES)
    buffer = ctypes.create_string_buffer(size)
    tp = ctypes.cast(buffer, ctypes.POINTER(TOKEN_PRIVILEGES)).contents
    tp.count = 1
    tp.get_array()[0].LUID = get_luid(name)
    tp.get_array()[0].Attributes = SE_PRIVILEGE_ENABLED if enable else 0
    token = get_process_token()
    res = AdjustTokenPrivileges(token, False, tp, 0, None, None)
    if res == 0:
        raise RuntimeError("Error in AdjustTokenPrivileges")

    ERROR_NOT_ALL_ASSIGNED = 1300
    return ctypes.windll.kernel32.GetLastError() != ERROR_NOT_ALL_ASSIGNED


def get_privilege_information():
    """
    Get all privileges associated with the current process.
    """
    # first call with zero length to determine what size buffer we need

    return_length = wintypes.DWORD()
    params = [
        get_process_token(),
        TOKEN_INFORMATION_CLASS.TokenPrivileges,
        None,
        0,
        return_length,
    ]

    res = GetTokenInformation(*params)

    # assume we now have the necessary length in return_length

    buffer = ctypes.create_string_buffer(return_length.value)
    params[2] = buffer
    params[3] = return_length.value

    res = GetTokenInformation(*params)
    assert res > 0, "Error in second GetTokenInformation (%d)" % res

    privileges = ctypes.cast(buffer, ctypes.POINTER(TOKEN_PRIVILEGES)).contents
    return privileges

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: set_time_windows.py <time_str>")
    else:
        set_system_time_windows(sys.argv[1])
