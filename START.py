# coding=utf-8
'''main program launch file'''
import sys
from PyQt5.QtWidgets import (QWidget, QMainWindow, QAction, QMessageBox,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QDesktopWidget, QApplication, QPushButton,
                             QLCDNumber, QLabel, QFrame, QGroupBox, QLayout)
from PyQt5.QtGui import QIcon, QImage
from PyQt5.QtCore import Qt, QSize, QTimer, QMargins
from cells import Cell, area
from game_over import Over
from menu_stat_game import Stat, saveResult
from menu_save_game import Save
from menu_load_game import Load
from menu_special_size import Size

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        # number of calls - new game
        self.CH = 0

        # the game timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.second_on_LSD)

        # the number of movies
        self.num_moves = 0
        # the second of game
        self.second = 0
        # number of times the radar-button is pressed
        self.num_radar = 3

        # The initial height of the playing field
        self.height_area = 9
        # The initial width of the playing field
        self.width_area = 9
        # Initial number of mines per field
        self.num_mines = 10

        # loading-flag
        self.loading = False

        # Creating a playing field
        self.createAll()

        # Creating a playing menu
        self.createMenu()

    # Creating playing field components
    def createAll(self):

        # New game or loaded from save?
        if not self.loading:
            # Filling the field with mines at the beginning of the game
            self.field = area(self.width_area, self.height_area, self.num_mines)

        self.loading = False

        # The central widget
        self.mainWidget = QWidget(self)
        self.setCentralWidget(self.mainWidget)

        # The main layer
        self.main_vBox = QVBoxLayout(self.mainWidget)

        # The layer Info-Board
        self.hBox = QHBoxLayout()

        # Playing field layer
        self.grid = QGridLayout()

        # Top buttons (info-board)
        self.lcd_left = QLCDNumber()
        self.lcd_left.setFixedSize(QSize(100, 30))
        self.hBox.addWidget(self.lcd_left)

        self.smile_btn = QPushButton()
        self.smile_btn.setFixedSize(QSize(40, 40))
        self.smile_btn.setIconSize(QSize(40, 40))
        self.smile_btn.setIcon(QIcon('./images/smile.png'))
        self.smile_btn.setFlat(True)  # no frame
        self.smile_btn.clicked.connect(self.newGameAction)
        self.hBox.addWidget(self.smile_btn)

        self.lcd_right = QLCDNumber()
        self.lcd_right.setFixedSize(QSize(100, 30))
        self.hBox.addWidget(self.lcd_right)

        self.main_vBox.addLayout(self.hBox)

        # Playing field
        gbox = QGroupBox()
        gbox.setStyleSheet('background-color: white')

        # Adding a playing field
        self.gameArea()

        self.lcd_left.display(self.num_moves)
        self.lcd_right.display(self.second)

        gbox.setLayout(self.grid)
        self.main_vBox.addWidget(gbox)

        self.statusBar().showMessage('Go!')
        self.setLayout(self.main_vBox)

    # Creating a game menu
    def createMenu(self):
        # Menu Events - Game
        newGame = QAction('New game', self)
        newGame.setShortcut('Ctrl+N')
        newGame.triggered.connect(self.newGameAction)
        newGame.setStatusTip('Start a new game')

        saveGame = QAction('Save', self)
        saveGame.setShortcut('Ctrl+S')
        saveGame.triggered.connect(self.saveGameAction)
        saveGame.setStatusTip('Save current game')

        loadGame = QAction('Load', self)
        loadGame.setShortcut('Ctrl+D')
        loadGame.triggered.connect(self.loadGameAction)
        loadGame.setStatusTip('Load current game')

        statGame = QAction('Statistics', self)
        statGame.setShortcut('Ctrl+Z')
        statGame.triggered.connect(self.statGameAction)
        statGame.setStatusTip('View game statistics')

        exitGame = QAction('Quit', self)
        exitGame.setShortcut('Esc')
        exitGame.triggered.connect(self.close)
        exitGame.setStatusTip('Quit the game')

        # Menu Events - Difficulty
        newbieDiff = QAction('Newbie', self)
        newbieDiff.triggered.connect(self.newbieDiffAction)
        newbieDiff.setStatusTip('Field 9х9, 10 mines')

        amateurDiff = QAction('Amateur', self)
        amateurDiff.triggered.connect(self.amateurDiffAction)
        amateurDiff.setStatusTip('Field 16х16, 40 mines')

        profiDiff = QAction('Professional', self)
        profiDiff.triggered.connect(self.profiDiffAction)
        profiDiff.setStatusTip('Field 16х30, 99 mines')

        specialDiff = QAction('Special...', self)
        specialDiff.triggered.connect(self.specialDiffAction)
        specialDiff.setStatusTip('Of your choice')

        # Menu Events - Help
        helpHelp = QAction('Rules', self)
        helpHelp.triggered.connect(self.helpFunc)
        helpHelp.setStatusTip('Help')

        aboutHelp = QAction('About the program', self)
        aboutHelp.triggered.connect(self.aboutFunc)
        aboutHelp.setStatusTip('About the program')

        # Menu - Game
        self.menubar = self.menuBar()

        self.gameMenu = self.menubar.addMenu('Game')
        self.gameMenu.addAction(newGame)
        self.gameMenu.addAction(saveGame)
        self.gameMenu.addAction(loadGame)
        self.gameMenu.addAction(statGame)
        self.gameMenu.addAction(exitGame)

        # Menu - Difficulty
        self.diffMenu = self.menubar.addMenu('Difficulty')
        self.diffMenu.addAction(newbieDiff)
        self.diffMenu.addAction(amateurDiff)
        self.diffMenu.addAction(profiDiff)
        self.diffMenu.addAction(specialDiff)

        # Menu - Help
        self.helpMenu = self.menubar.addMenu('Help')
        self.helpMenu.addAction(helpHelp)
        self.helpMenu.addAction(aboutHelp)

    # New game
    def newGameAction(self):
        text ='All gameplay will be reset without saving. Continue?'
        if self.num_moves > 0 and not self.loading or self.second > 0:
            self.timerFunc(stop=True)
            question = QMessageBox.question(self, 'Attention!', text,
                                            QMessageBox.Yes | QMessageBox.No,
                                            QMessageBox.No)
            if question == QMessageBox.Yes:
                # Zeroing the timer and the number of moves if "New game" is selected
                self.timerFunc(reset=True)
                self.createAll()
            else:
                self.timerFunc(pause=True)
        else:
            self.createAll()

    # Gambling field arrangement
    # Playing field tiles
    def gameArea(self):
        # List of game field buttons
        # to access the state of each button
        self.list_btns = []
        for x in range(self.height_area):
            row_btns = []
            for y in range(self.width_area):
                value = self.field[x][y]
                btn = Cell(x, y, value, self.smile_btn, self.timerFunc,
                           self.showMoves, self.checkBTN, self.usedFlag,
                           self.radar, self.changeValue, self)
                self.grid.addWidget(btn, x, y)
                row_btns.append(btn)
            self.list_btns.append(row_btns)

        # Window geometry
        if self.CH > 0:
            self.adjustSize()
        self.CH += 1

    # Change cell value
    def changeValue(self, value, x, y):
        self.field[x][y] = value

    # progress check
    def checkBTN(self, left, x=None, y=None):
        # left mouse button
        if left:
            self.showMoves()
            # mine?
            if self.field[x][y] == 19:
                self.win = False
                self.gameOver()
            elif self.field[x][y] == 10:
                # List of cells around the pressed button
                self.open_lst = []
                self.openBTN(x, y)
                # Opening empty cells
                for k in self.open_lst:
                    k.is_open = True
                    k.update()
        # right mouse button
        else:
            flag_on_mine = 0
            for i in range(self.height_area):
                for j in range(self.width_area):
                    if self.field[i][j] == 29:
                        flag_on_mine += 1
            # If all the flags on all mines - victory!
            if flag_on_mine == self.num_mines:
                self.win = True
                self.gameOver()

    # Count remaining flags
    def usedFlag(self):
        flag = 0
        for row in self.field:
            for value in row:
                if 19 < value < 30:
                    flag += 1

        if flag < self.num_mines:
            self.showMoves()
            return True
        else:
            return False

    # Game End Check
    def gameOver(self):
        self.game_over = True
        # Win or lose to record statistics
        if self.win:
            winner = 'victory'
        else:
            winner = 'losing'

        # Saving game results
        size = str(self.height_area) + 'x' + str(self.width_area)
        saveResult(size, str(self.num_mines), str(self.num_moves), str(self.second), winner)

        self.timerFunc(stop=True)
        # The result of the dialogue - the end of the game - New game or exit
        self.new_exit = False
        dialog = Over(self)
        dialog.exec_()
        # Processing the result of the dialog "End of the game"
        if self.new_exit:
            # Selected option - new game
            self.timerFunc(reset=True)
            self.newGameAction()
        else:
            # Closing the main program window, ending the game
            self.close()

    # Recursive search for empty cells
    def openBTN(self, x, y):
        if self.field[x][y] == 10 or self.field[x][y] == 0:
            for i in range(x - 1, x + 2):
                for j in range(y - 1, y + 2):
                    if 0 <= i < self.height_area and 0 <= j < self.width_area and self.field[i][j] < 9:
                        if self.list_btns[i][j] not in self.open_lst:
                            self.open_lst.append(self.list_btns[i][j])
                            self.field[i][j] += 10
                            self.openBTN(i, j)

    # Method for calculating game time and resetting parameters
    def timerFunc(self, start=False, stop=False, pause=False, reset=False):
        if start and self.num_moves == 0:
            self.timer.start(1000)
        elif stop:
            self.timer.stop()
            stop = False
        elif pause:
            self.timer.start()
            pause = False
        elif reset:
            # Zeroing the number of moves
            self.num_moves = 0
            # Zeroing the number of flags on the field
            self.used_flag = 0

            # Setting the radar value if "new game"
            if self.second > 0 and not self.loading:
                if self.num_mines <= 10:
                    self.num_radar = 3
                elif 10 < self.num_mines <= 40:
                    self.num_radar = 10
                elif 40 < self.num_mines:
                    self.num_radar = 15

            # Timer reset
            self.second = 0
            # Reset reset
            reset = False

    # RADAR method - open (close) cells using RMB
    def radar(self, open, x=None, y=None):
        if self.num_radar > 0:
            if open:
                self.radar_btn = []
                for i in range(x - 1, x + 2):
                    for j in range(y - 1, y + 2):
                        if (0 <= i < self.height_area and
                                0 <= j < self.width_area and
                                not self.list_btns[i][j].is_open and
                                not self.list_btns[i][j].is_flag):
                            self.radar_btn.append(self.list_btns[i][j])
                            self.list_btns[i][j].is_open = True
                            self.list_btns[i][j].update()
            else:
                for btn in self.radar_btn:
                    btn.is_open = False
                    btn.update()
                self.num_radar -= 1

    # Counting and displaying the number of moves
    def showMoves(self):
        self.num_moves += 1
        self.lcd_left.display(self.num_moves)

    # Game time display
    def second_on_LSD(self):
        self.second += 1
        self.lcd_right.display(self.second)

    def helpFunc(self):
        file = open('images/rules.txt')
        text = file.read()
        QMessageBox.information(self, 'Reference', text)

    def aboutFunc(self):
        QMessageBox.about(self, 'About programm', 'closed beta-vertion')

    # Save game method
    def saveGameAction(self):
        self.saveGameAction = Save(self.second, self.num_moves, self.num_radar, self.width_area, self.field, self)

    # Saved Game Load Method
    def loadGameAction(self):
        self.timerFunc(stop=True)
        dialog = Load(self)
        dialog.exec_()
        if self.loading:
            self.newGameAction()
        else:
            self.timerFunc(pause=True)

    # View game statistics
    def statGameAction(self):
        self.timerFunc(stop=True)
        dialog = Stat(self)
        dialog.exec_()
        self.timerFunc(pause=True)

    def newbieDiffAction(self):
        self.height_area = 9
        self.width_area = 9
        self.num_mines = 10
        self.num_radar = 3

        self.newGameAction()

    def amateurDiffAction(self):
        self.height_area = 16
        self.width_area = 16
        self.num_mines = 40
        self.num_radar = 10

        self.newGameAction()

    def profiDiffAction(self):
        self.height_area = 16
        self.width_area = 30
        self.num_mines = 99
        self.num_radar = 15

        self.newGameAction()

    # Calling up a menu item - Special parameters
    def specialDiffAction(self):
        # Stopping the timer during the dialogue with the user
        self.change = False
        self.timerFunc(stop=True)

        # Calling the window for changing the parameters and passing to its data class
        dialog = Size(self.height_area, self.width_area, self.num_mines, self)
        dialog.exec_()

        # If the user changed the game settings
        if self.change:
            self.newGameAction()
        else:
            self.timerFunc(pause=True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    main.setWindowTitle('Miner')
    main.setWindowIcon(QIcon('images/logo.png'))
    # Prevent resizing of the main window
    main.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
    desk = QApplication.desktop()
    window = main.geometry()
    x = (desk.width() - window.width()) // 2
    y = (desk.height() - window.height()) // 2
    main.move(x, y)
    main.show()
    sys.exit(app.exec_())