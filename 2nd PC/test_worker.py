import os
import signal
import threading
import subprocess
from PyQt5.QtCore import QObject, pyqtSignal

class TestWorker(QObject):
    outSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.stop_event = threading.Event()

    def run_command(self, cmd):
        self.stop_event.clear()
        threading.Thread(target=self._execute_command, args=(cmd), daemon=True).start()

    def cancel_command(self):
        self.stop_event.set()

    def _execute_command(self, cmd):
        if self.stop_event.isSet():
            return
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            universal_newlines=True,
        )
        if self.stop_event.isSet():
            proc.kill()
            return
        for line in proc.stdout:
            if self.stop_event.isSet():
                proc.kill()
                return
            self.outSignal.emit(line)