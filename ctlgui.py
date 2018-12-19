import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import ctl


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        menu = QtWidgets.QMenu(parent)
        exitAction = menu.addAction("trace on; debug on.")
        exitAction = menu.addAction("trace on; debug off.")
        exitAction = menu.addAction("trace off; debug on.")
        exitAction = menu.addAction("everything off")
        exitAction = menu.addAction("restart apache")
        exitAction = menu.addAction("Exit")
        self.setContextMenu(menu)
        menu.triggered.connect(self.exit)

    def exit(self, item):
        t = item.text()
        if "Exit" in t:
            QtCore.QCoreApplication.exit()
        elif "trace on; debug on." in t:
            ctl.configure_php_ini(1, 1)
            ctl.restart_apache()
        elif "trace on; debug off." in t:
            ctl.configure_php_ini(1, 0)
            ctl.restart_apache()
        elif "trace off; debug on." in t:
            ctl.configure_php_ini(0, 1)
            ctl.restart_apache()
        elif "everything off" in t:
            ctl.configure_php_ini(0, 0)
            ctl.restart_apache()
        elif "restart apache" in t:
            ctl.restart_apache()



def main(image):
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    trayIcon = SystemTrayIcon(QtGui.QIcon(image), w)
    trayIcon.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    on='icon.ico'
    main(on)