# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\test2.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets

def do_other_thing(arg):
    print(arg)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(227, 60)

        self.buttfunc = 0
        self.incement = 0

        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")

        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setObjectName("pushButton")

        self.verticalLayout.addWidget(self.pushButton)

        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")

        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        self.pushButton.clicked.connect(self.do_thing)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Snedige Greier"))
        self.pushButton.setText(_translate("Form", "OK!!!"))
        self.label.setText(_translate("Form", "FACK OFF!"))

    def do_thing(self):
        print('HALLA')
        if callable(self.buttfunc):
            self.buttfunc(self.incement)
        self.label.setText('PENIS')
        self.incement = self.incement + 1

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)

    ting = 0
    if callable(ting):
        ting()

    #ui.buttfunc = do_other_thing
    #ui.pushButton.clicked.connect(do_other_thing)

    #Enable/Disable button
    #ui.pushButton.setEnabled(False)tutorial

    # dict_test = dict()
    # dict_test['a'] = {'ip': '1', 'Mac': '2', 'Uni': 3}
    # dict_test['b'] = {'ip': '1', 'Mac': '2', 'Uni': 3}
    # print(dict_test)

    Form.show()
    sys.exit(app.exec_())
