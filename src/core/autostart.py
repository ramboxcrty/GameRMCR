"""Windows auto-start functionality."""
import winreg
import sys
from pathlib import Path


class AutoStart:
    """Manage Windows startup registration."""
    
    APP_NAME = "GamePPClone"
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    @classmethod
    def enable(cls) -> bool:
        """Enable auto-start on Windows startup."""
        try:
            exe_path = sys.executable
            if exe_path.endswith("python.exe"):
                # Running from source, use script path
                script_path = Path(__file__).parent.parent / "main.py"
                command = f'"{exe_path}" "{script_path}"'
            else:
                # Running as compiled exe
                command = f'"{exe_path}"'
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REG_PATH,
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, cls.APP_NAME, 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
            return True
        except Exception:
            return False
    
    @classmethod
    def disable(cls) -> bool:
        """Disable auto-start."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REG_PATH,
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(key, cls.APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return True  # Already disabled
        except Exception:
            return False
    
    @classmethod
    def is_enabled(cls) -> bool:
        """Check if auto-start is enabled."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REG_PATH,
                0,
                winreg.KEY_READ
            )
            winreg.QueryValueEx(key, cls.APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False
