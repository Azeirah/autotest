import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import ctl


ico_default = None
ico_waiting = None

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
            self.setIcon(ico_waiting)
            ctl.restart_apache()
            self.setIcon(ico_default)
        elif "trace on; debug off." in t:
            ctl.configure_php_ini(1, 0)
            self.setIcon(ico_waiting)
            ctl.restart_apache()
            self.setIcon(ico_default)
        elif "trace off; debug on." in t:
            ctl.configure_php_ini(0, 1)
            self.setIcon(ico_waiting)
            ctl.restart_apache()
            self.setIcon(ico_default)
        elif "everything off" in t:
            ctl.configure_php_ini(0, 0)
            self.setIcon(ico_waiting)
            ctl.restart_apache()
            self.setIcon(ico_default)
        elif "restart apache" in t:
            self.setIcon(ico_waiting)
            ctl.restart_apache()
            self.setIcon(ico_default)



def main():
    global ico_default, ico_waiting
    app = QtWidgets.QApplication(sys.argv)
    ico_default = QtGui.QIcon('icon.ico')
    ico_waiting = QtGui.QIcon('icon-wating.ico')
    w = QtWidgets.QWidget()
    trayIcon = SystemTrayIcon(ico_default, w)
    trayIcon.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
