import os
import subprocess
import signal
import platform


class OSControl:
    """
    OS Control Abstraction Layer.
    Each method maps to one explicit OS capability.
    """

    def __init__(self):
        self.os_name = platform.system().lower()

    # ================= PROCESS CONTROL =================

    def list_processes(self):
        return subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )

    def kill_process(self, pid):
        os.kill(pid, signal.SIGKILL)
        return f"Process {pid} killed"

    def find_process(self, name):
        return subprocess.run(
            ["pgrep", "-f", name],
            capture_output=True,
            text=True
        )

    # ================= FILE SYSTEM =================

    def read_file(self, path):
        with open(path, "r") as f:
            return f.read()

    def write_file(self, path, content):
        with open(path, "w") as f:
            f.write(content)
        return f"Written to {path}"

    def delete_file(self, path):
        os.remove(path)
        return f"Deleted {path}"

    def list_directory(self, path="."):
        return os.listdir(path)

    # ================= SYSTEM INFO =================

    def current_directory(self):
        return os.getcwd()

    def change_directory(self, path):
        os.chdir(path)
        return os.getcwd()

    def system_info(self):
        return {
            "os": platform.system(),
            "version": platform.version(),
            "architecture": platform.machine()
        }

    # ================= NETWORK =================

    def list_network_interfaces(self):
        return subprocess.run(
            ["ip", "addr"],
            capture_output=True,
            text=True
        )

    def ping(self, host):
        return subprocess.run(
            ["ping", "-c", "4", host],
            capture_output=True,
            text=True
        )


    # ================= SOFTWARE =================

    def run_program(self, program):
        return subprocess.run(
            [program],
            capture_output=True,
            text=True
        )

    def check_command_exists(self, command):
        return subprocess.run(
            ["which", command],
            capture_output=True,
            text=True
        )
