'''Creating one (each) cell of the playing field'''

import random
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import (QIcon, QColor, QPen,QBrush, QPainter,
                         QPalette, QPixmap, QImage)
from PyQt5.QtCore import Qt, QSize, QEvent

class Cell(QWidget):

    def __init__(self, x, y, value, smile_btn, timerFunc,
                 showMoves, checkBTN, usedFlag,
                 radar, changeValue, parent=None):
        QWidget.__init__(self, parent)

        # Size of one cell (buttons on the field)
        self.setFixedSize(QSize(30, 30))
        # Smile-button
        self.smile_btn = smile_btn
        # Timer function
        self.timerFunc = timerFunc
        # Move number (counting and display on LSD)
        self.showMoves = showMoves
        # Number of flags
        self.usedFlag = usedFlag
        # The value of this cell (blank, digit or mine)
        self.value = value
        # Progress Check Method
        self.checkBTN = checkBTN
        # RADAR Method
        self.radar = radar
        # Cell Value Change Method
        self.changeValue = changeValue
        # Cell coordinates
        self.x = x
        self.y = y

        # Button State
        # Controls whether the button is clamped (Change color and Smile-button)
        self.is_pressed = False
        # Whether the button is pressed - whether the cell is open
        if 9 < self.value < 19:
            self.is_open = True
        else:
            self.is_open = False
        # Mine button
        if self.value == 9:
            self.is_mine = True
        else:
            self.is_mine = False
        # Flag button
        if 19 < self.value < 30:
            self.is_flag = True
        else:
            self.is_flag = False

    def paintEvent(self, event):
        painter = QPainter(self)
        # Smooth edges of the drawing, if possible
        painter.setRenderHint(QPainter.Antialiasing)
        GREY = QColor('grey')
        l_GREY = QColor('lightgrey')
        BLACK = QColor('black')
        WHITE = QColor('white')

        # The rectangle that needs to be updated
        square = event.rect()

        # Change cell color while clicking
        if self.is_pressed and not self.is_flag:
            color_outer = BLACK
            color_inner = GREY
        elif self.is_flag:
            color_outer = l_GREY
            color_inner = WHITE
        else:
            color_outer = GREY
            color_inner = l_GREY

        if self.is_open:
            COLOR = self.palette().color(QPalette.Background)
            color_outer = COLOR
            color_inner = COLOR

        brush = QBrush(color_inner)
        # Fill a rectangle with a brush color
        painter.fillRect(square, brush)
        pen = QPen(color_outer)
        pen.setWidth(1)
        painter.setPen(pen)
        # Draws a rectangle
        painter.drawRect(square)

        # Right-click flag drawing
        if self.is_flag and not self.is_open:
            painter.drawPixmap(square, QPixmap(QImage('./images/flag.png')))

        # Drawing numbers of cells and mines after clicking on a button
        if self.is_open and not self.is_flag and 0 < self.value < 9:
            painter.drawPixmap(square, QPixmap(QImage('./images/{}.png'.format(self.value+10))))
        elif self.is_open and not self.is_flag and 10 < self.value < 19:
            painter.drawPixmap(square, QPixmap(QImage('./images/{}.png'.format(self.value))))
        elif self.is_open and not self.is_flag and self.value == 9:
            painter.drawPixmap(square, QPixmap(QImage('./images/logo.png')))

    # Capturing the mouse input event on the button area
    def event(self, event):
        if event.type() == QEvent.Enter and not self.is_open and not self.is_flag and self.value == 9:
            self.smile_btn.setIcon(QIcon('./images/bomb.png'))
        elif event.type() == QEvent.Enter and not self.is_open and not self.is_flag and self.value != 9:
            view = random.randint(1, 3)
            if view == 1:
                # Random image of smile_btn
                img = random.randint(1, 8)
                source = './images/{}.png'.format(img)
                self.smile_btn.setIcon(QIcon(source))
        elif event.type() == QEvent.Leave:
            self.smile_btn.setIcon(QIcon('./images/smile.png'))
        return QWidget.event(self, event)

    # Event when the mouse button is pressed
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_pressed = True
            if not self.is_open and not self.is_flag:
                # Random image of smile_btn
                img = random.randint(1, 8)
                source = './images/{}.png'.format(img)
                self.smile_btn.setIcon(QIcon(source))
        elif event.button() == Qt.MiddleButton:
            self.radar(True, self.x, self.y)
        self.update()

    # Event: LMB or RMB released
    def mouseReleaseEvent(self, event):
        self.smile_btn.setIcon(QIcon('./images/smile.png'))
        self.timerFunc(start=True, pause=True)
        if event.button() == Qt.LeftButton:
            self.is_pressed = False
            if not self.is_flag and not self.is_open:
                self.is_open = True
                self.changeValue(self.value + 10, self.x, self.y)
                self.checkBTN(True, self.x, self.y)
        elif event.button() == Qt.RightButton:
            if self.is_flag:
                self.is_flag = False
                self.changeValue(self.value - 20, self.x, self.y)
            # If the cell is not open and the number of flags is not exceeded
            elif not self.is_open and self.usedFlag():
                self.is_flag = True
                self.changeValue(self.value + 20, self.x, self.y)
            # Flag on a mine?
            self.checkBTN(False)
        elif event.button() == Qt.MiddleButton:
            self.radar(False)
        self.update()

def area(width, height, num_of_mines):

    # Create an empty field
    field = []
    for i in range(height):
        row = []
        for j in range(width):
            row.append(0)
        field.append(row)

    # Setting mines on the field
    while num_of_mines > 0:
        x = random.randint(0, height-1)
        y = random.randint(0, width-1)
        if field[x][y] == 0:
            field[x][y] = 9
            num_of_mines -= 1

    # Filling the remaining cells
    for x in range(height):
        for y in range(width):
            cell = field[x][y]
            around_mine = 0
            if cell != 9:
                for i in range(x-1, x+2):
                    for j in range(y-1, y+2):
                        if 0 <= i < height and 0 <= j < width and field[i][j] == 9:
                            around_mine += 1
            if field[x][y] != 9:
                field[x][y] = around_mine

    return field