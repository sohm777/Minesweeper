'''game save and save management module'''

import datetime
from PyQt5 import QtSql
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QHBoxLayout,
                             QPushButton, QGroupBox, QMessageBox)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt

class Save(QDialog):
    def __init__(self, second, num_moves, num_radar, len_row, field, parent=None):
        QDialog.__init__(self, parent)
        # Block windows of the entire application
        self.setWindowModality(Qt.ApplicationModal)

        # Play time
        self.second = second
        # Numbers of moves
        self.num_moves = num_moves
        # Number of Remaining Tips - Radar
        self.num_radar = num_radar
        # Length of one field line (field width)
        self.len_row = len_row
        # Playing field
        self.field = field

        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                   'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']

        self.text_field = ''
        for row in self.field:
            for val in row:
                if val > 9:
                    self.text_field += letters[val - 10]
                else:
                    self.text_field += str(val)

        # Opening (creating) a database
        con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        con.setDatabaseName('data.sqlite')
        con.open()

        # View tables in the database
        tabs = con.tables()
        if 'save' not in tabs:
            query = QtSql.QSqlQuery()
            query.exec(
                'CREATE TABLE save(id INTEGER PRIMARY KEY autoincrement, dt TIMESTAMP, play_time INTEGER, num_moves INTEGER, num_radar INTEGER, len_row INTEGER, field TEXT)')
            query.finish()

        # Checking the saves table for data availability and retrieval
        query = QtSql.QSqlQuery()
        query.exec("SELECT * FROM save ORDER BY dt")
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

        # Closing a database connection
        con.close()

        # Window selection
        if len(self.lst) < 3:
            self.empty()
        else:
            self.notEmpty()

    def empty(self):
        self.setWindowIcon(QIcon('images/logo.png'))
        con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        con.setDatabaseName('data.sqlite')
        con.open()

        query = QtSql.QSqlQuery()

        dt = datetime.datetime.today().strftime('%H:%M:%S %d/%m/%Y')

        query.prepare('INSERT INTO save VALUES(null, ?, ?, ?, ?, ?, ?)')
        query.addBindValue(dt)
        query.addBindValue(self.second)
        query.addBindValue(self.num_moves)
        query.addBindValue(self.num_radar)
        query.addBindValue(self.len_row)
        query.addBindValue(self.text_field)
        query.exec_()

        con.close()

        # successful save
        QMessageBox.information(self, 'Save', 'Game saved successfully')

    def notEmpty(self):
        # Creating a window without drawing
        self.resize(300, 250)
        self.setWindowTitle('Saves')
        self.setWindowIcon(QIcon('images/logo.png'))

        msg = 'Save Limit Reached'
        # successful save
        QMessageBox.information(self, 'Save', msg)

        main_vbox = QVBoxLayout()

        lbl = QLabel('Choose save to overwrite')
        lbl.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        lbl.setFont(QFont('Times', 9))
        main_vbox.addWidget(lbl)

        i = 0
        mark, upd_btn, del_btn, id_row = [], [], [], []

        # Creating a list of id records in the save table to transmit button clicks
        for k in self.lst:
            id_row.append(k['id'])

        # Creating output in the window of each record
        for dct in self.lst:
            vbox = QVBoxLayout()
            hbox = QHBoxLayout()
            gbox = QGroupBox()

            mark.append(QLabel('Save ' + str(i+1) + '\n' +
                               'date of recording: ' + dct['dt'], self))
            mark[i].setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            mark[i].setFont(QFont('Times', 9, QFont.Bold))

            upd_btn.append(QPushButton('Overwrite'))
            upd_btn[i].clicked.connect(lambda state, i=i:
                                       self.update_row(mark[i], upd_btn,
                                                       id_row[i]))
            upd_btn[i].setAutoDefault(True)

            del_btn.append(QPushButton('Delete record', self))
            del_btn[i].clicked.connect(lambda state, i=i:
                                       self.delete_row(mark[i], upd_btn[i],
                                                       del_btn[i], id_row[i]))
            del_btn[i].setAutoDefault(True)

            hbox.addWidget(upd_btn[i])
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
        cancel_btn.clicked.connect(self.close)
        cancel_btn.setShortcut('Esc')
        cancel_btn.setAutoDefault(True)

        btn_hbox = QHBoxLayout()

        btn_hbox.addWidget(clear_btn)
        btn_hbox.addWidget(cancel_btn)
        main_vbox.addLayout(btn_hbox)

        self.setLayout(main_vbox)

        # Saving the SAVE window
        self.show()

    def delete_row(self, mark, upd_btn, del_btn, id_row):
        con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        con.setDatabaseName('data.sqlite')
        con.open()

        query = QtSql.QSqlQuery()
        query.prepare('DELETE FROM save WHERE id=?')
        query.addBindValue(id_row)
        query.exec_()

        con.close()

        # Change the text of the inscription
        mark.setText('Record deleted')

        # Button deactivation
        del_btn.setEnabled(False)
        upd_btn.setEnabled(False)

    # Method to delete all records
    def delete_all(self):
        con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        con.setDatabaseName('data.sqlite')
        con.open()
        query = QtSql.QSqlQuery()
        query.exec('DELETE FROM save')
        con.close()

        # successful deletion of all records
        QMessageBox.information(self, 'Delete', 'All save deleted')

        # Close the save window, return to the main game window
        self.close()

    def update_row(self, mark, upd_btn_all, id_row):
        dt = datetime.datetime.today().strftime('%H:%M:%S %d/%m/%Y')

        con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        con.setDatabaseName('data.sqlite')
        con.open()

        query = QtSql.QSqlQuery()
        query.prepare('UPDATE save SET dt=?, play_time=?, num_moves=?, num_radar=?, len_row=?, field=? where id=?')
        query.addBindValue(dt)
        query.addBindValue(self.second)
        query.addBindValue(self.num_moves)
        query.addBindValue(self.num_radar)
        query.addBindValue(self.len_row)
        query.addBindValue(self.text_field)
        query.addBindValue(id_row)
        query.exec_()

        con.close()

        mark.setText('Record Overwritten')

        # Button deactivation
        for i in upd_btn_all:
            i.setEnabled(False)