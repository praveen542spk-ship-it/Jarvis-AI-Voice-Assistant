import os
import sys

def setup_startup():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    ui_script = os.path.join(project_dir, "jarvis_ui.py")
    
    # Use the absolute path to the active python.exe (keeps console descriptors active so PyAudio doesn't crash)
    python_exe = sys.executable
    
    # 1. Path to Windows Startup folder
    startup_dir = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
    vbs_path = os.path.join(startup_dir, "jarvis_startup.vbs")
    shortcut_path = os.path.join(startup_dir, "Jarvis.lnk")
    bat_path = os.path.join(startup_dir, "JarvisAutoStart.bat")
    
    try:
        # 1. Clean up old conflicting files
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            print("Deleted old Shortcut .lnk file.")
        if os.path.exists(bat_path):
            os.remove(bat_path)
            print("Deleted old BAT file.")
            
        # 2. Re-create VBScript with python.exe path using the 0 parameter in WshShell.Run
        # This keeps PyAudio perfectly happy by maintaining a console context, but hides the window completely (0) from the user
        vbs_code = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """{python_exe}"" ""{ui_script}""", 0, False
'''
        
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_code)
            
        print(f"Startup VBScript successfully installed at: {vbs_path}")
        return True
        
    except Exception as e:
        print(f"Error configuring startup: {e}")
        return False

if __name__ == "__main__":
    setup_startup()
