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

def mushUnEscape(str):
	retStr = ""
	x = 0
	while x != len(str):
		if str[x] == "%":
			x = x + 1
			if str[x] == "%":
				retStr = retStr + "%"
			elif str[x] == "r":
				retStr = retStr + "\n"
			else:
				retStr = retStr + str[x]
		else:
			retStr = retStr + str[x]
		x = x + 1
	return retStr

def mushEscape(str):
	retStr = ""
	x = 0
	while x != len(str):
		if str[x] == "%":
			retStr = retStr + "%%"
		elif str[x] == "\n":
			retStr = retStr + "%r"
		else:
			retStr = retStr + str[x]
		x = x + 1
	return retStr

def findNewId(lst):
	returnId = 0
	check = 1
	while check:
		for x in lst:
			if x.id == returnId:
				returnId = returnId + 1
				check = 1
			else:
				check = 0
		if not lst:
			check = 0
	return returnId

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
		self.alias = []
		self.returnAlias = []
		self.desc = ""
		self.returnDesc = ""
		self.source = source
		self.dest = -1
		self.line = QGraphicsLineItem()

class Label:
	type='label'
	def __init__(self, text, x_, y_):
		self.box = labelBox()
		self.x = x_
		self.y = y_
		self.normalText = text
		self.text = QGraphicsTextItem()
		self.text.setHtml("<p>" + self.normalText + "</p>")
		self.text.setPos(x_ - (self.text.boundingRect().width() / 2), y_ - (self.text.boundingRect().height() / 2))
		self.box.setPos(x_ - (self.text.boundingRect().width() / 2), y_ - (self.text.boundingRect().height() / 2))
		self.box.setBrush(QColor("#FFF7A9"))
		self.box.setRect(0, 0, self.text.boundingRect().width(), self.text.boundingRect().height())
	def setText(self, text_):
		self.normalText = text_
		self.text.setHtml("<p>" + self.normalText + "</p>")

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
				strExport = strExport + "@desc here=" + mushEscape(str(k.desc)) + "\n"
			strExport = strExport + "@set me=room_id" + str(k.id) + ":[loc(me)]" + "\n"
		for k in exitList:
			strExport = strExport + "@tel [v(room_id" + str(k.source) + ")]" + "\n"
			if k.twoWay == False:
				aliasString = ""
				for x in k.alias:
					aliasString = aliasString + ";" + x
				strExport = strExport + "@open " + k.name + aliasString + "\n"
				if k.desc != "":
					strExport = strExport + "@desc " + k.name + "=" + mushEscape(str(k.desc)) + "\n"
				if k.dest != -1:
					strExport = strExport + "@link " + k.name + "=" + "[v(room_id" + str(k.dest) + ")]" + "\n"
			else: # Two way exit
				aliasString = ""
				for x in k.alias:
					aliasString = aliasString + ";" + x
				returnAliasString = ""
				for x in k.returnAlias:
					returnAliasString = returnAliasString + ";" + x
				strExport = strExport + "@open " + k.name + aliasString + "=" + "[v(room_id" + str(k.dest) + ")], " + k.returnName + returnAliasString + "\n"
				if k.desc != "":
					strExport = strExport + "@desc " + k.name + "=" + mushEscape(str(k.desc)) + "\n"
				if k.returnDesc != "":
					strExport = strExport + k.name + "\n@desc " + k.returnName + "=" + k.returnDesc + "\n"
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
		self.btn1.clicked.connect(self.accept)

class editRoom(QDialog):
	def __init__(self, parent = None):
		super(editRoom, self).__init__(parent)
		self.setWindowTitle("Edit Room Properties")
		self.tabName = QWidget()
		self.tabDesc = QWidget()
		self.tab = QTabWidget()
		self.btn1 = QPushButton("Ok")
		self.btn1.clicked.connect(self.accept)
		self.tab.addTab(self.tabName, "Name")
		self.tab.addTab(self.tabDesc, "Description")

		tabLayout = QFormLayout()
		tabLayout.addRow(self.tab)
		tabLayout.addRow(self.btn1)
		self.setLayout(tabLayout)

		layout = QFormLayout()
		self.cur_room = 0
		self.lbl = QLabel("Name")
		self.le = QLineEdit()
		self.lbl2 = QLabel("Position")
		self.le2 = QLineEdit()
		self.le3 = QLineEdit()
		layout.addRow(self.lbl,self.le)
		layout.addRow(self.lbl2)
		layout.addRow(self.le2, self.le3)
		self.tabName.setLayout(layout)

		layout2 = QFormLayout()
		self.lblDesc = QLabel("Description")
		self.te = QTextEdit()
		layout2.addRow(self.lblDesc)
		layout2.addRow(self.te)
		self.tabDesc.setLayout(layout2)

	def setData(self, room):
		self.le.setText(roomList[room].name)
		self.te.setPlainText(roomList[room].desc)
		self.le2.setText(str(int(roomList[room].x)))
		self.le3.setText(str(int(roomList[room].y)))

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


class aliasList(QListWidget):
	def __init__(self, parent = None):
		super(aliasList, self).__init__(parent)
		self.resize(300,120)
		pass
	def contextMenuEvent(self, event):
		menu = QMenu()
		items = self.selectedItems()
		actionAddAlias = menu.addAction("Add Alias")
		if len(items) > 0:
			actionDeleteAlias = menu.addAction("Delete")
			item = items[0].text()
		action = menu.exec_(event.globalPos())
		if action == actionAddAlias:
			alias, ok = QInputDialog.getText(self, "Add Alias", "Alias:")
			if ok:
				self.addItem(alias)
		elif len(items) > 0:
			if action == actionDeleteAlias:
				self.takeItem(self.currentRow())

class editExit(QDialog):
	def __init__(self, parent = None):
		super(editExit, self).__init__(parent)
		self.rDict = {}
		self.setWindowTitle("Edit Exit Properties")

		self.tabNames = QWidget()
		self.tabAlias = QWidget()
		self.tabDesc = QWidget()
		self.btn1 = QPushButton("Ok")
		self.btn1.clicked.connect(self.accept)
		self.tab = QTabWidget()
		self.tab.addTab(self.tabNames, "Name")
		self.tab.addTab(self.tabDesc, "Description")
		self.tab.addTab(self.tabAlias, "Alias")

		tabLayout = QFormLayout()
		tabLayout.addRow(self.tab)
		tabLayout.addRow(self.btn1)
		self.setLayout(tabLayout)

		layout = QFormLayout()
		self.lbl = QLabel("Name")
		self.le = QLineEdit()
		self.lbl2 = QLabel("Return name")
		self.le2 = QLineEdit()
		self.checkBox = QRadioButton(self)
		self.boxLbl = QLabel("Two way exit")
		self.lbl3 = QLabel("Source")
		self.combo3 = QComboBox()
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
		self.tabNames.setLayout(layout)

		layout2 = QFormLayout()
		self.list1 = aliasList()
		self.list2 = aliasList()
		self.lblList1 = QLabel("Source exit")
		self.lblList2 = QLabel("Destination exit")
		layout2.addRow(self.lblList1, self.lblList2)
		layout2.addRow(self.list1, self.list2)
		self.tabAlias.setLayout(layout2)

		layout3 = QFormLayout()
		self.te1 = QTextEdit()
		self.te2 = QTextEdit()
		self.lblDesc1 = QLabel("Source description")
		self.lblDesc2 = QLabel("Destination description")
		layout3.addRow(self.lblDesc1, self.lblDesc2)
		layout3.addRow(self.te1, self.te2)
		self.tabDesc.setLayout(layout3)

		self.connect(self.btn1, SIGNAL("clicked()"), self, SLOT("accept()"))
		self.checkBox.toggled.connect(self.ButtonHide)
		self.checkBox.toggle()
	def ButtonHide(self, state):
		if self.checkBox.isChecked():
			self.le2.setEnabled(True)
			self.list2.setEnabled(True)
			self.te2.setEnabled(True)
		else:
			self.le2.setEnabled(False)
			self.list2.setEnabled(False)
			self.te2.setEnabled(False)
	def setData(self):
		global exitList
		self.combo4.addItem("#-1: No destination")
		self.rDict["#-1: No destination"] = -1
		for i in roomList:
			self.rDict[str("#" + str(i.id) + ": " + i.name)] = i.id
			self.combo3.addItem("#" + str(i.id) + ": " + i.name)
			self.combo4.addItem("#" + str(i.id) + ": " + i.name)
	def fillData(self, exit):
		self.le.setText(exitList[exit].name)
		self.combo3.setCurrentIndex(self.combo3.findText("#" + str(exitList[exit].source) + ": " + roomList[exitList[exit].source].name))
		self.combo4.setCurrentIndex(self.combo4.findText("#" + str(exitList[exit].dest) + ": " + roomList[exitList[exit].dest].name))
		self.te1.setPlainText(exitList[exit].desc)
		self.te2.setPlainText(exitList[exit].returnDesc)
		if exitList[exit].twoWay == False:
			self.checkBox.toggle()
			self.list2.setEnabled(False)
			self.le2.setEnabled(False)
			self.te2.setEnabled(False)
		else:
			self.le2.setText(exitList[exit].returnName)
		for x in exitList[exit].alias:
			self.list1.addItem(x)
		for x in exitList[exit].returnAlias:
			self.list2.addItem(x)
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
