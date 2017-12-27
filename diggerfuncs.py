import os
import sys
from mush import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import xml.dom.minidom
from xml.dom.minidom import parse
import json


#######################################
# Global Dictionaries
roomList = {}
exitList = {}
labelList = {}


def findNewId(dict):
	returnId = 0
	check = 1
	while check:
		for x in dict:
			if x == returnId:
				returnId = returnId + 1
				check = 1
			else:
				check = 0
		if not dict:
			check = 0
	return returnId

class labelBox(QGraphicsRectItem):
	def __init__(self, parent = None):
		super(labelBox, self).__init__(parent)
		self.setFlag(QGraphicsItem.ItemIsMovable, True)
		self.setFlag(QGraphicsItem.ItemIsSelectable, True)
		self.index = 0
		self.moved = 0

	def mouseReleaseEvent(self, event):
		if self.moved == 1:
			QGraphicsRectItem.mouseReleaseEvent(self, event)
			self.scene().parent().parent().parent().drawLabel(self.index)
		self.moved = 0

	def mouseMoveEvent(self, event):
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

	def mouseReleaseEvent(self, event):
		if self.moved == 1:
			QGraphicsRectItem.mouseReleaseEvent(self, event)
			self.scene().parent().parent().parent().drawRoom(self.index)
		self.moved = 0

	def mouseMoveEvent(self, event):
		self.moved = 1
		roomList[self.index].x = self.scenePos().x()
		roomList[self.index].y = self.scenePos().y()

		if self.move_restrict_rect.contains(event.scenePos()):
			QGraphicsRectItem.mouseMoveEvent(self, event)

class Map:
	def __init__(self):
		self.width = diggerconf.mapWidth
		self.height = diggerconf.mapHeight
		self.bcolor = diggerconf.mapColor
		self.rooms = {}
		self.exits = {}
		self.labels = {}

class Room:
	def __init__(self, name, id, parent):
		self.name = name
		self.desc = ""
		self.bColor = ""
		self.x = 0
		self.y = 0
		self.size = diggerconf.roomSize # Get room size from config file
		self.center = diggerconf.roomCenter # Also room center
		self.box = roomBox()
		self.box.index = id
		self.text = QGraphicsTextItem()
		self.code = [] # List of lines of code to be executed in room

class Exit:
	type='exit'
	def __init__(self, name, source):
		self.name = name
		self.alias = ""
		self.desc = ""
		self.source = source
		self.dest = -1
		self.line = QGraphicsLineItem()
		self.verbs = {}
		if str(name) in diggerconf.aliasDict:
			self.name = diggerconf.aliasDict[str(name)][0]
			for x in range(len(diggerconf.aliasDict[str(name)])):
				if x != 0:
					self.alias += diggerconf.aliasDict[str(name)][x] + ";"
			self.alias = self.alias[:-1]

class Label:
	type='label'
	def __init__(self, text, id, x_, y_):
		self.box = labelBox()
		self.x = x_
		self.y = y_
		self.normalText = text
		self.text = QGraphicsTextItem()
		self.text.setHtml("<p>" + self.normalText + "</p>")
		self.text.setPos(x_ - (self.text.boundingRect().width() / 2), y_ - (self.text.boundingRect().height() / 2))
		self.box.index = id
		self.box.setPos(x_ - (self.text.boundingRect().width() / 2), y_ - (self.text.boundingRect().height() / 2))
		self.box.setBrush(QColor("#FFF7A9"))
		self.box.setRect(0, 0, self.text.boundingRect().width(), self.text.boundingRect().height())
	def setText(self, text_):
		self.normalText = text_
		self.text.setHtml("<p>" + self.normalText + "</p>")


def exportCodeToFile(title):
	fname = QFileDialog.getSaveFileName(None, 'Export to File', '/', "")[0]
	fsave = QFile(fname)
	if not fsave.open(QIODevice.WriteOnly):
		raise IOError(unicode(fsave.errorString()))
	stream = QTextStream(fsave)
	stream.setCodec("UTF-8")
	stream << generateCode(title, roomList, exitList, labelList)

def importJson(self, fname):
	with open(fname) as f:
		data = json.load(f)
		map = data["map"]
		retMap = Map()
		retMap.width = map["width"]
		retMap.height = map["height"]
		retMap.bcolor = map["bcolor"]
		rooms = map["rooms"]
		exits = map["exits"]
		labels = map["labels"]
		for r in rooms:
			id = r["id"]
			retMap.rooms[id] = Room(r["name"], id, self)
			retMap.rooms[id].x = r["x"]
			retMap.rooms[id].y = r["y"]
			retMap.rooms[id].desc = r["description"]
			retMap.rooms[id].bColor = r["bcolor"]
			retMap.rooms[id].center = r["size"]
			retMap.rooms[id].size = r["size"] * 2 + 1
			retMap.rooms[id].code = r["code"]
		for e in exits:
			id = e["id"]
			retMap.exits[id] = Exit(e['name'], e['source'])
			retMap.exits[id].dest = e['destination']
			retMap.exits[id].desc = e['description']
			retMap.exits[id].alias = e['alias']
			retmap.exits[id].verbs = e['verbs']
		for l in labels:
			id = findNewId(retMap.labels)
			retMap.labels[id] = Label(l["text"], l["x"], l["y"])
		return retMap

def importXml(self, fname):

	def getText(element):
		if element.childNodes:
			return element.childNodes[0].data
		return "" # Empty tag

	retMap = Map()
	DOMTree = xml.dom.minidom.parse(str(fname))
	root = DOMTree.documentElement
	if root.tagName != "DIGGER":
		raise ValueError("not a Digger XML file.")
		return 1
	element = root.getElementsByTagName("map")[0]
	retMap.width =  int(element.getAttribute("width"))
	retMap.height = int(element.getAttribute("height"))
	retMap.bcolor = element.getAttribute("bcolor")
	rooms = element.getElementsByTagName("room")
	exits = element.getElementsByTagName("exit")
	labels = element.getElementsByTagName("label")
	for element in rooms:
		id = int(element.getAttribute("id"))
		load_room_x = int(element.getAttribute("x"))
		load_room_y = int(element.getAttribute("y"))
		load_room_bcolor = element.getAttribute("bcolor")
		load_room_center = int(element.getAttribute("size"))
		load_room_desc = ""
		load_room_code = []
		if element.getElementsByTagName("description"):
			load_room_desc = getText(element.getElementsByTagName("description")[0])
		for i in element.getElementsByTagName("code"):
			load_room_code.append(getText(i))
		retMap.rooms[id] = Room(getText(element.getElementsByTagName("name")[0]), id, self)
		retMap.rooms[id].desc = mushUnEscape(load_room_desc)
		retMap.rooms[id].x = load_room_x
		retMap.rooms[id].y = load_room_y
		retMap.rooms[id].bColor = load_room_bcolor
		retMap.rooms[id].center = load_room_center
		retMap.rooms[id].size = (load_room_center * 2) + 1
		retMap.rooms[id].code = load_room_code

	for element in exits:
		id = int(element.getAttribute("id"))
		load_exit_source = int(element.getAttribute("source"))
		load_exit_dest = int(element.getAttribute("destination"))
		load_exit_alias = []
		load_exit_name = getText(element.getElementsByTagName("name")[0])
		load_exit_desc = ""
		load_exit_msg = {}
		if element.getElementsByTagName("description"):
			load_exit_desc = getText(element.getElementsByTagName("description")[0])
		for i in element.getElementsByTagName("alias"):
			load_exit_alias.append(getText(i))

		msgElement = element.getElementsByTagName('verbs')
		if msgElement:
			for i in verbList:
				if msgElement[0].getElementsByTagName(i):
					message = getText(msgElement[0].getElementsByTagName(i)[0])
					load_exit_msg[i] = message

		retMap.exits[id] = Exit(load_exit_name, load_exit_source)
		retMap.exits[id].alias = ";".join(load_exit_alias)
		retMap.exits[id].dest = load_exit_dest
		retMap.exits[id].desc = mushUnEscape(load_exit_desc)
		retMap.exits[id].verbs = load_exit_msg

	for element in labels:
		id = findNewId(retMap.labels)
		retMap.labels[id] = Label(getText(element), int(element.getAttribute("x")), int(element.getAttribute("y")))

	return retMap


class exportClass(QDialog):
	def __init__(self, parent = None):
		super(exportClass, self).__init__(parent)
		self.resize(500, 500)
		self.setWindowTitle("Export")
		self.browser = QTextBrowser(self)
		self.browser.setGeometry(QRect(0, 0, 500, 500))
		if diggerconf.monospaceEdit:
			self.browser.setFontFamily("Monospace")
		layout = QVBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.browser)
		self.setLayout(layout)
	def exportAll(self, filename):
		self.browser.setText(generateCode(filename, roomList, exitList, labelList))

class optionsClass(QDialog):
	def __init__(self, parent=None):
		super(optionsClass, self).__init__(parent)
		layout = QFormLayout()
		self.setWindowTitle("Options")
		self.lbl = QLabel("Map Size")
		self.lbl2 = QLabel("Width")
		self.lbl3 = QLabel("Height")
		self.lbl4 = QLabel("Background Color")
		self.lbl5 = QLabel("Default room color")
		self.sp = QSpinBox()
		self.sp.setRange(200, 10000)
		self.sp2 = QSpinBox()
		self.sp2.setRange(200, 10000)
		self.btnRColor = QPushButton("Select...")
		self.btnBColor = QPushButton("Select...")
		self.btn1 = QPushButton("Ok")
		self.bColor = QColor()
		self.rColor = QColor()
		layout.addRow(self.lbl)
		layout.addRow(self.lbl2, self.lbl3)
		layout.addRow(self.sp, self.sp2)
		layout.addRow(self.lbl4, self.btnBColor)
		layout.addRow(self.lbl5, self.btnRColor)
		layout.addRow(self.btn1)
		self.setLayout(layout)
		self.btn1.clicked.connect(self.accept)
		self.btnRColor.clicked.connect(self.selectRoomColor)
		self.btnBColor.clicked.connect(self.selectBackgroundColor)

	def selectRoomColor(self):
		self.rColor = QColorDialog.getColor(initial = self.rColor)
	def selectBackgroundColor(self):
		self.bColor = QColorDialog.getColor(initial = self.bColor)

	def setData(self):
		self.sp.setValue(int(self.parent().parent().scene.width()))
		self.sp2.setValue(int(self.parent().parent().scene.height()))
		self.rColor = QColor(self.parent().parent().roomBColor)
		self.bColor = QColor(self.parent().parent().bColor)


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
		self.tabCode = QWidget()
		self.tab = QTabWidget()
		self.btn1 = QPushButton("Ok")
		self.btn1.clicked.connect(self.accept)
		self.tab.addTab(self.tabName, "Name")
		self.tab.addTab(self.tabDesc, "Description")
		self.tab.addTab(self.tabCode, "Code")
		self.color = QColor()
		tabLayout = QFormLayout()
		tabLayout.addRow(self.tab)
		tabLayout.addRow(self.btn1)
		self.setLayout(tabLayout)

		layout = QFormLayout() # Layout for name tab
		self.cur_room = 0
		self.lbl = QLabel("Name")
		self.le = QLineEdit()
		self.lbl2 = QLabel("Position")
		self.le2 = QLineEdit()
		self.le3 = QLineEdit()
		self.lbl3 = QLabel("Color")
		self.btnColor = QPushButton("Select...")
		self.btnColor.clicked.connect(self.openColorDialog)

		self.lbl4 = QLabel("Size")
		self.sp = QSpinBox()
		self.sp.setRange(5, 50)

		layout.addRow(self.lbl,self.le)
		layout.addRow(self.lbl2)
		layout.addRow(self.le2, self.le3)
		layout.addRow(self.lbl3, self.btnColor)
		layout.addRow(self.lbl4, self.sp)
		self.tabName.setLayout(layout)

		layout2 = QFormLayout() # Layout for description tab
		self.lblDesc = QLabel("Description")
		self.te = QTextEdit()
		layout2.addRow(self.lblDesc)
		layout2.addRow(self.te)
		self.tabDesc.setLayout(layout2)

		layout3 = QFormLayout() # Layout for code tab
		self.lblCode = QLabel("Code")
		self.te2 = QTextEdit()
		layout3.addRow(self.lblCode)
		layout3.addRow(self.te2)
		self.tabCode.setLayout(layout3)

		if diggerconf.monospaceEdit:
			self.te.setFontFamily("Monospace")
			self.te2.setFontFamily("Monospace")

	def openColorDialog(self):
		self.color = QColorDialog.getColor(initial = self.color)



	def setData(self, room):
		self.color = QColor(roomList[room].bColor)
		self.le.setText(roomList[room].name)
		self.te.setPlainText(roomList[room].desc)
		self.te2.setPlainText(str("\n".join(roomList[room].code))) # Join lines of mushcode
		self.le2.setText(str(int(roomList[room].x)))
		self.le3.setText(str(int(roomList[room].y)))
		self.sp.setValue((roomList[room].size-1)/2)

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
		self.btn1.clicked.connect(self.accept)

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
		self.tabMsg = QWidget()
		self.btn1 = QPushButton('Ok')
		self.btn1.clicked.connect(self.accept)
		self.tab = QTabWidget()
		self.tab.addTab(self.tabNames, 'Name')
		self.tab.addTab(self.tabDesc, 'Description')
		self.tab.addTab(self.tabAlias, 'Alias')
		self.tab.addTab(self.tabMsg, 'Verbs')

		tabLayout = QFormLayout()
		tabLayout.addRow(self.tab)
		tabLayout.addRow(self.btn1)
		self.setLayout(tabLayout)

		layout = QFormLayout()
		self.lbl = QLabel("Name")
		self.le = QLineEdit()
		self.lbl2 = QLabel("Source")
		self.combo1 = QComboBox()
		self.lbl3 = QLabel("Destination")
		self.combo2 = QComboBox()
		layout.addRow(self.lbl,self.le)
		layout.addRow(self.lbl2, self.combo1)
		layout.addRow(self.lbl3, self.combo2)
		self.tabNames.setLayout(layout)

		layout2 = QFormLayout()
		self.list1 = aliasList()
		self.lblList1 = QLabel("Alias list")
		layout2.addRow(self.lblList1)
		layout2.addRow(self.list1)
		self.tabAlias.setLayout(layout2)

		layout3 = QFormLayout()
		self.te1 = QTextEdit()
		self.lblDesc1 = QLabel("Exit description")
		layout3.addRow(self.lblDesc1)
		layout3.addRow(self.te1)
		self.tabDesc.setLayout(layout3)

		layout4 = QFormLayout()

		self.msgLabel = {}
		self.msgLineEdit = {}
		for i in verbList:
			self.msgLabel[i] = QLabel('@' + i)
			self.msgLineEdit[i] = QLineEdit()
			layout4.addRow(self.msgLabel[i], self.msgLineEdit[i])

		self.tabMsg.setLayout(layout4)

		self.btn1.clicked.connect(self.accept)

		if diggerconf.monospaceEdit:
			self.te1.setFontFamily("Monospace")

	def setData(self):
		self.combo2.addItem("#-1: No destination")
		self.rDict["#-1: No destination"] = -1
		for i, room in roomList.items():
			self.rDict[str("#" + str(i) + ": " + room.name)] = i
			self.combo1.addItem("#" + str(i) + ": " + room.name)
			self.combo2.addItem("#" + str(i) + ": " + room.name)
	def fillData(self, exit):
		self.le.setText(exitList[exit].name)
		self.combo1.setCurrentIndex(self.combo1.findText("#" + str(exitList[exit].source) + ": " + roomList[exitList[exit].source].name))
		if exitList[exit].dest == -1:
			self.combo2.setCurrentIndex(0)
		else:
			self.combo2.setCurrentIndex(self.combo2.findText("#" + str(exitList[exit].dest) + ": " + roomList[exitList[exit].dest].name))
		self.te1.setPlainText(exitList[exit].desc)
		if len(exitList[exit].alias) > 0: # The exit does have an alias
			for x in exitList[exit].alias.split(";"):
				self.list1.addItem(x)
		for key, value in exitList[exit].verbs.items():
			self.msgLineEdit[key].setText(value)

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
		self.btn1.clicked.connect(self.accept)
		layout.addRow(self.btn1)
