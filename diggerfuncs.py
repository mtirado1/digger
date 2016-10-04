import os
import sys
import diggerconf
from PyQt4.QtCore import *
from PyQt4.QtGui import *

__version__ = "1.2.1"

#######################################
# Global Lists
roomList = []
exitList = []
labelList = []

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

def saveToFile(fname, parent):
	fsave = QFile(fname)
	if not fsave.open(QIODevice.WriteOnly):
		raise IOError, unicode(fsave.errorString())
	stream = QTextStream(fsave)
	stream.setCodec("UTF-8")
	stream << ("<?xml version='1.0' encoding='UTF-8'?>\n" + "<!DOCTYPE DIGGER>\n" + "<DIGGER VERSION='%s'>\n" % (__version__))
	stream << ("<map width='%d' height='%d' bcolor='%s'>\n" % (parent.ui.scene.width(), parent.ui.scene.height(), parent.bColor))
	global roomList
	global exitList
	for iRoom in roomList:
		stream << ("\t<room id='%d' x='%d' y='%d' bcolor='%s'>\n" % (iRoom.id, iRoom.x, iRoom.y, iRoom.bColor))
		stream << "\t\t<name>" << Qt.escape(iRoom.name) << "</name>\n"
		if iRoom.desc != "":
			stream << "\t\t<description>" << mushEscape(Qt.escape(iRoom.desc)) << "</description>\n"
		if iRoom.code:
			for codeLine in iRoom.code:
				stream << "\t\t<code>" << Qt.escape(codeLine) << "</code>\n"
		stream << "\t</room>\n"
	for iExit in exitList:
		stream << ("\t<exit id='%d' source='%d' destination='%d'>\n" % (iExit.id, iExit.source, iExit.dest))
		stream << "\t\t<name>" << Qt.escape(iExit.name) << "</name>\n"
		if iExit.desc != "":
			stream <<"\t\t<description>" << mushEscape(Qt.escape(iExit.desc)) << "</description>\n"
		if iExit.alias != "":
			stream << "\t\t<alias>" << Qt.escape(iExit.alias) << "</alias>\n"
		stream << "\t</exit>\n"
	for x in xrange(len(labelList)):
		stream << ("\t<label x='%d' y='%d'>" % (labelList[x].x, labelList[x].y))
		stream << Qt.escape(labelList[x].normalText)
		stream << "</label>\n"
	stream << "</map>\n</DIGGER>"

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
			self.scene().parent().parent().drawLabel(labelList[self.index])
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
		#self.setRect(QRectF(0,0,1080,683))

	def mouseReleaseEvent(self, event):
		if self.moved == 1:
			QGraphicsRectItem.mouseReleaseEvent(self, event)
			self.scene().parent().parent().drawRoom(roomList[self.index])
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
		self.bColor = ""
		self.x = 0
		self.y = 0
		self.box = roomBox()
		self.text = QGraphicsTextItem()
		self.code = [] # List of lines of code to be executed in room

class Exit:
	type='exit'
	def __init__(self, name, id_, source):

		self.id = id_
		self.name = name
		self.alias = ""
		self.desc = ""
		self.source = source
		self.dest = -1
		self.line = QGraphicsLineItem()
		if str(name) in diggerconf.aliasDict:
			self.name = diggerconf.aliasDict[str(name)][0]
			for x in xrange(len(diggerconf.aliasDict[str(name)])):
				if x != 0:
					self.alias += diggerconf.aliasDict[str(name)][x] + ";"
			self.alias = self.alias[:-1]

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


def generateCode():
	def isCode(codelist):
		if codelist:
			if codelist[0] == "" and len(codelist) == 1:
				return False
			return True
		return False
	strExport = "@@ Generated by Digger v" + __version__ + "\n"
	for k in roomList:
		strExport += "@dig/teleport " + k.name + "\n"
		if k.desc != "":
			strExport += "@desc here=" + mushEscape(str(k.desc)) + "\n"
		strExport += "think set(me, " + diggerconf.attributePrefix + str(k.id) + ":%l)\n"

	for k in roomList:
		sourceExits = []
		for j in exitList:
			if j.source == k.id: # Select source exits
				sourceExits.append(j)
		if isCode(k.code) or sourceExits:
			strExport += "@tel [v(" + diggerconf.attributePrefix + str(k.id) + ")]\n"
		for j in sourceExits:
			aliasString = ""
			if j.alias != "":
				aliasString += ";" + j.alias
			if j.dest != -1:
				strExport += "@open " + j.name + aliasString + "=[v(" + diggerconf.attributePrefix + str(j.dest) + ")]\n"
			else:
				strExport += "@open " + j.name + aliasString + "\n"
			if j.desc != "":
				strExport += "@desc " + j.name + "=" + mushEscape(str(j.desc)) + "\n"
		if isCode(k.code):
			if diggerconf.enableImports:
				for codeLine in k.code:
					codeWords = codeLine.split()
					if codeWords[0] == "@@@" and codeWords[1] == "import":
						fname = str(" ".join(codeWords[2:]))
						if os.path.isfile(fname):
							strExport += "@@ Import file: " + fname + "\n"
							with open(str(fname), 'r') as codeFile:
								strExport += codeFile.read() + "\n"
						else:
							strExport += "@@ Import file: " + fname + " not found.\n"
					else:
						strExport += codeLine + "\n"
			else:
				for codeLine in k.code:
					strExport += codeLine + "\n"
	if diggerconf.clearAttributes:
		for k in roomList:
			strExport += "&" + diggerconf.attributePrefix  + str(k.id) + " me\n"
	if diggerconf.exportLabels:
		for k in labelList:
			strExport += "think LABEL: *** " + k.normalText + " ***\n"
	return strExport

def exportCodeToFile():
	fname = QFileDialog.getSaveFileName(None, 'Export to File', '/', "")
	fsave = QFile(fname)
	if not fsave.open(QIODevice.WriteOnly):
		raise IOError, unicode(fsave.errorString())
	stream = QTextStream(fsave)
	stream.setCodec("UTF-8")
	stream << generateCode()

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
	def exportAll(self):
		self.browser.setText(generateCode())

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
		self.le3 = QLineEdit()
		self.le4 = QLineEdit()
		self.btn1 = QPushButton("Ok")
		layout.addRow(self.lbl)
		layout.addRow(self.lbl2, self.lbl3)
		layout.addRow(self.sp, self.sp2)
		layout.addRow(self.lbl4)
		layout.addRow(self.le3)
		layout.addRow(self.lbl5)
		layout.addRow(self.le4)
		layout.addRow(self.btn1)
		self.setLayout(layout)
		self.connect(self.btn1, SIGNAL("clicked()"), self, SLOT("accept()"))
	def setData(self):
		self.sp.setValue(int(self.parent().ui.scene.width()))
		self.sp2.setValue(int(self.parent().ui.scene.height()))
		self.le3.setText(str(self.parent().bColor))
		self.le4.setText(str(self.parent().roomBColor))


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
		layout.addRow(self.lbl,self.le)
		layout.addRow(self.lbl2)
		layout.addRow(self.le2, self.le3)
		layout.addRow(self.lbl3, self.btnColor)
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
		self.color = QColorDialog.getColor()
		


	def setData(self, room):
		self.le.setText(roomList[room].name)
		self.te.setPlainText(roomList[room].desc)
		self.te2.setPlainText(str("\n".join(roomList[room].code))) # Join lines of mushcode
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

		self.btn1.clicked.connect(self.accept)

		if diggerconf.monospaceEdit:
			self.te1.setFontFamily("Monospace")

	def setData(self):
		global exitList
		self.combo2.addItem("#-1: No destination")
		self.rDict["#-1: No destination"] = -1
		for i in roomList:
			self.rDict[str("#" + str(i.id) + ": " + i.name)] = i.id
			self.combo1.addItem("#" + str(i.id) + ": " + i.name)
			self.combo2.addItem("#" + str(i.id) + ": " + i.name)
	def fillData(self, exit):
		self.le.setText(exitList[exit].name)
		self.combo1.setCurrentIndex(self.combo1.findText("#" + str(exitList[exit].source) + ": " + roomList[exitList[exit].source].name))
		if exitList[exit].dest == -1:
			self.combo2.setCurrentIndex(0)
		else:
			self.combo2.setCurrentIndex(self.combo2.findText("#" + str(exitList[exit].dest) + ": " + roomList[exitList[exit].dest].name))
		self.te1.setPlainText(exitList[exit].desc)
		for x in exitList[exit].alias.split(";"):
			self.list1.addItem(x)

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
