# Dialog - End of Game

import sys
from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QHBoxLayout,
                             QApplication, QPushButton, QGroupBox, QDialog)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt

class Over(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        # Block windows of the entire application
        self.setWindowModality(Qt.ApplicationModal)

        vbox = QVBoxLayout()
        lbl_vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        gbox = QGroupBox()

        pre_text = '\nNumber of moves: {}\nTime spent: {} sec.'.format(self.parent().num_moves,
                                                                               self.parent().second)

        if self.parent().win:
            text = 'You Win!' + pre_text
        else:
            text = 'You lose!' + pre_text

        lbl = QLabel(text)
        lbl.setFont(QFont('Times', 10, QFont.Bold))
        lbl.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        lbl_vbox.addWidget(lbl)
        gbox.setLayout(lbl_vbox)
        vbox.addWidget(gbox)

        n_game_btn = QPushButton('New game')
        n_game_btn.clicked.connect(self.n_game)
        n_game_btn.setAutoDefault(True)
        hbox.addWidget(n_game_btn)

        exit_btn = QPushButton('Quit')
        exit_btn.clicked.connect(self.exit_game)
        exit_btn.setAutoDefault(True)
        hbox.addWidget(exit_btn)

        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.resize(250, 150)
        self.setWindowTitle('Game over')
        self.setWindowIcon(QIcon('images/logo.png'))
        self.show()

    def n_game(self):
        self.parent().new_exit = True
        self.close()

    def exit_game(self):
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = True
    main = Over()
    sys.exit(app.exec_())