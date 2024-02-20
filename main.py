import minecraft_launcher_lib
import subprocess
from PyQt5 import QtCore, QtGui, QtWidgets
from uuid import uuid1

minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()

class LaunchThread(QtCore.QThread):
    launch_setup_signal = QtCore.pyqtSignal(str, str)
    progress_update_signal = QtCore.pyqtSignal(int, int, str)
    state_update_signal = QtCore.pyqtSignal(bool)

    version_id = ''
    username = ''

    progress = 0
    progress_max = 0
    progress_label = ''

    def __init__(self):
        super().__init__()

        self.launch_setup_signal.connect(self.launch_setup)

    def launch_setup(self, version_id, username):
        self.version_id = version_id
        self.username = username

    def update_progress_label(self, value):
        self.progress_label = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)

    def update_progress(self, value):
        self.progress = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)

    def update_progress_max(self, value):
        self.progress_max = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)

    def run(self):
        self.state_update_signal.emit(True)

        minecraft_launcher_lib.install.install_minecraft_version(versionid=self.version_id, minecraft_directory=minecraft_directory, callback={'setStatus': self.update_progress_label, 'setProgress': self.update_progress, 'setMax': self.update_progress_max})

        options = {
            'username': self.username,
            'uuid': str(uuid1()),
            'token': ''
        }
        
        self.state_update_signal.emit(False)
        subprocess.run(minecraft_launcher_lib.command.get_minecraft_command(version=self.version_id, minecraft_directory=minecraft_directory, options=options))


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(268, 220)
        MainWindow.setMinimumSize(QtCore.QSize(268, 220))
        MainWindow.setMaximumSize(QtCore.QSize(268, 220))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.username = QtWidgets.QLineEdit(self.centralwidget)
        self.username.setObjectName("username")
        self.username.setMaxLength(16)
        self.verticalLayout.addWidget(self.username)
        self.version_select = QtWidgets.QComboBox(self.centralwidget)
        self.version_select.setObjectName("version_select")
        self.verticalLayout.addWidget(self.version_select)

        latest_version = minecraft_launcher_lib.utils.get_latest_version()["release"]
        self.version_select.addItem('Latest release ' + latest_version)

        for version in minecraft_launcher_lib.utils.get_available_versions(minecraft_launcher_lib.utils.get_minecraft_directory()):
            if minecraft_launcher_lib.utils.is_vanilla_version(version['id']):
                self.version_select.addItem(version['type'] + ' ' + version['id'])
            else:
                self.version_select.addItem(version['id'])

        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem1)
        self.progress_label = QtWidgets.QLabel(self.centralwidget)
        self.progress_label.setText('')
        self.progress_label.setVisible(False)
        self.verticalLayout.addWidget(self.progress_label)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.progressBar.setVisible(False)

        self.play_button = QtWidgets.QPushButton(self.centralwidget)
        self.play_button.setAutoFillBackground(False)
        self.play_button.setStyleSheet("")
        self.play_button.setFlat(False)
        self.play_button.setObjectName("play_button")
        self.play_button.clicked.connect(self.launch_minecraft)
        self.verticalLayout.addWidget(self.play_button)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.launch_thread = LaunchThread()
        self.launch_thread.state_update_signal.connect(self.state_update)
        self.launch_thread.progress_update_signal.connect(self.update_progress)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PLauncher"))
        self.username.setPlaceholderText(_translate("MainWindow", "Enter Nickname"))
        self.play_button.setText(_translate("MainWindow", "Play"))

    def state_update(self, value):
        self.play_button.setDisabled(value)
        self.progress_label.setVisible(value)
        self.progressBar.setVisible(value)

    def update_progress(self, progress, max_progress, label):
        self.progressBar.setValue(progress)
        self.progressBar.setMaximum(max_progress)
        self.progress_label.setText(label)

    def launch_minecraft(self):
        latest_version = ('Latest release ' + minecraft_launcher_lib.utils.get_latest_version()["release"])
        if latest_version == self.version_select.currentText():
            self.launch_thread.launch_setup_signal.emit(self.version_select.currentText().split(' ', maxsplit=2)[-1], self.username.text())
        else:
            self.launch_thread.launch_setup_signal.emit(self.version_select.currentText().split(' ', maxsplit=1)[-1], self.username.text())
        self.launch_thread.start()

if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)

    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
