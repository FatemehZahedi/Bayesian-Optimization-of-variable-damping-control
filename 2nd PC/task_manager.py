import sys
import queue
import zmq
import time
from functools import partial
from subprocess import Popen, PIPE

from PyQt5.QtCore import (QObject, pyqtSignal, pyqtSlot, QThread)
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# https://stackoverflow.com/questions/53461496/trying-to-get-qprocess-to-work-with-a-queue

"""
 History : 0421 version : 1) adding the saving path from the other PC
                          2) Since ssh_client.py is updated
"""

class ZeroMQ_Listener(QtCore.QObject):

    message = QtCore.pyqtSignal(bytes)
    
    def __init__(self, address):
       
        QtCore.QObject.__init__(self)        
        self.init_zmq(address)   
        self.running = False
        self.str_res = None
        self.client_addr = None

        self.message.connect(self.myAction)

    def init_zmq(self, address):
        context = zmq.Context()
        self.socket = context.socket(zmq.DEALER)
        # Set the timeout time for receiving messages to 1 second
        self.socket.setsockopt(zmq.RCVTIMEO, 1000)
        self.socket.connect(address)
        # Send heartbeat to broker to register worker
        self.socket.send_multipart([b"heart", b""])
 
    def set_completed(self):
        if(self.str_res is not None and self.client_addr is not None):
            self.socket.send_multipart([self.client_addr, b"world"])
            self.str_res = None
            self.client_addr = None  

    def restart(self):
        self.running = True          
        self.str_res = None
        self.client_addr = None

    def alive(self):
        return self.running

    def connectSignal(self):        
        self.message.connect(self.myAction)

    @QtCore.pyqtSlot()
    def myAction(self):
        print("signal triggered : %s", self.str_res)

    def loop(self):
        while True:
            QtCore.QThread.msleep(50)
            if(self.running):
                try:
                    # Get client address and message content
                    client_addr, str_res = self.socket.recv_multipart()   
                except Exception as e:
                    # Timeout resend heartbeat
                    print(e)
                    self.socket.send_multipart([b"heart", b""])
                    continue

                if(str_res):
                    self.str_res = str_res
                    self.client_addr = client_addr    
                    self.message.emit(self.str_res) 
                self.running = False

class Processes(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    task_started = QtCore.pyqtSignal(str)

    seq_num = 0
    _queue_id = 0
    last_seq_num = 0
    _queue_id = 0
    _queue = queue.Queue()
    listener = None
    triggered = False

    def __init__(self, commands, listner_adress =""):
        super().__init__()

        self.commands = commands 

        # Create a QThread object
        self.thread = QtCore.QThread()
        self.listener = ZeroMQ_Listener(listner_adress)          
        self.listener.message.connect(self.signal_received)
        # Create a worker object
        self.listener.moveToThread(self.thread)

        # Connect signals and slots
        self.thread.started.connect(self.listener.loop)
        self.thread.finished.connect(self.thread.quit)

        self.seq_num = 0
        self.last_queue_id = 0

        QtCore.QTimer.singleShot(0, self.thread.start)
        
        self.next_task_ready = True
        self.infinteFlag = False
        self.running = True

    def init(self):
        pass
        
    def signal_received(self, message):
        print("message:", message)
        if(message):
            self.triggered = True            
            print("Task thread: started!")

    def appendTask(self, task):
        self._queue.put(task)

    def start(self):
        self.seq_num = 1
        self.listener.running = True
        print("self.start()")

    def stop(self):
        self.listener.running = False       
        print("self.stop()")

    def reboot(self):  
        self._queue = queue.Queue()
        self._queue_id = 0
        self.listener.running = False

        print("self.reboot()")
    
    def set_task_ready(self, ready):
        self.next_task_ready = ready

    def set_infinteFlag(self, flag):
        self.infinteFlag = flag 

    def call_task(self):
        if(not self._queue.empty()):
            cmd = self._queue.get()
            self._queue_id += 1
            print("cmd:", cmd)

            self.next_task_ready = True
            self.task_started.emit(cmd)
            self.next_task_ready = False

    def task_process(self):        
        while True:      
            if(self.running):
                if(self.seq_num is not self.last_seq_num):
                    self.last_seq_num = self.seq_num
                    print("self.seq_num :", self.seq_num )  

                if(self.seq_num == 0):
                    if(not self.listener.alive):
                        self.listener.restart()
                    else:
                        self.triggered = False

                elif(self.seq_num == 1):
                    if(self.triggered):
                        for task in self.commands:
                            self.appendTask(task)
                                            
                        self.seq_num = 2

                elif(self.seq_num == 2):
                    self.triggered = False
                    if(self.next_task_ready):
                        self.call_task()

                    if(self._queue.empty()):
                        self.listener.running = True
                        self.seq_num = 3

                elif(self.seq_num == 3):
                    self.listener.set_completed()
                    self.reboot()

                    if(self.infinteFlag):
                        self.listener.running = True
                        self.seq_num = 1
                    else:
                        self.seq_num = 0
                QtCore.QThread.msleep(50)
                    
class TaskManager(QtCore.QObject):
    messageProcChanged = QtCore.pyqtSignal(str)
    messageZmqTCPServerChanged = QtCore.pyqtSignal(str)
    messageZmqBrokerChanged = QtCore.pyqtSignal(str)

    def __init__(self, commands, parent=None):
        super(TaskManager, self).__init__(parent)
        self._queue = queue.Queue()
        self._queue_id = 0
        self._running = False
        self.commands = commands

        self.process_thread = QtCore.QThread()
        self.worker = Processes(self.commands, "tcp://%s:%s" % ("192.168.0.109", 13000))

        self.worker.moveToThread(self.process_thread)
        self.worker.finished.connect(self.process_thread.quit)

        self.process_thread.started.connect(self.worker.task_process)
        self.worker.task_started.connect(self.on_task_start)
        self.process_thread.start()

        self.next_task_ready = True

        self.proc_dics = dict()

        self.make_task_process()

        #self.make_zmq_tcp_server_process()

    def make_task_process(self):
        self.proc_dics["task"] = QtCore.QProcess()
        self.proc_dics["task"].setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.proc_dics["task"].readyReadStandardOutput.connect(self.on_readyReadStandardOutput)
        self.proc_dics["task"].finished.connect(self.on_cur_task_finished)
        self.proc_dics["task"].started.connect(self.on_cur_task_started)
        self.proc_dics["task"].errorOccurred.connect(self.on_errorOccurred)

    def make_zmq_tcp_server_process(self):
        command = "python zmq_tcp_server.py"

        self.proc_dics["zmq_tcp_server"] = QtCore.QProcess()
        self.proc_dics["zmq_tcp_server"].setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.proc_dics["zmq_tcp_server"].readyReadStandardOutput.connect(self.on_readyReadStandardOutput)
        self.proc_dics["zmq_tcp_server"].finished.connect(self.on_zmq_broker_finished)
        #self.proc_dics["zmq_tcp_server"].started.connect(lambda: self.on_process_start("zmq_tcp_server"), command)
        self.proc_dics["zmq_tcp_server"].errorOccurred.connect(self.on_errorOccurred)

        self.proc_dics["zmq_tcp_server"].start(command)
        print("[script, pid]:", command, self.proc_dics["zmq_tcp_server"].pid())

    def make_zmq_broker_process(self):
        self.proc_dics["zmq_broker"] = QtCore.QProcess()
        self.proc_dics["zmq_broker"].setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.proc_dics["zmq_broker"].readyReadStandardOutput.connect(self.on_readyReadStandardOutput)
        self.proc_dics["zmq_broker"].finished.connect(self.on_zmq_broker_finished)
        self.proc_dics["zmq_broker"].errorOccurred.connect(self.on_errorOccurred)


    def on_zmq_broker_finished(self, exitCode, exitStatus):
        print(exitCode, exitStatus)
        #self.pushButton.setEnabled(True)

    def on_task_start(self, cmd):
        self.proc_dics["task"].start(cmd)

    def on_process_start(self, str_process, cmd):
        self.proc_dics[str_process].start(cmd)

    def start(self):
        self.worker.start()

    def stop(self):
        self.worker.stop()

    def reboot(self):
        self.worker.reboot()
    
    def reboot_tcp_server(self):
        print("reboot_tcp_server")

    def reboot_zmq_broker(self):
        print("reboot_zmq_broker")

    def on_readyReadStandardOutput(self):
        codec = QtCore.QTextCodec.codecForLocale()
        decoder_stdout = codec.makeDecoder()
        process = self.sender()
        text = decoder_stdout.toUnicode(process.readAllStandardOutput())

        if(process == self.proc_dics["task"]):
            self.messageProcChanged.emit(text)
        elif(process == self.proc_dics["zmq_tcp_server"]):
            self.messageZmqTCPServerChanged.emit(text)
        elif(process == self.proc_dics["zmq_tcp_server"]):
            self.messageZmqBrokerChanged.emit(text)    

    def on_cur_task_finished(self):
        process = self.sender()

        if(process == self.proc_dics["task"]):
            print("cur task is finished")
            self.worker.set_task_ready(True)
        """    
        elif(process == self.proc_dics["zmq_tcp_server"]):
            print("on_cur_task_finished: edZmqTCPServerStatus")
        elif(process == self.proc_dics["zmq_broker"]):
            print("on_cur_task_finished: edZmqBrokerStatus")
        """

    def on_cur_task_started(self):
        process = self.sender()
        print("started: ", " ".join([process.program()] + process.arguments()))

    def on_errorOccurred(self, error):
        process = self.sender()
        print("error: ", error, "-", " ".join([process.program()] + process.arguments()))

    def onStateChanged(self):
        process = self.sender()    
        self.worker.set_infinteFlag(process.isChecked())

def has_bash():
    process = QtCore.QProcess()
    process.start("which bash")
    process.waitForStarted()
    process.waitForFinished()
    if process.exitStatus() == QtCore.QProcess.NormalExit:
        return bool(process.readAll())
    return False

# https://stackoverflow.com/questions/57420407/show-realtime-output-of-subprocess-in-a-qdialog
class PipManager(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()
    textChanged = pyqtSignal(str)

    def __init__(self, venv_dir, venv_name, parent=None):
        super().__init__(parent)

        self._venv_dir = venv_dir
        self._venv_name = venv_name

        self._process = QtCore.QProcess(self)
        self._process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self._process.readyReadStandardError.connect(self.onReadyReadStandardError)
        self._process.readyReadStandardOutput.connect(self.onReadyReadStandardOutput)
        #self._process.readyReadStandardOutput.connect(partial(self.dataReady, self.process))
        self._process.stateChanged.connect(self.onStateChanged)
        #self._process.started.connect(self.started)
        self._process.finished.connect(self.finished)
        self._process.finished.connect(self.onFinished)
        self._process.errorOccurred.connect(self.on_errorOccurred)
        #self._process.readyRead.connect(self.on_readReady)
        self._process.setWorkingDirectory(venv_dir)

    def run_command(self, command="", options=None):
        #if has_bash():
        if options is None:
            options = []
        #script = f"""source {self._venv_name}/bin/activate; {command} {" ".join(options)}; deactivate;"""
        #script = f"""{command} {" ".join(options)} """
        self.command = command
        #self._process.start("bash", ["-c", command])
        #QtCore.QTimer.singleShot(100, partial(self._process.start, self.command))
        self._process.start(command)

        print("[script, pid]:", command, self._process.pid())

    def on_errorOccurred(self, error):
        process = self.sender()
        print("error: ", error, "-", " ".join([process.program()] + process.arguments()))

    """
    def on_readReady(self):
        cursor = self._textedit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(str(self._process.readAll(), "utf-8"))
        self._textedit.ensureCursorVisible()
    """

    @pyqtSlot(QtCore.QProcess.ProcessState)
    def onStateChanged(self, state):
        if state == QtCore.QProcess.NotRunning:
            print(self.command, ": not running")
        elif state == QtCore.QProcess.Starting:
            print(self.command, ": starting")
            self.textChanged.emit("aaa")
        elif state == QtCore.QProcess.Running:
            print(self.command, ": running")
            codec = QtCore.QTextCodec.codecForLocale()
            decoder_stdout = codec.makeDecoder()
            text = decoder_stdout.toUnicode(self._process.readAll())
            self.textChanged.emit(text)
            #print(self._process.readAllStandardOutput())

    def onFinished(self, exitCode, exitStatus):
        print(exitCode, exitStatus)

    def onReadyReadStandardError(self):
        message = self._process.readAllStandardError().data().decode().strip()
        print("error:", message)
        self.finished.emit()
        self._process.kill()
        """self.textChanged.emit(message)"""

    def onReadyReadStandardOutput(self):
        message = self._process.readAllStandardOutput().data().decode().strip('\n')
        self.textChanged.emit(message)   

        #message = self._process.readAllStandardOutput().data().decode().strip()
        
        #message = str(self._process.readAllStandardOutput())
        #self.textChanged.emit(message)   
        #codec = QtCore.QTextCodec.codecForLocale()
        #decoder_stdout = codec.makeDecoder()
        #process = self.sender()
        #text = decoder_stdout.toUnicode(process.readAllStandardOutput())
        #self.textChanged.emit(text)


class Widget(QtWidgets.QWidget):
    def __init__(self, ui_file = "", config_file = "", parent=None):
        super(Widget, self).__init__(parent)
        vlay = QtWidgets.QVBoxLayout(self)

        uic.loadUi(ui_file, self)

        str_pBtn_list = ["pBtnRunTasks", 
                         "pBtnStopTasks",
                         "pBtnRebootTasks",
                         "pBtnRebootTCPServer",
                         "pBtnRebootZmqBroker"]

        str_pChkBox_list = ["chkInfiniteStart"]

        str_pTxtEdit_list = ["edProcessStatus",
                        "edZmqTCPServerStatus",
                        "edZmqBrokerStatus"]
                         
        self.pBtn_dicts = dict()
        self.pChkBox_dicts = dict()
        self.pTxtEdit_dicts = dict()

        for str_pBtn in str_pBtn_list:
            self.pBtn_dicts[str_pBtn] = self.findChild(QtWidgets.QPushButton, str_pBtn)

        for str_pChkBox in str_pChkBox_list:
            self.pChkBox_dicts[str_pChkBox] = self.findChild(QtWidgets.QCheckBox, str_pChkBox)

        for str_pTxtEdit in str_pTxtEdit_list:
            self.pTxtEdit_dicts[str_pTxtEdit] = self.findChild(QtWidgets.QPlainTextEdit, str_pTxtEdit)
       
        #self.te = self.findChild(QtWidgets.QTextEdit, "edProcessStatus")
        
        with open(config_file) as f:
            content = f.readlines()
        content = [x.strip() for x in content] 

        print("command contents:", content)

        self.manager = TaskManager(commands = content, parent=self)
        self.manager.worker.init()
        self.manager.messageProcChanged.connect(self.pTxtEdit_dicts["edProcessStatus"].appendPlainText)

        import os
        current_dir = f"""{str(os.path.dirname(os.path.realpath(__file__)))}"""
        print("current_dir:", current_dir)
        venv_name = "/home/user/env38_amd64_1804"

        self.procTCPServer = PipManager(current_dir, venv_name)
        self.procTCPServer.textChanged.connect(self.pTxtEdit_dicts["edZmqTCPServerStatus"].appendPlainText)
        self.procTCPServer.run_command("python zmq_tcp_server.py")
        #self.pip_TCPServer.started.connect(self.manager.start)
        #self.pip_TCPServer.finished.connect(self.manager.reboot)
        
        self.procZmqBroker = PipManager(current_dir, venv_name)
        self.procZmqBroker.textChanged.connect(self.pTxtEdit_dicts["edZmqBrokerStatus"].appendPlainText)
        self.procZmqBroker.run_command("python zmq_broker.py")
        #self.manager.make_zmq_broker_process(self.procTCPServer._process)

        
        self.manager.messageZmqTCPServerChanged.connect(self.pTxtEdit_dicts["edZmqTCPServerStatus"].appendPlainText)
        #self.manager.messageZmqBrokerChanged.connect(self.pTxtEdit_dicts["edZmqBrokerStatus"].append)

        self.pBtn_dicts["pBtnRunTasks"].clicked.connect(self.manager.start)
        self.pBtn_dicts["pBtnStopTasks"].clicked.connect(self.manager.stop)
        self.pBtn_dicts["pBtnRebootTasks"].clicked.connect(self.manager.reboot)
        self.pBtn_dicts["pBtnRebootTasks"].clicked.connect(lambda: self.clear_text("edProcessStatus"))

        self.pBtn_dicts["pBtnRebootTCPServer"].clicked.connect(self.manager.reboot_tcp_server)
        self.pBtn_dicts["pBtnRebootTCPServer"].clicked.connect(lambda: self.clear_text("edZmqTCPServerStatus"))

        self.pBtn_dicts["pBtnRebootZmqBroker"].clicked.connect(self.manager.reboot_zmq_broker)
        self.pBtn_dicts["pBtnRebootZmqBroker"].clicked.connect(lambda: self.clear_text("edZmqBrokerStatus"))


        print("self.pChkBox_dicts:", self.pChkBox_dicts)
        print("self.pTxtEdit_dicts:", self.pTxtEdit_dicts)
        self.pChkBox_dicts["chkInfiniteStart"].clicked.connect(self.manager.onStateChanged)

    def clear_text(self, str_element):
        if(str_element == "all"):
            for element in str_pTxtEdit_list:
                self.pTxtEdit_dicts[element].clear()
        else:
            self.pTxtEdit_dicts[str_element].clear()
        print("cleared (", str_element, ") !")

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Quit?',
                                     'Are you sure you want to quit?',
                                     QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            if not type(event) == bool:
                #
                #self.procTCPServer.deleteLater()
                self.procZmqBroker.deleteLater()

                self.manager.stop()
                self.manager.reboot()
                #self.pip_TCPServer._process.waitForFinished()
                event.accept()     
            else:
                sys.exit()
        else:
            if not type(event) == bool:
                event.ignore()
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Widget(ui_file = "python_frontend.ui",
               config_file = 'config/commands.txt')
    w.show()
    sys.exit(app.exec_())
