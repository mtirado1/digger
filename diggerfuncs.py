import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *



#######################################
# Some constants

ROOM_SIZE = 31 # odd number
ROOM_CENTER = (ROOM_SIZE - 1) / 2
VIEW_X = 1080
VIEW_Y = 683
SCENE_X = 1080
SCENE_Y = 669


#######################################
# Global Lists and id references
roomList = []
exitList = []
labelList = []
global id_exit
id_room = 0
id_exit = 0
id_label = 0


def midPoint(x1, x2):
	return (x1 + x2) / 2

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

class labelBox(QGraphicsRectItem):
	def __init__(self, parent = None):
		super(labelBox, self).__init__(parent)
		self.setFlag(QGraphicsItem.ItemIsMovable, True)
		self.setFlag(QGraphicsItem.ItemIsSelectable, True)
		self.index = 0
		self.moved = 0
		self.move_restrict_rect = QRectF(0, 0, SCENE_X, SCENE_Y)

	def mouseReleaseEvent(self, event):
		if self.moved == 1:
			QGraphicsRectItem.mouseReleaseEvent(self, event)
			self.scene().parent().parent().drawAll()
		self.moved = 0

	def mouseMoveEvent(self, event):
		global roomList
		self.moved = 1
		labelList[self.index].x = self.scenePos().x()
		labelList[self.index].y = self.scenePos().y()

		if self.move_restrict_rect.contains(event.scenePos()):
			QGraphicsRectItem.mouseMoveEvent(self, event)


class roomBox(QGraphicsRectItem):
	def __init__(self, parent = None):
		super(roomBox, self).__init__(parent)
		self.setFlag(QGraphicsItem.ItemIsMovable, True)
		self.setFlag(QGraphicsItem.ItemIsSelectable, True)
		self.index = 0
		self.moved = 0
		self.move_restrict_rect = QRectF(0, 0, SCENE_X, SCENE_Y)
		#self.setRect(QRectF(0,0,1080,683))

	def mouseReleaseEvent(self, event):
		if self.moved == 1:
			QGraphicsRectItem.mouseReleaseEvent(self, event)
			self.scene().parent().parent().drawAll()
		self.moved = 0

	def mouseMoveEvent(self, event):
		global roomList
		self.moved = 1
		roomList[self.index].x = self.scenePos().x()
		roomList[self.index].y = self.scenePos().y()

		if self.move_restrict_rect.contains(event.scenePos()):
			QGraphicsRectItem.mouseMoveEvent(self, event)

class Room:
	def __init__(self, name, id_, parent):
		self.id = id_
		self.name = name
		self.desc = ""
		self.x = 0
		self.y = 0
		self.box = roomBox()
		self.text = QGraphicsTextItem()


class Exit:
	type='exit'
	def __init__(self, name, id_, source):
		self.id = id_
		self.twoWay = False
		self.name = name
		self.returnName = ""
		self.alias = ""
		self.desc = ""
		self.source = source
		self.dest = -1
		self.line = QGraphicsLineItem()

class Label:
	type='label'
	def __init__(self, text, x_, y_):
		self.box = labelBox()
		self.x = x_
		self.y = y_
		self.text = QGraphicsTextItem()
		self.text.setHtml("<p>" + text + "</p>")
		self.text.setPos(x_ - (self.text.boundingRect().width() / 2), y_ - (self.text.boundingRect().height() / 2))
		self.box.setPos(x_ - (self.text.boundingRect().width() / 2), y_ - (self.text.boundingRect().height() / 2))
		self.box.setBrush(QColor("#FFF7A9"))
		self.box.setRect(0, 0, self.text.boundingRect().width(), self.text.boundingRect().height())

class textDialog(QDialog):
	def __init__(self, title, text, parent = None):
		super(textDialog, self).__init__(parent)
		layout = QFormLayout()
		self.lbl = QLabel(text)
		layout.addRow(self.lbl)
		self.setLayout(layout)
		self.setWindowTitle(title)
		self.btn1 = QPushButton("Ok")
		layout.addRow(self.btn1)
		self.connect(self.btn1, SIGNAL("clicked()"), self, SLOT("accept()"))

class exportClass(QDialog):
	def __init__(self, parent = None):
		super(exportClass, self).__init__(parent)
		self.resize(500, 500)
		self.setWindowTitle("Export")
		self.browser = QTextBrowser(self)
		self.browser.setGeometry(QRect(0, 0, 500, 500))
	def exportAll(self):
		strExport = ""
		for k in roomList:
			strExport = strExport + "@dig/teleport " + k.name + "\n"
			if k.desc != "":
				strExport = strExport + "@desc here=" + k.desc + "\n"
			strExport = strExport + "@set me=room_id" + str(k.id) + ":[loc(me)]" + "\n"
		for k in exitList:
			strExport = strExport + "@tel [v(room_id" + str(k.source) + ")]" + "\n"
			if k.twoWay == False:
				strExport = strExport + "@open " + k.name + "\n"
				if k.dest != -1:
					strExport = strExport + "@link " + k.name + "=" + "[v(room_id" + str(k.dest) + ")]" + "\n"
			else: # Two way exit
				strExport = strExport + "@open " + k.name + "=" + "[v(room_id" + str(k.dest) + ")], " + k.returnName + "\n"
		for k in roomList:
			strExport = strExport + "&room_id" + str(k.id) + " me\n"
		self.browser.setText(strExport)

class optionsClass(QDialog):
	def __init__(self, parent=None):
		super(optionsClass, self).__init__(parent)
		layout = QFormLayout()
		self.setWindowTitle("Options")
		self.lbl = QLabel("Window Size")
		self.lbl2 = QLabel("Width")
		self.lbl3 = QLabel("Height")
		self.lbl4 = QLabel("Background Color")
		self.le = QLineEdit()
		self.le2 = QLineEdit()
		self.le3 = QLineEdit()
		self.btn1 = QPushButton("Ok")
		layout.addRow(self.lbl)
		layout.addRow(self.lbl2, self.lbl3)
		layout.addRow(self.le, self.le2)
		layout.addRow(self.lbl4)
		layout.addRow(self.le3)
		layout.addRow(self.btn1)
		self.setLayout(layout)
		self.connect(self.btn1, SIGNAL("clicked()"), self, SLOT("accept()"))
	def setData(self):
		self.le.setText(str(self.parent().ui.graphicsView.width()))
		self.le2.setText(str(self.parent().ui.graphicsView.height()))
		self.le3.setText(str(self.parent().bColor))


class newRoom(QDialog):
	def __init__(self, parent=None):
		super(newRoom, self).__init__(parent)
		layout = QFormLayout()
		self.lbl = QLabel("Name")
		self.le = QLineEdit()
		layout.addRow(self.lbl,self.le)
		self.setLayout(layout)
		self.setWindowTitle("New Room")
		self.btn1 = QPushButton("Ok")
		layout.addRow(self.btn1)
		self.connect(self.btn1, SIGNAL("clicked()"), self, SLOT("accept()"))

class editRoom(QDialog):
	def __init__(self, parent = None):
		super(editRoom, self).__init__(parent)
		layout = QFormLayout()
		self.cur_room = 0
		self.lbl = QLabel("Name")
		self.le = QLineEdit()
		layout.addRow(self.lbl,self.le)
		self.lbl2 = QLabel("Description")
		self.le2 = QLineEdit()
		layout.addRow(self.lbl2, self.le2)
		self.lbl3 = QLabel("Position")
		self.le3 = QLineEdit()
		self.le4 = QLineEdit()
		layout.addRow(self.lbl3)
		layout.addRow(self.le3, self.le4)
		self.setLayout(layout)
		self.setWindowTitle("Edit Room Properties")
		self.btn1 = QPushButton("Ok")
		layout.addRow(self.btn1)
		self.connect(self.btn1, SIGNAL("clicked()"), self, SLOT("accept()"))
	def setData(self, room):
		global boxList
		self.le.setText(roomList[room].name)
		self.le2.setText(roomList[room].desc)
		self.le3.setText(str(int(roomList[room].x)))
		self.le4.setText(str(int(roomList[room].y)))

class newExitName(QDialog):
	def __init__(self, parent = None):
		super(newExitName, self).__init__(parent)
		layout = QFormLayout()
		self.lbl = QLabel("Name")
		self.le = QLineEdit()
		self.lbl2 = QLabel("Return name")
		self.le2 = QLineEdit()
		self.checkBox = QRadioButton(self)
		self.boxLbl = QLabel("Two way exit")
		self.setWindowTitle("New Exit")
		self.btn1 = QPushButton("Ok")

		self.hbox = QHBoxLayout()
		self.hbox.addWidget(self.checkBox)
		self.hbox.addWidget(self.boxLbl)
		self.hbox.addStretch()

		layout.addRow(self.lbl,self.le)
		layout.addRow(self.lbl2, self.le2)
		layout.addRow(self.hbox)
		layout.addRow(self.btn1)
		self.setLayout(layout)
		self.connect(self.btn1, SIGNAL("clicked()"), self, SLOT("accept()"))

		self.checkBox.toggled.connect(self.ButtonHide)
		self.checkBox.toggle()
	def ButtonHide(self, state):
		if self.checkBox.isChecked():
			self.le2.setEnabled(True)
		else:
			self.le2.setEnabled(False)

class newExit(QDialog):
	def __init__(self, parent = None):
		super(newExit, self).__init__(parent)
		layout = QFormLayout()
		self.rDict = {}
		self.lbl = QLabel("Name")
		self.le = QLineEdit()
		self.lbl2 = QLabel("Return name")
		self.le2 = QLineEdit()
		self.checkBox = QRadioButton(self)
		self.boxLbl = QLabel("Two way exit")
		self.lbl3 = QLabel("Source")
		self.combo3 = QComboBox()
		self.setWindowTitle("New Exit")
		self.btn1 = QPushButton("Ok")
		self.lbl4 = QLabel("Destination")
		self.combo4 = QComboBox()
		self.hbox = QHBoxLayout()
		self.hbox.addWidget(self.checkBox)
		self.hbox.addWidget(self.boxLbl)
		self.hbox.addStretch()

		layout.addRow(self.lbl,self.le)
		layout.addRow(self.lbl2, self.le2)
		layout.addRow(self.hbox)
		layout.addRow(self.lbl3, self.combo3)
		layout.addRow(self.lbl4, self.combo4)
		self.setLayout(layout)

		self.connect(self.btn1, SIGNAL("clicked()"), self, SLOT("accept()"))
		self.checkBox.toggled.connect(self.ButtonHide)
		self.checkBox.toggle()
		layout.addRow(self.btn1)
	def ButtonHide(self, state):
		if self.checkBox.isChecked():
			self.le2.setEnabled(True)
		else:
			self.le2.setEnabled(False)
	def setData(self):
		global roomList
		self.combo4.addItem("#-1: No destination")
		self.rDict["#-1: No destination"] = -1
		for i in roomList:
			self.rDict["#" + str(i.id) + ": " + i.name] = i.id
			self.combo3.addItem("#" + str(i.id) + ": " + i.name)
			self.combo4.addItem("#" + str(i.id) + ": " + i.name)

class addLabel(QDialog):
	def __init__(self, parent = None):
		super(addLabel, self).__init__(parent)
		layout = QFormLayout()
		self.lbl = QLabel("Label")
		self.le = QLineEdit()
		self.setLayout(layout)
		self.setWindowTitle("Add Label")
		self.btn1 = QPushButton("Ok")
		layout.addRow(self.lbl, self.le)
		self.connect(self.btn1, SIGNAL("clicked()"), self, SLOT("accept()"))
		layout.addRow(self.btn1)
