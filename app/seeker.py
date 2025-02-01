import asyncio
import socket
import time
import psutil
import hashlib
import os

hash_library = [
    "a14c14397ec48c23c64d298cb78f61c3",  # RobloxPlayerBeta.exe, 02-01-2025
    "87d16125a92ef654c99aa882df194f25",  # isaac-ng.exe, 02-01-2025
    ""
]

banned_processes = ["RobloxPlayerBeta.exe",
                    "hl.exe",
                    "hl2.exe",
                    "isaac-ng.exe",
                    "aces.exe",
                    ""
                    ]

possible_path_parts = [
    "roblox",
    "counter-strike",
    "counter strike",
    "isaac",
]

debug_mode = False
at_home = True

pc_name = socket.gethostname()
start_time = time.time()

print(pc_name)

if not at_home:
    #  даем время пк запуститься
    time.sleep(120)


def check_by_hash(file_hash):
    if file_hash in hash_library:
        return True
    return False


def check_by_name(proc):
    if proc.info['name'] in banned_processes:
        return True
    return False


def check_by_path(exe_path):
    for item in possible_path_parts:
        if exe_path.count(item):
            return True
    return False


def send_notif(proc, exe_path, file_hash, method):
    # в будущем для телеграмуса
    print(f"Имя: {pc_name}")
    print(f"PID: {proc.pid}")
    print(f"Имя: {proc.info['name']}")
    print(f"Путь: {exe_path}")
    print(f"MD5-hash: {file_hash}")
    print(f"Метод: {method}")


def get_hash(file_path):
    if not os.path.isfile(file_path):
        return None
    try:
        with open(file_path, "rb") as f:
            file_content = f.read()
            md5_hash = hashlib.md5(file_content).hexdigest()
        return md5_hash
    except Exception as e:
        print(f"{file_path} - {e}")
        return None


def is_system_process(process):
    try:
        if process.username().lower() in ["system", "local service", "network service"]:
            return True
        exe_path = process.exe()
        if exe_path.lower().startswith("c:\\windows\\"):
            return True
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        return True
    return False


class Checker:
    def __init__(self):
        self.known_pids = set()

    def check(self):
        seen = set()
        for proc in psutil.process_iter(['pid', 'name', 'exe']):

            if proc.pid in self.known_pids:
                continue
            try:
                exe_path = proc.info['exe']
                if not exe_path:
                    continue
                exe_path = exe_path.lower()
                if is_system_process(proc):
                    continue

                terminated = False
                file_hash = get_hash(exe_path)

                if check_by_hash(file_hash) and not terminated:
                    proc.terminate()
                    send_notif(proc, exe_path, file_hash, "ByHash")
                    terminated = True

                if check_by_name(proc) and not terminated:
                    proc.terminate()
                    send_notif(proc, exe_path, file_hash, "ByName")
                    terminated = True

                if check_by_path(exe_path) and not terminated:
                    proc.terminate()
                    send_notif(proc, exe_path, file_hash, "ByPath")

                if debug_mode:
                    print(f"PID: {proc.pid}")
                    print(f"Имя: {proc.info['name']}")
                    print(f"Путь: {exe_path}")
                    print(f"MD5-hash: {file_hash}")
                    print("-" * 50)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

            finally:
                seen.add(proc.pid)

        self.known_pids = seen

    async def inf_loop(self):
        while True:
            self.check()
            await asyncio.sleep(5)


checker = Checker()
asyncio.run(checker.inf_loop())

