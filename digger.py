# -*- coding: utf-8 -*-


import sys
import math
from PyQt5 import QtCore, QtGui, QtXml
from diggerUi import *
import platform
__version__ = "1.0.0"


try:
    from PyQt5.QtCore import QString
except ImportError:
    QString = str

try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	def _fromUtf8(s):
		return s

try:
	_encoding = QtWidgets.QApplication.UnicodeUTF8
	def _translate(context, text, disambig):
		return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
	def _translate(context, text, disambig):
		return QtWidgets.QApplication.translate(context, text, disambig)



class Main(QtWidgets.QMainWindow):
	def __init__(self):
		QtWidgets.QMainWindow.__init__(self, parent = None)
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.ui.actionExport.triggered.connect(self.exportDump)
		self.ui.actionNew.triggered.connect(self.newFile)
		self.ui.actionOptions.triggered.connect(self.setOptions)
		self.ui.actionAbout.triggered.connect(self.viewAbout)
		self.ui.actionOpen.triggered.connect(self.openFile)
		self.ui.actionSave.triggered.connect(self.saveFile)
		self.ui.actionToggleText.triggered.connect(self.toggleText)
		self.isNewFile = 1
		self.fileName = "Untitled"
		self.bColor = "#FFFFFF"
		self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))

	def resizeEvent(self, event):
		self.ui.graphicsView.setGeometry(QtCore.QRect(0, 0, event.size().width(), event.size().height()))
		self.ui.scene.setSceneRect(0, 0, event.size().width(), event.size().height() - 14)
		for iRoom in roomList:
			iRoom.box.move_restrict_rect = QRectF(0, 0, event.size().width(), event.size().height() - 14)

	def toggleText(self):
		self.drawAll()

	def readMapNode(self, element):
		global roomList
		global exitList
		global labelList
		global id_room
		global id_exit
		global id_label
		def intFromQStr(qstr):
			return int(str(qstr))
		def getText(node):
			child = node.firstChild()
			text = QString()
			while not child.isNull():
				if child.nodeType() == QtXml.QDomNode.TextNode:
					text += child.toText().data()
				child = child.nextSibling()
			return text.strip()
		def readLabelNode(element):
			global id_label
			load_label_x = intFromQStr(element.attribute("x"))
			load_label_y = intFromQStr(element.attribute("y"))
			load_label_text = getText(element)
			labelList.append(Label(load_label_text, load_label_x, load_label_y))
			self.ui.scene.addItem(labelList[id_label].text)
			self.ui.scene.addItem(labelList[id_label].box)
			id_label = id_label + 1
		def readRoomNode(element):
			global id_room
			load_room_id = intFromQStr(element.attribute("id"))
			load_room_x = intFromQStr(element.attribute("x"))
			load_room_y = intFromQStr(element.attribute("y"))
			load_room_name = load_room_desc = None
			node = element.firstChild()
			while load_room_name is None or load_room_desc is None:
				if node.isNull():
					raise ValueError("Missing name or description")
				if node.toElement().tagName() == "name":
					load_room_name = getText(node)
				elif node.toElement().tagName() == "description":
					load_room_desc = getText(node)
				node = node.nextSibling()
			roomList.append(Room(load_room_name, load_room_id, self))
			roomList[id_room].desc = load_room_desc
			roomList[id_room].x = load_room_x
			roomList[id_room].y = load_room_y
			self.ui.scene.addItem(roomList[id_room].box)
			self.ui.scene.addItem(roomList[id_room].text)
			id_room = id_room + 1

		def readExitNode(element):
			global id_exit
			global exitList
			load_exit_id = intFromQStr(element.attribute("id"))
			load_exit_source = intFromQStr(element.attribute("source"))
			load_exit_dest = intFromQStr(element.attribute("destination"))
			load_exit_twoway = str(element.attribute("twoway"))
			load_exit_name = load_exit_return = load_exit_alias = None
			node = element.firstChild()
			while not node.isNull():
				if node.toElement().tagName() == "name":
					load_exit_name = getText(node)
				if node.toElement().tagName() == "return":
					load_exit_return = getText(node)
				elif node.toElement().tagName() == "alias":
					load_exit_alias = getText(node)
				node = node.nextSibling()
			exitList.append(Exit(load_exit_name, load_exit_id, load_exit_source))
			if load_exit_twoway == "True":
				exitList[id_exit].twoWay = True
				exitList[id_exit].returnName = load_exit_return
			exitList[id_exit].alias = load_exit_alias
			exitList[id_exit].dest = load_exit_dest
			self.ui.scene.addItem(exitList[id_exit].line)
			id_exit = id_exit + 1


		load_map_width = intFromQStr(element.attribute("width"))
		load_map_height = intFromQStr(element.attribute("height"))
		load_map_bcolor = str(element.attribute("bcolor"))
		node = element.firstChild()
		while not node.isNull():
			if node.toElement().tagName() == "room":
				readRoomNode(node.toElement())
			elif node.toElement().tagName() == "exit":
				readExitNode(node.toElement())
			elif node.toElement().tagName() == "label":
				readLabelNode(node.toElement())
			node = node.nextSibling()
		self.bColor = load_map_bcolor
		self.ui.scene.setBackgroundBrush(QColor(load_map_bcolor))
		self.resize(load_map_width, load_map_height)
		self.ui.graphicsView.setGeometry(QtCore.QRect(0, 0, load_map_width, load_map_height))
		self.ui.menubar.setGeometry(QtCore.QRect(0, 0, load_map_width, load_map_height))
		self.ui.scene.setSceneRect(0, 0, load_map_width, load_map_height - 14)

	def populateFromDOM(self, dom):
		global roomList
		global exitList
		global labelList
		global id_room
		global id_exit
		global id_label
		del roomList[:]
		del exitList[:]
		del labelList[:]
		id_room = 0
		id_exit = 0
		id_label = 0
		self.ui.scene.clear()
		root = dom.documentElement()
		if root.tagName() != "DIGGER":
			raise ValueError("not a Digger XML file")
		node = root.firstChild()
		while not node.isNull():
			if node.toElement().tagName() == "map":
				self.readMapNode(node.toElement())
			node = node.nextSibling()
		self.drawAll()

	def openFile(self):
		fname = QFileDialog.getOpenFileName(self, 'Open file', '/',"")[0]
		if fname:
			dom = QtXml.QDomDocument()
			error = None
			fh = None
			try:
				fh = QFile(fname)
				if not fh.open(QIODevice.ReadOnly):
					raise IOError(unicode(fh.errorString()))
				if not dom.setContent(fh):
					raise ValueError("could not parse XML")
			except (IOError, OSError, ValueError) as e:
				error = "Failed to import: %s" % e
			finally:
				if fh is not None:
					fh.close()
				if error is not None:
					return False, error
			try:
				self.populateFromDOM(dom)
				self.fileName = fname
				self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))
			except ValueError as e:
				return False, "Failed to import: %s" % e


	def saveFile(self):
		fname = QFileDialog.getSaveFileName(self, 'Save file', '/', "")[0]
		if fname:
			if self.isNewFile == 1:
				self.fileName = fname
				self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))
				self.isNewFile = 0
				fsave = QFile(fname)
				if not fsave.open(QIODevice.WriteOnly):
					raise IOError(unicode(fsave.errorString()))
				stream = QTextStream(fsave)
				stream.setCodec("UTF-8")
				stream << ("<?xml version='1.0' encoding='UTF-8'?>\n" + "<!DOCTYPE DIGGER>\n" + "<DIGGER VERSION='%s'>\n" % (__version__))
				stream << ("<map width='%d' height='%d' bcolor='%s'>\n" % (self.ui.graphicsView.width(), self.ui.graphicsView.height(), self.bColor))
				global roomList
				global exitList
				for iRoom in roomList:
					stream << ("\t<room id='%d' x='%d' y='%d'>\n" % (iRoom.id, iRoom.x, iRoom.y))
					stream << "\t\t<name> " << Qt.escape(iRoom.name) << " </name>\n"
					stream << "\t\t<description> " << Qt.escape(iRoom.desc) << " </description>\n"
					stream << "\t</room>\n"
				for iExit in exitList:
					stream << ("\t<exit id='%d' source='%d' destination='%d' twoway='%s'>\n" % (iExit.id, iExit.source, iExit.dest, str(iExit.twoWay)))
					stream << "\t\t<name> " << Qt.escape(iExit.name) << " </name>\n"
					stream << "\t\t<return> " << Qt.escape(iExit.returnName) << " </return>\n"
					for x in range(len(iExit.alias)):
						stream << "\t\t<alias>" << Qt.escape(iExit.alias[x]) << "</alias>\n"
					stream << "\t</exit>\n"
				for x in range(len(labelList)):
					stream << ("\t<label x='%d' y='%d'> " % (labelList[x].x, labelList[x].y))
					stream << "\t\t" << Qt.escape(labelList[x].normalText)
					stream << "\t</label>\n"
				stream << "</map>\n"

	def isRGB(self, number):
		check = 1
		for x in list(number[1:]):
			if (ord(x) >= 48 and ord(x) <= 57) or ((ord(x) >= 65 and ord(x) <= 70) or (ord(x) >= 97 and ord(x) <= 102)):
				check = check * 1
			else:
				check = 0
		return check and (number[0] == '#')

	def viewAbout(self):
		QMessageBox.about(self, "About Digger", """<b>Digger</b> v %s<p>Copyright &copy; 2016 Martin Tirado. All rights reserved. <p> This program can be used to design MUSH words through a graphical interface. <p> Python %s - Qt %s - PyQt %s on %s <p> Hosted on <a href='https://github.com/mtirado1/digger'> Github </a>""" % (__version__, platform.python_version(), QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

	def setOptions(self):
		optionsDialog = optionsClass(self)
		optionsDialog.setData()
		if optionsDialog.exec_():
			colorString = str(optionsDialog.le3.text())
			if self.isRGB(colorString):
				self.bColor = colorString
				self.ui.scene.setBackgroundBrush(QColor(colorString))
			if is_number(optionsDialog.le.text()) and is_number(optionsDialog.le2.text()):
				self.resize(int(optionsDialog.le.text()), int(optionsDialog.le2.text()))
				self.ui.graphicsView.setGeometry(QtCore.QRect(0, 0, int(optionsDialog.le.text()), int(optionsDialog.le2.text())))
				self.ui.menubar.setGeometry(QtCore.QRect(0, 0, int(optionsDialog.le.text()), int(optionsDialog.le2.text())))
				self.ui.scene.setSceneRect(0, 0, int(optionsDialog.le.text()), int(optionsDialog.le2.text()) - 14)
				global roomList
				for x in range(len(roomList)):
					roomList[x].box.move_restrict_rect = QRectF(0, 0, self.ui.scene.width(), self.ui.scene.height())

	def exportDump(self):
		exportWindow = exportClass(self)
		exportWindow.exportAll()
		exportWindow.show()

	def newFile(self): # New Map
		self.fileName = "Untitled"
		self.bColor = "#FFFFFF"
		self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))
		self.ui.scene.setBackgroundBrush(QColor(self.bColor))
		self.isNewFile = 1
		global roomList
		global exitList
		global labelList
		global id_room
		global id_exit
		global id_label
		id_room = 0
		id_exit = 0
		id_label = 0
		del roomList[:]
		del exitList[:]
		del labelList[:]
		self.ui.scene.clear()

	def drawAll(self):
		global roomList
		global exitList
		global labelList
		def getPosOfRoom(room_id_):
			for x in range(len(roomList)):
				if roomList[x].id == room_id_:
					return x
		for x in range(len(exitList)):
			self.ui.scene.removeItem(exitList[x].line)
			coord_a = roomList[getPosOfRoom(exitList[x].source)].x + ROOM_CENTER
			coord_b = roomList[getPosOfRoom(exitList[x].source)].y + ROOM_CENTER
			if exitList[x].dest == -1:
				coord_c = roomList[getPosOfRoom(exitList[x].source)].x + 3 * ROOM_CENTER
				coord_d = roomList[getPosOfRoom(exitList[x].source)].y + 3 * ROOM_CENTER
			else:
				coord_c = roomList[getPosOfRoom(exitList[x].dest)].x + ROOM_CENTER
				coord_d = roomList[getPosOfRoom(exitList[x].dest)].y + ROOM_CENTER

			exitList[x].line.setLine(coord_a, coord_b, coord_c, coord_d)
			self.ui.scene.addItem(exitList[x].line)
			exitList[x].line.setZValue(0)
		for j in range(len(roomList)):
			self.ui.scene.removeItem(roomList[j].box)
			self.ui.scene.removeItem(roomList[j].text)
			roomList[j].box.setPos(roomList[j].x, roomList[j].y)
			roomList[j].box.index=j
			roomString = "<p><b>" + roomList[j].name + "</b>"
			roomString = roomString + "<br />Exits:<br />"
			for k in range(len(exitList)):
				if exitList[k].source == roomList[j].id:
					roomString = roomString + exitList[k].name + "<br />"
				if exitList[k].dest == roomList[j].id and exitList[k].twoWay:
					roomString = roomString + exitList[k].returnName + "<br />"
			if self.ui.actionToggleText.isChecked():
				roomList[j].text.setHtml(roomString + "</p>")
			else:
				roomList[j].text.setHtml("")
			roomList[j].text.setPos(QPointF(roomList[j].x + ROOM_CENTER + 2 - (roomList[j].text.boundingRect().width() / 2), roomList[j].y + ROOM_SIZE + 5))
			roomList[j].box.setBrush(QColor("#FF0000"))
			roomList[j].box.setRect(0, 0, ROOM_SIZE, ROOM_SIZE)
			self.ui.scene.addItem(roomList[j].box)
			self.ui.scene.addItem(roomList[j].text)
			roomList[j].box.setZValue(1)
		for j in range(len(labelList)):
			labelList[j].text.setZValue(10)
			labelList[j].box.setZValue(9)
			labelList[j].text.setPos(labelList[j].x, labelList[j].y)
			labelList[j].box.setPos(labelList[j].x, labelList[j].y)

	def digRoom(self, x_, y_):
		roomDialog = newRoom(self)
		if roomDialog.exec_():
			global roomList
			global id_room
			if roomDialog.le.text() != "":
				roomList.append(Room(roomDialog.le.text(), id_room, self))
			roomList[id_room].x = x_
			roomList[id_room].y = y_
			self.ui.scene.addItem(roomList[id_room].box)
			self.ui.scene.addItem(roomList[id_room].text)
			self.drawAll()
			id_room = id_room + 1
			roomDialog.close()

	def deleteRoom(self, id_):
		self.ui.scene.removeItem(roomList[id_].box)
		self.ui.scene.removeItem(roomList[id_].text)

		global id_room
		global id_exit
		id_room = id_room - 1
		deleted = True
		while deleted:
			for x in range(len(exitList)): # First round, delete all sources
				if exitList[x].source == roomList[id_].id:
					self.ui.scene.removeItem(exitList[x].line)
					del exitList[x]
					id_exit = id_exit - 1
					break
				else:
					deleted = False
			if not exitList:
				deleted = False
		for x in range(len(exitList)): # Next round, fix all destinations
			if exitList[x].dest == roomList[id_].id: # The exits still exists, but without destination
				exitList[x].dest = -1
		del roomList[id_]
		self.drawAll()

	def openExit(self):
		exitDialog = newExit(self)
		exitDialog.setData()
		if exitDialog.exec_():
			global exitList
			global id_exit
			exitList.append(Exit(exitDialog.le.text(), id_exit, exitDialog.rDict[exitDialog.combo3.currentText()]))
			if exitDialog.checkBox.isChecked():
				exitList[id_exit].twoWay = True
				exitList[id_exit].returnName = exitDialog.le2.text()
			exitList[id_exit].dest = exitDialog.rDict[exitDialog.combo4.currentText()]
			self.ui.scene.addItem(exitList[id_exit].line)
			self.drawAll()
			id_exit = id_exit + 1
			exitDialog.close()
	def openExitName(self, source, destination):
		global id_exit
		global roomList
		global exitList
		exitList.append(Exit("##placeholder##", id_exit, roomList[source].id)) # User will be asked for name soon
		exitList[id_exit].dest = destination
		self.ui.scene.addItem(exitList[id_exit].line)
		exitDialog = newExitName()
		if exitDialog.exec_():
			exitList[id_exit].name = exitDialog.le.text()
			if exitDialog.checkBox.isChecked():
				exitList[id_exit].twoWay = True
				exitList[id_exit].returnName = exitDialog.le2.text()
			self.drawAll()
		id_exit = id_exit + 1

	def addLabel(self, x_, y_):
		labelDialog = addLabel()
		if labelDialog.exec_():
			global labelList
			global id_label
			labelList.append(Label(labelDialog.le.text(), x_, y_))
			labelList[id_label].box.index = id_label
			self.ui.scene.addItem(labelList[id_label].text)
			self.ui.scene.addItem(labelList[id_label].box)
			self.drawAll()
			id_label = id_label + 1
			labelDialog.close()
	def deleteLabel(self, id_):
		global labelList
		global id_label
		self.ui.scene.removeItem(labelList[id_].text)
		self.ui.scene.removeItem(labelList[id_].box)
		del labelList[id_]
		id_label = id_label - 1
		self.drawAll()


if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = Main()
	window.show()
	sys.exit(app.exec_())
