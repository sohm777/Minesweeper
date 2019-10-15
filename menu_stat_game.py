import sys, datetime
from PyQt5 import QtSql
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QMessageBox,
                             QLabel, QHBoxLayout,
                             QApplication, QPushButton,
                             QGroupBox, QTableView)
from PyQt5.QtGui import QIcon, QFont, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

class Stat(QDialog):
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

        query = QtSql.QSqlQuery()

        # Checking the stat table for data availability and retrieval
        query.exec("SELECT * FROM stat")
        self.lst = []
        if query.isActive():
            query.first()
            while query.isValid():
                data = dict(id=query.value('id'),
                            dt=query.value('dt'),
                            size=query.value('size'),
                            mines=query.value('mines'),
                            moves=query.value('moves'),
                            play_time=query.value('play_time'),
                            wins=query.value('wins'))
                self.lst.append(data)
                query.next()
        # Closing a database connection
        con.close()

        if 'stat' not in tabs or len(self.lst) == 0:
            self.empty()
        else:
            self.not_empty()

        # Drawing the Statistics window
        self.resize(550, 510)
        self.setWindowTitle('Statistics')
        self.setWindowIcon(QIcon('images/logo.png'))
        self.show()

    def empty(self):
        vbox = QVBoxLayout()
        vvbox = QVBoxLayout()
        gbox = QGroupBox()

        lbl = QLabel('No statistics')
        lbl.setFont(QFont('Times', 10, QFont.Bold))
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

    def not_empty(self):
        # For the correct output of information in the table
        self.lst.reverse()

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        h_btn = QHBoxLayout()
        vvbox = QVBoxLayout()
        gbox = QGroupBox()

        tv = QTableView()
        sti = QStandardItemModel(parent=hbox)
        sti.setColumnCount(6)

        # Table headers
        sti.setHorizontalHeaderLabels(['Date', 'Field', 'Mines', 'Moves', 'Time of play', 'Result'])

        # Counting victories and defeats
        win, lose = 0, 0
        for row in self.lst:
            if row['wins'] == 'victory':
                win += 1
            elif row['wins'] == 'losing':
                lose += 1

        # Filling a table with data
        for num, row in enumerate(self.lst):
            if num > 9:
                break
            item1 = QStandardItem(row['dt'])
            item2 = QStandardItem(row['size'])
            item3 = QStandardItem(row['mines'])
            item4 = QStandardItem(row['moves'])
            item5 = QStandardItem(row['play_time'] + ' сек')
            item6 = QStandardItem(row['wins'])
            sti.appendRow([item1, item2, item3, item4, item5, item6])

        tv.setModel(sti)
        tv.resizeColumnsToContents()
        tv.resizeRowToContents(0)
        tv.setColumnWidth(1, 50)
        tv.setColumnWidth(2, 50)
        tv.setColumnWidth(3, 50)
        tv.setColumnWidth(4, 100)
        tv.setColumnWidth(5, 80)

        lbl_2 = QLabel('All games: {}\nWins: {}\nTotal lesions: {}'.format(str(len(self.lst)), str(win), str(lose)))
        lbl_2.setFont(QFont('Times', 12))
        lbl_2.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        clear_btn = QPushButton('Clear')
        clear_btn.clicked.connect(self.clear)
        clear_btn.setAutoDefault(True)

        back_btn = QPushButton('Back')
        back_btn.clicked.connect(self.close)
        back_btn.setShortcut('Esc')
        back_btn.setAutoDefault(True)

        hbox.addWidget(tv)
        vvbox.addWidget(lbl_2)
        gbox.setLayout(vvbox)
        vbox.addLayout(hbox)
        vbox.addWidget(gbox)
        h_btn.addWidget(clear_btn)
        h_btn.addWidget(back_btn)
        vbox.addLayout(h_btn)

        self.setLayout(vbox)

    def clear(self):
        con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        con.setDatabaseName('data.sqlite')
        con.open()
        query = QtSql.QSqlQuery()
        query.exec('DELETE from stat')
        con.close()

        # Info window on successful deletion of all data
        QMessageBox.information(self, 'Delete', 'Statistics is cleared')

        # Closing the window, returning to the main game window
        self.close()

# Saving game results
# *args: size, mines, moves, play_time, wins
def saveResult(*args):
    # Opening (creating) a database
    con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    con.setDatabaseName('data.sqlite')
    con.open()

    # View tables in the database
    tabs = con.tables()
    # Request creation
    query = QtSql.QSqlQuery()

    sql_query = 'CREATE TABLE stat(id INTEGER PRIMARY KEY autoincrement, dt TIMESTAMP, size TEXT, mines TEXT, moves TEXT, play_time TEXT, wins TEXT)'

    # Creating a stat table if it does not exist
    if 'stat' not in tabs:
        query.exec(sql_query)
        query.finish()

    # Stat table population
    dt = datetime.datetime.today().strftime('%H:%M:%S %d/%m/%Y')

    query.prepare('INSERT INTO stat VALUES(null, ?, ?, ?, ?, ?, ?)')
    query.addBindValue(dt)
    for k in args:
        query.addBindValue(k)
    query.exec_()

    # Closing a database connection
    con.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Stat()
    sys.exit(app.exec_())