'''A window for selecting, managing, and further loading game saves'''

import sys
from PyQt5 import QtSql
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QHBoxLayout,
                             QApplication, QPushButton, QGroupBox, QMessageBox)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt

class Load(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        # Block windows of the entire application
        self.setWindowModality(Qt.ApplicationModal)

        # DB connection
        con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        con.setDatabaseName('data.sqlite')
        con.open()

        # View tables in the database
        tabs = con.tables()

        if 'save' not in tabs:
            self.empty()
        else:
            # Request creation
            query = QtSql.QSqlQuery()
            # Checking the saves table for data availability and retrieval
            query.exec('SELECT * FROM save ORDER BY dt')
            self.lst = []
            if query.isActive():
                query.first()
                while query.isValid():
                    data = dict(id=query.value('id'),
                                dt=query.value('dt'),
                                play_time=query.value('play_time'),
                                num_moves=query.value('num_moves'),
                                num_radar=query.value('num_radar'),
                                len_row=query.value('len_row'),
                                field=query.value('field'))
                    self.lst.append(data)
                    query.next()
            # Window selection
            if len(self.lst) == 0:
                self.empty()
            else:
                self.notEmpty()

        # Closing a database connection
        con.close()

        # Saving the SAVE window
        self.resize(300, 250)
        self.setWindowTitle('Saves')
        self.setWindowIcon(QIcon('images/logo.png'))
        self.show()

    # Window if the table is empty
    def empty(self):
        vbox = QVBoxLayout()
        vvbox = QVBoxLayout()
        gbox = QGroupBox()

        lbl = QLabel('No Saves')
        lbl.setFont(QFont('Times', 9, QFont.Bold))
        lbl.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        cancel_btn = QPushButton('Back')
        cancel_btn.clicked.connect(self.close)
        cancel_btn.setShortcut('Esc')
        cancel_btn.setAutoDefault(True)

        vvbox.addWidget(lbl)
        gbox.setLayout(vvbox)
        vbox.addWidget(gbox)
        vbox.addWidget(cancel_btn)

        self.setLayout(vbox)

    # Window if the save table HAS RECORDS
    def notEmpty(self):

        main_vbox = QVBoxLayout()
        i = 0
        mark, load_btn, del_btn, id_row = [], [], [], []

        # Creating a list of id records in the save table to transmit button clicks
        for k in self.lst:
            id_row.append(k['id'])

        # Creating output in the window of each record
        for dct in self.lst:
            vbox = QVBoxLayout()
            hbox = QHBoxLayout()
            gbox = QGroupBox()

            mark.append(QLabel('Save ' + str(i+1) + '\n' +
                          'Recording time: ' + dct['dt'], self))
            mark[i].setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            mark[i].setFont(QFont('Times', 9, QFont.Bold))

            load_btn.append(QPushButton('Download Record'))
            load_btn[i].clicked.connect(lambda state, dct=dct: self.load(dct))
            load_btn[i].setAutoDefault(True)

            del_btn.append(QPushButton('Delete Record', self))
            del_btn[i].clicked.connect(lambda state, i=i: self.delete_row(mark[i], del_btn[i],
                                                                          load_btn[i], id_row[i]))
            del_btn[i].setAutoDefault(True)

            hbox.addWidget(load_btn[i])
            hbox.addWidget(del_btn[i])

            vbox.addWidget(mark[i])
            vbox.addLayout(hbox)

            gbox.setLayout(vbox)

            main_vbox.addWidget(gbox)

            i += 1

        clear_btn = QPushButton('Clear all')
        clear_btn.clicked.connect(self.delete_all)
        clear_btn.setAutoDefault(True)
        cancel_btn = QPushButton('Back')
        cancel_btn.clicked.connect(self.back)
        cancel_btn.setShortcut('Esc')
        cancel_btn.setAutoDefault(True)

        btn_hbox = QHBoxLayout()

        btn_hbox.addWidget(clear_btn)
        btn_hbox.addWidget(cancel_btn)
        main_vbox.addLayout(btn_hbox)

        self.setLayout(main_vbox)

    def load(self, dct):
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                   'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']

        # Retrieving Game Field Data
        len_field = len(dct['field'])
        len_row = dct['len_row']
        field = []
        for i in range(int(len_field / len_row)):
            row = []
            for j in range(len_row*i, len_row*(i+1)):
                if dct['field'][j] in letters:
                    value = letters.index(dct['field'][j]) + 10
                    row.append(value)
                else:
                    row.append(int(dct['field'][j]))
            field.append(row)
        self.parent().loading = True

        self.parent().field = list(map(list, field))
        self.parent().second = dct['play_time']
        self.parent().num_moves = dct['num_moves']
        self.parent().num_radar = dct['num_radar']

        self.back()

    # Method for deleting a specific record
    def delete_row(self, mark, del_btn, load_btn, id_row):
        con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        con.setDatabaseName('data.sqlite')
        con.open()

        query = QtSql.QSqlQuery()
        query.prepare('DELETE FROM save WHERE id = ?')
        query.addBindValue(id_row)
        query.exec_()

        con.close()

        mark.setText('Record deleted')
        del_btn.setEnabled(False)
        load_btn.setEnabled(False)

    # Method to delete all records
    def delete_all(self):
        con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        con.setDatabaseName('data.sqlite')
        con.open()
        query = QtSql.QSqlQuery()
        query.exec('DELETE FROM save')
        con.close()

        # successful deletion of all saves
        QMessageBox.information(self, 'Delete', 'All save deleted')

        # Close the save window, return to the main game window
        self.back()

    def back(self):
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Load()
    sys.exit(app.exec_())