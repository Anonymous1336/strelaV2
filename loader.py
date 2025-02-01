import io
import zipfile
import sys
import requests
import os
import stat
import winreg
import win32com.client

shell = win32com.client.Dispatch("WScript.Shell")
python_exe = sys.executable.replace("\\", "/")

script_path = os.path.abspath(__file__)
script_directory = os.path.dirname(script_path)

folder_path = "C:/Program Files/StrelaV2"
if not os.path.isdir(folder_path):
    os.mkdir(folder_path)
    os.chmod(folder_path, stat.S_IRWXU)

version = "beta"

url = "https://api.github.com/repos/Anonymous1336/strelaV2/releases/latest"


def clear_directory(path):
    if os.path.exists(path):
        print(f"Clearing directory: {path}")
        for root, dirs, files in os.walk(path, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                print(f"Removing file: {file_path}")
                os.remove(file_path)
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                print(f"Removing directory: {dir_path}")
                os.rmdir(dir_path)
        print(f"All contents removed from: {path}")
    else:
        print(f"Directory does not exist: {path}")


def add_to_autostart(path):
    name = "loader.py"
    full_path = path + "/" + name
    command = f'"{python_exe}" "{full_path}"'
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)

        winreg.SetValueEx(key, "StrelaV2Loader", 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)

        print("Added to registry")
    except PermissionError:
        print("No access")
    except Exception as e:
        print(f"Error - {e}")


def check_version():
    response = requests.get("https://api.github.com/repos/Anonymous1336/strelaV2/tags")
    if response.status_code == 200:
        print(f"{response.status_code=}")

        releases = response.json()
        first_release = releases[0]
        if first_release["name"] != version:
            print("New version found")
            print("Removing old folder")
            clear_directory(folder_path)
            print(f"Downloading new release...")
            zip_response = requests.get(first_release["zipball_url"])
            print("Extracting...")
            with zipfile.ZipFile(io.BytesIO(zip_response.content)) as z:
                z.extractall("C:/Program Files/StrelaV2")
            print("Done")
            files_folder = folder_path + "/" + os.listdir(folder_path)[0]
            print(files_folder)
            add_to_autostart(files_folder)

        directory = script_directory + "/app/seeker.py"
        directory = directory.replace("\\", "/")
        command = f"{python_exe} {directory}"
        print(command)
        shell.Run(command, 0)

    else:
        print(f"Failed to fetch releases. Status code: {response.status_code}")
        print(f"")


check_version()
