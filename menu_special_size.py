'''Menu window for selecting specific game parameters'''

from PyQt5.QtWidgets import (QVBoxLayout, QGroupBox, QHBoxLayout, QFormLayout,
                             QSpinBox, QMessageBox, QDialog, QDialogButtonBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class Size(QDialog):
    def __init__(self, height, width, num, parent=None):
        QDialog.__init__(self, parent)
        # Block windows of the entire application
        self.setWindowModality(Qt.ApplicationModal)
        vbox = QVBoxLayout()

        self.h = height
        self.w = width
        self.n = num

        gBox = QGroupBox('Special settings')

        form = QFormLayout()

        self.height = QSpinBox()
        self.height.setRange(9, 16)
        self.height.setWrapping(True)
        self.height.setValue(self.h)

        self.width = QSpinBox()
        self.width.setRange(9, 30)
        self.width.setWrapping(True)
        self.width.setValue(self.w)

        self.mines = QSpinBox()
        self.mines.setRange(1, 480)
        self.mines.setWrapping(True)
        self.mines.setValue(self.n)

        form.addRow('Height (9 to 16)', self.height)
        form.addRow('Width (9 to 30)', self.width)
        form.addRow('The number of mines per field', self.mines)

        ok_btn = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_btn.accepted.connect(self.checkAnsw)
        cancel_btn = QDialogButtonBox(QDialogButtonBox.Cancel)
        cancel_btn.rejected.connect(self.cancelFunc)

        hbox = QHBoxLayout()
        hbox.addWidget(ok_btn)
        hbox.addWidget(cancel_btn)

        gBox.setLayout(form)

        vbox.addWidget(gBox)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setWindowTitle('Special...')
        self.setWindowIcon(QIcon('./images/logo.png'))

    def checkAnsw(self):
        # Check: did the user change the parameters
        if self.height.value() != self.h or self.width.value() != self.w or self.mines.value() != self.n:
            sq = self.height.value() * self.width.value()
            if self.mines.value() >= 0.9 * sq:
                self.mines.setValue(0.9 * sq - 1)
                QMessageBox.critical(self, 'Attention!',
                         'The number of mines in the field exceeds 90% of the cells\n'
                         'The maximum value is set: {}'.format(self.mines.value()))
            else:
                # Data transfer to the main program window
                self.parent().change = True
                self.parent().height_area = self.height.value()
                self.parent().width_area = self.width.value()
                self.parent().num_mines = self.mines.value()
                if self.mines.value() <= 10:
                    self.parent().num_radar = 3
                elif 10 < self.mines.value() <= 40:
                    self.parent().num_radar = 10
                elif 40 < self.mines.value():
                    self.parent().num_radar = 15
                self.close()
        else:
            self.parent().change = True
            self.close()

    def cancelFunc(self):
        self.close()