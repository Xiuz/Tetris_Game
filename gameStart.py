# Date:2018.6.7
# Author: Zhuxi
# version: 1.0
# copyrights reserved
# refered: http://zetcode.com/gui/pyqt5/

from PyQt5.QtWidgets import QApplication,QMainWindow,QDesktopWidget,QLabel,QPushButton
from PyQt5.QtCore import pyqtSignal,QBasicTimer,Qt
from PyQt5.QtGui import QPainter,QColor
from Dialogue import LogDialogue
import sqlite3
import sys,random,os

class Game(QMainWindow):

    msg2labelStatus = pyqtSignal(str)
    msg2labelScore = pyqtSignal(str)

    def __init__(self):
        super(Game,self).__init__()
        self.total_width = 600
        self.total_height = 600

        self.game_width = 228
        self.game_height = 450
        self.game_top_left = [60, (self.total_height - self.game_height) / 4]

        self.score_width = 160
        self.score_height = self.game_height / 2
        self.score_top_left = [self.game_top_left[0]+self.game_width+60, self.game_top_left[1]]

        self.predict_width = self.score_width
        self.predict_height = self.game_height - self.score_height - 40
        self.predict_top_left = [self.score_top_left[0], self.score_top_left[1] + self.score_height + 40]

        self.square_width_num = 12
        self.square_height_num = 25
        self.square_width = self.game_width/self.square_width_num
        self.square_height = self.game_height/self.square_height_num

        self.Speed = 300

        self.user = ''
        self.pwd = ''

        self.counter = 0
        self.shape = [random.randint(1,7) for i in range(1000)]

        self.setupUI()

        self.setupGame()

    def setupUI(self):
        """初始化游戏界面"""
        self.setWindowTitle("Tetris_for_my_girl")
        self.setFixedSize(self.total_width,self.total_height)
        self.center()

        self.label1 = QLabel("用户名：未登陆",self)
        self.label2 = QLabel("当前成绩：",self)
        self.label3 = QLabel("当前状态：正在游戏",self)
        self.label4 = QLabel("用户最好成绩：",self)
        self.label5 = QLabel("游戏最好成绩：",self)
        self.label1.setFixedSize(150, 20)
        self.label2.setFixedSize(150, 20)
        self.label3.setFixedSize(150, 20)
        self.label4.setFixedSize(150, 20)
        self.label5.setFixedSize(150, 20)

        self.label1.move(self.score_top_left[0]+20,self.score_top_left[1]+20)
        self.label2.move(self.score_top_left[0]+20, self.score_top_left[1]+60)
        self.label3.move(self.score_top_left[0]+20, self.score_top_left[1]+100)
        self.label4.move(self.score_top_left[0]+20, self.score_top_left[1]+140)
        self.label5.move(self.score_top_left[0]+20, self.score_top_left[1]+180)

        self.button1 = QPushButton("开始",self)
        self.button2 = QPushButton("结束",self)
        self.button3 = QPushButton("暂停", self)
        self.button4 = QPushButton("登陆",self)
        self.button1.move(50,520)
        self.button2.move(185,520)
        self.button3.move(318,520)
        self.button4.move(452,520)
        self.button1.clicked.connect(self.startGame)
        self.button2.clicked.connect(self.endGame)
        self.button3.clicked.connect(self.pauseGame)
        self.button4.clicked.connect(self.logIn)
        self.msg2labelStatus.connect(self.showStatus)
        self.msg2labelScore.connect(self.showScore)

    def setupGame(self):
        """开始主程序逻辑"""
        self.timer = QBasicTimer()
        self.isWaitingAfterLine = False
        self.numLinesRemoved = int(0)

        self.board = []

        self.setFocusProxy(self)
        self.isStarted = False
        self.isPaused = False
        self.clearBoard()
        self.initDatabase()
        self.start()
        self.showMaxScore()

    def center(self):
        # 将界面放置在屏幕中央
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2,(screen.height()-size.height())/2-30)

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

    def startGame(self):

        self.isStarted = True
        self.isPaused = False
        self.msg2labelStatus.emit("正在游戏")
        self.clearScreen()
        self.start()
        self.showMaxScore()

    def endGame(self):
        if self.isStarted == False:
            return None
        self.isStarted = False
        self.msg2labelStatus.emit("游戏结束")
        if self.user is not '':
            self.updateScore(self.user,self.numLinesRemoved)
        self.showUserMaxScore(self.user)
        self.clearScreen()
        self.numLinesRemoved = 0
        self.msg2labelScore.emit(str(self.numLinesRemoved))
        self.timer.stop()
        self.update()

    def pauseGame(self):
        self.pause()

    def logIn(self):
        self.pause()
        dialogue = LogDialogue(self)
        dialogue.login_success_signal.connect(self.showLogIn)
        dialogue.show()
        pass

    def showLogIn(self,user,pwd):
        self.user = user
        self.pwd = pwd
        self.label1.setText('用户名：%s' % self.user)
        self.showUserMaxScore(user)
        pass

    def showStatus(self,txt):
        self.label3.setText("当前状态："+ txt)

    def showScore(self,i):
        self.label2.setText("当前分数："+ str(i))

    def showMaxScore(self):
        conn = sqlite3.connect('user_data.db3')
        cur = conn.cursor()
        cur.execute('SELECT SCORE FROM USER')
        self.label5.setText('游戏最好成绩：%d'% max(list(cur.fetchall()))[0])
        conn.close()

    def showUserMaxScore(self,user):
        conn = sqlite3.connect('user_data.db3')
        cur = conn.cursor()
        cur.execute("SELECT SCORE FROM USER WHERE NAME=='{user}'".format(user=user))
        self.label4.setText('用户最好成绩：%d' % cur.fetchall()[0][0])
        conn.close()

    def updateScore(self,user,score):
        conn = sqlite3.connect('user_data.db3')
        conn.execute("UPDATE USER SET SCORE={score} where NAME=='{user}'".format(score=score, user=user))
        conn.commit()
        conn.close()

    def shapeAt(self,x,y):
        return self.board[y * self.square_width_num + x]

    def setShapeAt(self,x,y,shape):
        self.board[y * self.square_width_num + x] = shape

    def start(self):

        if self.isPaused:
            return

        self.isStarted = True
        self.isWaitingAfterLine = False
        self.numLinesRemoved =0
        self.clearBoard()
        self.msg2labelScore.emit(str(self.numLinesRemoved))
        self.newPiece()
        self.timer.start(self.Speed,self)

    def pause(self):

        if not self.isStarted:
            return

        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.button3.setText("继续")
            self.msg2labelStatus.emit("已暂停")

        else:
            self.timer.start(self.Speed,self)
            self.button3.setText("暂停")
            self.msg2labelStatus.emit("已开始")

        self.update()

    def clearScreen(self):
        for k in range(self.square_height_num):
            for l in range(self.square_width_num):
                self.setShapeAt(l, k, Tetrominoe.NoShape)

    def initData(self):
        con = sqlite3.connect(r'F:\Tetris\gameDatabase.db3')
        cur = con.cursor()
        cur.execute('CREATE TABLE game (username VARCHAR(20),password VARCHAR(30),score INTEGER)')
        pass

    def saveData(self):
        con = sqlite3.connect(r'F:\Tetris\gameDatabase.db3')
        cur = con.cursor()
        pass

    def readData(self):
        pass

    def timerEvent(self, event):
        """在计时器事件里，要么是等一个方块下落完之后创建一个新的方块，要么是让一个方块直接落到底"""
        if event.timerId() == self.timer.timerId():
            if self.isWaitingAfterLine:
                self.isWaitingAfterLine = False
                self.newPiece()
            else:
                self.oneLineDown()
        else:
            super(Game,self).timerEvent(event)

    def keyPressEvent(self, event):
        '''processes key press events'''

        if not (self.isStarted or self.curPiece.shape() == Tetrominoe.NoShape):
            super(Game, self).keyPressEvent(event)
            return

        key = event.key()

        if key == Qt.Key_P:
            self.pause()
            return

        if self.isPaused:
            return

        elif key == Qt.Key_J:
            self.tryMove(self.curPiece, self.curX - 1, self.curY)

        elif key == Qt.Key_L:
            self.tryMove(self.curPiece, self.curX + 1, self.curY)

        elif key == Qt.Key_I:
            self.tryMove(self.curPiece.rotateRight(), self.curX, self.curY)

        elif key == Qt.Key_K:
            self.tryMove(self.curPiece.rotateLeft(), self.curX, self.curY)

        elif key == Qt.Key_M:
            self.dropDown()

        elif key == Qt.Key_N:
            self.oneLineDown()

        else:
            super(Game, self).keyPressEvent(event)

    def clearBoard(self):
        for i in range(self.square_width_num * self.square_height_num):
            self.board.append(Tetrominoe.NoShape)

    def dropDown(self):
        """降到不能降为止"""
        newY = self.curY

        while newY > 0:
            # newY为0的时候结束，可为什么是为0的时候结束呢？不应该是21到底部结束吗？
            if not self.tryMove(self.curPiece, self.curX, newY - 1):
                break

            newY -= 1

        self.pieceDropped()

    def oneLineDown(self):
        """调用tryMove一次，就往下滑一次，如果返回False，就说明到底了，将这个方块添加到board列表中去，存储为已有方块"""
        if not self.tryMove(self.curPiece,self.curX,self.curY-1):
            self.pieceDropped()
            pass

    def pieceDropped(self):

        for i in range(4):
            x = self.curX + self.curPiece.x(i)
            y = self.curY - self.curPiece.y(i)
            self.setShapeAt(x, y, self.curPiece.shape())

        self.removeFullLines()

        if not self.isWaitingAfterLine:
            self.newPiece()

    def removeFullLines(self):
        '''removes all full lines from the board'''

        numFullLines = 0
        rowsToRemove = []

        for i in range(self.square_height_num):

            n = 0
            for j in range(self.square_width_num):
                if not self.shapeAt(j, i) == Tetrominoe.NoShape:
                    n = n + 1

            if n == self.square_width_num:
                # 如果10路的形状小方块都不是空，那么说明都已经填满了
                rowsToRemove.append(i)

        rowsToRemove.reverse()
        # 将rowsToRemove列表反转，从大行数开始搜索，因为纵坐标在上面，最大行代表最下面游戏的第一行

        for m in rowsToRemove:

            for k in range(m, self.square_height_num):
                for l in range(self.square_width_num):
                    self.setShapeAt(l, k, self.shapeAt(l, k + 1))
                    # 确定行列坐标，将上一行的数据整体下移一行

        numFullLines = numFullLines + len(rowsToRemove)

        if numFullLines > 0:
            self.numLinesRemoved = self.numLinesRemoved + (numFullLines * 2 - 1)
            self.msg2labelScore.emit(str(self.numLinesRemoved))

            self.isWaitingAfterLine = True
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.update()   # 这个应该是针对定时器的更新，以减少消除行所需要的时间

    def tryMove(self, newPiece, newX, newY):
        '''tries to move a shape'''

        for i in range(4):

            x = newX + newPiece.x(i)
            y = newY - newPiece.y(i)
            # 这里选择左上角为出发点，所以确定方块纵坐标用的是减法,这样我们得到了四个小方块的横纵坐标
            if x < 0 or x >= self.square_width_num or y < 0 or y >= self.square_height_num:
                return False  # 虽然这里用了return False，但是实际上x和y的坐标不可能出现上述情况，因此这里不可能返回false，false只有在触碰到其他方块的时候才会出现
            # 注意如果这里不是空形状就说明已经有形状填充在这里了，那么函数运行到此处就结束返回了
            if self.shapeAt(x, y) != Tetrominoe.NoShape:
                return False

        self.curPiece = newPiece
        self.curX = newX
        self.curY = newY
        self.update()

        return True

    def newPiece(self):
        '''creates a new shape'''

        self.curPiece = Shape()
        self.curPiece.setShape(self.shape[self.counter])
        self.counter += 1
        self.curX = self.square_width_num // 2 + 1
        self.curY = self.square_height_num - 1 + self.curPiece.minY()

        if not self.tryMove(self.curPiece, self.curX, self.curY):
            # 当刚产生的方块触碰到其他方块的时候，说明已产生的方块已经到顶了，游戏结束
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.timer.stop()
            self.isStarted = False
            self.msg2labelStatus.emit("游戏结束")

    def paintEvent(self, event):
        curPiece = Shape()
        curPiece.setShape(self.shape[self.counter])
        pre_x = self.predict_width/self.square_width//2
        pre_y = self.predict_height/self.square_height//2
        qp = QPainter(self)


        for i in range(4):
            x = pre_x + curPiece.x(i)
            y = pre_y - curPiece.y(i)
            self.draw(qp, self.predict_top_left[0] + x * self.square_width,
                             20+(self.square_height_num - y - 1) * self.square_height,
                            curPiece.shape())

        if self.curPiece.shape() != Tetrominoe.NoShape:

            for i in range(4):
                x = self.curX + self.curPiece.x(i)
                y = self.curY - self.curPiece.y(i)
                self.draw(qp, self.game_top_left[0] + x * self.square_width,
                          self.game_top_left[1] + (self.square_height_num - y - 1) * self.square_height,
                                self.curPiece.shape())
            # 注意这里curX和curY是当前的正在移动的小方块的锚点坐标，并非像素点的绝对坐标,x和y分别代表四个小方块的横纵坐标，乘上squareWidth和squareHeight就是像素点绝对坐标了


        for i in range(self.square_height_num):
            for j in range(self.square_width_num):
                shape = self.shapeAt(j, self.square_height_num - i - 1)

                if shape != Tetrominoe.NoShape:
                    self.draw(qp, self.game_top_left[0] + j * self.square_width,
                                    self.game_top_left[1] + i * self.square_height, shape)
        # 以上这部分是用来画下面已经有了的内容,注意画的时候是一个小方块一个小方块的画，并不是四个一起的


    def draw(self, painter,x,y,shape):

        painter.drawRect(self.game_top_left[0],self.game_top_left[1],self.game_width,self.game_height)
        painter.drawRect(self.score_top_left[0],self.score_top_left[1],self.score_width,self.score_height)
        painter.drawRect(self.predict_top_left[0],self.predict_top_left[1],self.predict_width,self.predict_height)
        # for i in range(self.square_height_num):
        #     for j in range(self.square_width_num):
        #         painter.drawRect(self.game_top_left[0] + j * self.square_width, self.game_top_left[1] + i * self.square_height,self.square_width,self.square_height)
        # 加个网格看得清

        colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                      0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

        color = QColor(colorTable[shape])
        painter.fillRect(x + 1, y + 1, self.square_width - 2,
                         self.square_height - 2, color)
        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.square_height - 1, x, y)
        painter.drawLine(x, y, x + self.square_width - 1, y)

        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.square_height - 1,
                         x + self.square_width - 1, y + self.square_height - 1)
        painter.drawLine(x + self.square_width - 1,
                         y + self.square_height - 1, x + self.square_width - 1, y + 1)

class Tetrominoe(object):

    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7

class Shape(object):
    coordsTable = (
        ((0, 0), (0, 0), (0, 0), (0, 0)),
        ((0, -1), (0, 0), (-1, 0), (-1, 1)),
        ((0, -1), (0, 0), (1, 0), (1, 1)),
        ((0, -1), (0, 0), (0, 1), (0, 2)),
        ((-1, 0), (0, 0), (1, 0), (0, 1)),
        ((0, 0), (1, 0), (0, 1), (1, 1)),
        ((-1, -1), (0, -1), (0, 0), (0, 1)),
        ((1, -1), (0, -1), (0, 0), (0, 1))
    )

    def __init__(self):

        self.coords = [[0, 0] for i in range(4)]
        self.pieceShape = Tetrominoe.NoShape

        self.setShape(Tetrominoe.NoShape)

    def shape(self):
        '''returns shape'''

        return self.pieceShape

    def setShape(self, shape):
        '''sets a shape'''

        table = Shape.coordsTable[shape]

        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self.pieceShape = shape

    def setRandomShape(self):
        '''chooses a random shape'''

        self.setShape(random.randint(1, 7))

    def x(self, index):
        '''returns x coordinate'''

        return self.coords[index][0]

    def y(self, index):
        '''returns y coordinate'''

        return self.coords[index][1]

    def setX(self, index, x):
        '''sets x coordinate'''

        self.coords[index][0] = x

    def setY(self, index, y):
        '''sets y coordinate'''

        self.coords[index][1] = y

    def minX(self):
        '''returns min x value'''

        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])

        return m

    def maxX(self):
        '''returns max x value'''

        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][0])

        return m

    def minY(self):
        '''returns min y value'''

        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])

        return m

    def maxY(self):
        '''returns max y value'''

        m = self.coords[0][1]
        for i in range(4):
            m = max(m, self.coords[i][1])

        return m

    def rotateLeft(self):
        '''rotates shape to the left'''

        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):
            result.setX(i, self.y(i))
            result.setY(i, -self.x(i))

        return result

    def rotateRight(self):
        '''rotates shape to the right'''

        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):
            result.setX(i, -self.y(i))
            result.setY(i, self.x(i))

        return result

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = Game()
    game.show()
    sys.exit(app.exec_())
