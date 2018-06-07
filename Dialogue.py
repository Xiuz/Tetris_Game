from PyQt5.QtWidgets import QApplication,QDialog
from PyQt5.QtCore import pyqtSignal
from Log_interface import Ui_Form
import sqlite3
import os,sys

class LogDialogue(QDialog,Ui_Form):

    login_clicked_signal = pyqtSignal(str,str)
    register_clicked_signal = pyqtSignal(str,str)
    login_success_signal = pyqtSignal(str,str)

    def __init__(self,parent=None):
        super(LogDialogue,self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.login_clicked)
        self.pushButton_2.clicked.connect(self.register_clicked)
        self.login_clicked_signal.connect(self.LogIn)
        self.register_clicked_signal.connect(self.Register)

        self.initDatabase()

    def login_clicked(self):
        self.login_clicked_signal.emit(str(self.lineEdit.text()),str(self.lineEdit_2.text()))
        print(str(self.lineEdit.text()),str(self.lineEdit_2.text()))

    def register_clicked(self):
        self.register_clicked_signal.emit(str(self.lineEdit.text()),str(self.lineEdit_2.text()))

    def initDatabase(self):
        if 'user_data.db3' in os.listdir():
            return
        conn = sqlite3.connect('user_data.db3')
        conn.execute('''CREATE TABLE USER 
                (NAME TEXT NOT NULL ,
                PASSWORD TEXT NOT NULL ,
                 SCORE INT NOT NULL );''')
        conn.execute("INSERT INTO USER VALUES ('Zhuxi','woailaopo',1000)")
        conn.commit()
        conn.close()

    def LogIn(self,user,pwd):
        conn = sqlite3.connect('user_data.db3')
        cur =conn.cursor()
        cur.execute('SELECT * FROM USER')
        for item in cur.fetchall():
            if (user == item[0]) and (pwd == item[1]):
                self.label_3.setText('登陆成功!')
                self.login_success_signal.emit(user,pwd)
                conn.close()
                return (user,pwd)
        self.label_3.setText("登陆失败,请确认账户和密码")
        conn.close()

    def Register(self,user,pwd):
        conn = sqlite3.connect('user_data.db3')
        cur = conn.cursor()
        cur.execute('SELECT * FROM USER')
        for item in cur.fetchall():
            if (user == item[0]):
                self.label_3.setText('已注册，请登陆！')
                conn.close()
                return
        cur.execute("INSERT INTO USER VALUES ('{user}','{pwd}',0)".format(user=user,pwd=pwd))
        conn.commit()
        conn.close()
        self.label_3.setText('注册成功！')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    log = LogDialogue()
    log.show()
    sys.exit(app.exec_())
