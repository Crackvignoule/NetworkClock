import toml
import datetime
import ctypes
from pathlib import Path
from ctypes import wintypes

def get_formatted_time(format_string):
        try:
            current_time = datetime.datetime.now()
            test_time = current_time.strftime(
                format_string
            )
            return test_time
        except ValueError:
            return None
        
def get_known_folder(guid):
    # Define FOLDERID_LocalAppData
    class GUID(ctypes.Structure):
        _fields_ = [
            ("Data1", wintypes.DWORD),
            ("Data2", wintypes.WORD),
            ("Data3", wintypes.WORD),
            ("Data4", wintypes.BYTE * 8),
        ]

    # Define SHGetKnownFolderPath function
    SHGetKnownFolderPath = ctypes.windll.shell32.SHGetKnownFolderPath
    SHGetKnownFolderPath.argtypes = [
        ctypes.POINTER(GUID),
        wintypes.DWORD,
        wintypes.HANDLE,
        ctypes.POINTER(ctypes.c_wchar_p),
    ]
    SHGetKnownFolderPath.restype = wintypes.DWORD

    # Define FOLDERID_LocalAppData GUID
    FOLDERID_LocalAppData = GUID(
        0xF1B32785,
        0x6FBA,
        0x4FCF,
        (wintypes.BYTE * 8)(0x9D, 0x55, 0x7B, 0x8E, 0x7F, 0x15, 0x70, 0x91),
    )

    path_buf = ctypes.c_wchar_p()
    # Retrieve the path to the LocalAppData folder
    if SHGetKnownFolderPath(ctypes.byref(FOLDERID_LocalAppData), 0, None, ctypes.byref(path_buf)) == 0:
        return path_buf.value
    return None

def get_port():
    local_appdata_path = Path(get_known_folder("{F1B32785-6FBA-4FCF-9D55-7B8E7F157091}"))
    clock_dir = local_appdata_path / "Clock"
    clock_dir.mkdir(parents=True, exist_ok=True)
    config_path = clock_dir / "config.toml"
    if not config_path.exists():
        with config_path.open("w") as config_file:
            default_config = {"SERVER": {"port": 12345}}
            toml.dump(default_config, config_file)
        print(f"Default config file created at {config_path}.")
    try:
        config = toml.load(config_path)
        port = int(config["SERVER"]["port"])
        if not 1024 <= port <= 65535:
            raise ValueError("Port number must be between 1024 and 65535.")
        return port
    except FileNotFoundError:
        print(f"Config file not found at {config_path}.")
    except Exception as e:
        print(f"Error loading port from config: {e}")
    return 12345