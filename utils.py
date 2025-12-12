import sys
import os

def resource_path(relative_path):
    """ 
    Get absolute path to resource (images/assets).
    Read-only. Used for bundled assets in PyInstaller _MEIPASS.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_config_path(filename):
    """
    Get path for persistent configuration files (JSONs).
    Used for reading/writing user settings.
    - Frozen (EXE): Returns path relative to the .exe file.
    - Dev: Returns path relative to current working dir.
    """
    if getattr(sys, 'frozen', False):
        # Se for executável, salva na mesma pasta do .exe
        base_path = os.path.dirname(sys.executable)
    else:
        # Se for script, salva na pasta atual
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, filename)
