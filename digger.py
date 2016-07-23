# -*- coding: utf-8 -*-


import sys
import math
import xml.dom.minidom
from xml.dom.minidom import parse
from PyQt4 import QtCore, QtGui
from diggerUi import *
import platform
__version__ = "1.0.0"


try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	def _fromUtf8(s):
		return s

try:
	_encoding = QtGui.QApplication.UnicodeUTF8
	def _translate(context, text, disambig):
		return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
	def _translate(context, text, disambig):
		return QtGui.QApplication.translate(context, text, disambig)



class Main(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self, parent = None)
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

		def getText(element):
			return element.childNodes[0].data

		def readLabelNode(element):
			global id_label
			load_label_x = int(element.getAttribute("x"))
			load_label_y = int(element.getAttribute("y"))
			load_label_text = getText(element)
			labelList.append(Label(load_label_text, load_label_x, load_label_y))
			self.ui.scene.addItem(labelList[id_label].text)
			self.ui.scene.addItem(labelList[id_label].box)
			id_label = id_label + 1
		def readRoomNode(element):
			global id_room
			load_room_id = int(element.getAttribute("id"))
			load_room_x = int(element.getAttribute("x"))
			load_room_y = int(element.getAttribute("y"))

			load_room_name = getText(element.getElementsByTagName("name")[0])
			load_room_desc = ""
			if element.getElementsByTagName("description"):
				load_room_desc = getText(element.getElementsByTagName("description")[0])

			roomList.append(Room(load_room_name, load_room_id, self))
			roomList[id_room].desc = mushUnEscape(load_room_desc)
			roomList[id_room].x = load_room_x
			roomList[id_room].y = load_room_y
			self.ui.scene.addItem(roomList[id_room].box)
			self.ui.scene.addItem(roomList[id_room].text)
			id_room = id_room + 1

		def readExitNode(element):
			global id_exit
			global exitList
			load_exit_id = int(element.getAttribute("id"))
			load_exit_source = int(element.getAttribute("source"))
			load_exit_dest = int(element.getAttribute("destination"))
			load_exit_twoway = element.getAttribute("twoway")
			load_exit_alias = []
			load_exit_returnAlias = []
			load_exit_name = getText(element.getElementsByTagName("name")[0])
			load_exit_return = getText(element.getElementsByTagName("return")[0])
			load_exit_desc = ""
			load_exit_returnDesc = ""
			if element.getElementsByTagName("description"):
				load_exit_desc = getText(element.getElementsByTagName("description")[0])
			if element.getElementsByTagName("returndescription"):
				load_exit_returnDesc = getText(element.getElementsByTagName("returndescription")[0])
			for i in element.getElementsByTagName("alias"):
				load_exit_alias.append(getText(i))
			for i in element.getElementsByTagName("returnalias"):
				load_exit_returnAlias.append(getText(i))

			exitList.append(Exit(load_exit_name, load_exit_id, load_exit_source))
			if load_exit_twoway == "True":
				exitList[id_exit].twoWay = True
				exitList[id_exit].returnName = load_exit_return
			exitList[id_exit].alias = load_exit_alias
			exitList[id_exit].returnAlias = load_exit_returnAlias
			exitList[id_exit].dest = load_exit_dest
			exitList[-1].desc = mushUnEscape(load_exit_desc)
			exitList[-1].returnDesc = mushUnEscape(load_exit_returnDesc)
			self.ui.scene.addItem(exitList[id_exit].line)
			id_exit = id_exit + 1

		load_map_width =  int(element.getAttribute("width"))
		load_map_height = int(element.getAttribute("height"))
		load_map_bcolor = element.getAttribute("bcolor")
		rooms = element.getElementsByTagName("room")
		exits = element.getElementsByTagName("exit")
		labels = element.getElementsByTagName("label")
		for i in rooms:
			readRoomNode(i)
		for i in exits:
			readExitNode(i)
		for i in labels:
			readLabelNode(i)

		self.bColor = load_map_bcolor
		self.ui.scene.setBackgroundBrush(QColor(load_map_bcolor))
		self.resize(load_map_width, load_map_height)
		self.ui.graphicsView.setGeometry(QtCore.QRect(0, 0, load_map_width, load_map_height))
		self.ui.menubar.setGeometry(QtCore.QRect(0, 0, load_map_width, load_map_height))
		self.ui.scene.setSceneRect(0, 0, load_map_width, load_map_height - 14)

	def populateFromDOM(self, fname):
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
		DOMTree = xml.dom.minidom.parse(str(fname))
		root = DOMTree.documentElement
		if root.tagName != "DIGGER":
			raise ValueError, "not a Digger XML file"
		maps = root.getElementsByTagName("map")[0]
		self.readMapNode(maps)
		self.drawAll()

	def openFile(self):
		fname = QFileDialog.getOpenFileName(self, 'Open file', '/',"XML Files (*.xml)")
		if fname:
			self.populateFromDOM(fname)
			self.fileName = fname
			self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))


	def saveFile(self):
		fname = QFileDialog.getSaveFileName(self, 'Save file', '/', "XML Files (*.xml)")
		if fname:
			if self.isNewFile == 1:
				self.fileName = fname
				self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))
				self.isNewFile = 0
				fsave = QFile(fname)
				if not fsave.open(QIODevice.WriteOnly):
					raise IOError, unicode(fsave.errorString())
				stream = QTextStream(fsave)
				stream.setCodec("UTF-8")
				stream << ("<?xml version='1.0' encoding='UTF-8'?>\n" + "<!DOCTYPE DIGGER>\n" + "<DIGGER VERSION='%s'>\n" % (__version__))
				stream << ("<map width='%d' height='%d' bcolor='%s'>\n" % (self.ui.graphicsView.width(), self.ui.graphicsView.height(), self.bColor))
				global roomList
				global exitList
				for iRoom in roomList:
					stream << ("\t<room id='%d' x='%d' y='%d'>\n" % (iRoom.id, iRoom.x, iRoom.y))
					stream << "\t\t<name>" << Qt.escape(iRoom.name) << "</name>\n"
					if iRoom.desc != "":
						stream << "\t\t<description>" << mushEscape(Qt.escape(iRoom.desc)) << "</description>\n"
					stream << "\t</room>\n"
				for iExit in exitList:
					stream << ("\t<exit id='%d' source='%d' destination='%d' twoway='%s'>\n" % (iExit.id, iExit.source, iExit.dest, str(iExit.twoWay)))
					stream << "\t\t<name>" << Qt.escape(iExit.name) << "</name>\n"
					stream << "\t\t<return>" << Qt.escape(iExit.returnName) << "</return>\n"
					if iExit.desc != "":
						stream <<"\t\t<description>" << mushEscape(Qt.escape(iExit.desc)) << "</description>\n"
					if iExit.returnDesc != "":
						stream <<"\t\t<returndescription>" << mushEscape(Qt.escape(iExit.returnDesc)) << "</returndescription>\n"
					for x in xrange(len(iExit.alias)):
						stream << "\t\t<alias>" << Qt.escape(iExit.alias[x]) << "</alias>\n"
					for x in xrange(len(iExit.returnAlias)):
						stream << "\t\t<returnalias>" << Qt.escape(iExit.returnAlias[x]) << "</returnalias>\n"
					stream << "\t</exit>\n"
				for x in xrange(len(labelList)):
					stream << ("\t<label x='%d' y='%d'>" % (labelList[x].x, labelList[x].y))
					stream << Qt.escape(labelList[x].normalText)
					stream << "</label>\n"
				stream << "</map>\n</DIGGER>"

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
				for x in xrange(len(roomList)):
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
			for x in xrange(len(roomList)):
				if roomList[x].id == room_id_:
					return x
		for x in xrange(len(exitList)):
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
		for j in xrange(len(roomList)):
			self.ui.scene.removeItem(roomList[j].box)
			self.ui.scene.removeItem(roomList[j].text)
			roomList[j].box.setPos(roomList[j].x, roomList[j].y)
			roomList[j].box.index=j
			roomString = "<p><b>" + roomList[j].name + "</b>"
			roomString = roomString + "<br />Exits:<br />"
			for k in xrange(len(exitList)):
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
		for j in xrange(len(labelList)):
			labelList[j].text.setZValue(10)
			labelList[j].box.setZValue(9)
			labelList[j].text.setPos(labelList[j].x, labelList[j].y)
			labelList[j].box.setPos(labelList[j].x, labelList[j].y)

	def digRoom(self, x_, y_):
		global roomList
		roomDialog = newRoom(self)
		if roomDialog.exec_():
			global roomList
			global id_room
			if roomDialog.le.text() != "":
				roomList.append(Room(roomDialog.le.text(), findNewId(roomList), self))
			roomList[id_room].x = x_
			roomList[id_room].y = y_
			self.ui.scene.addItem(roomList[id_room].box)
			self.ui.scene.addItem(roomList[id_room].text)
			self.drawAll()
			id_room = id_room + 1
			roomDialog.close()

	def deleteRoom(self, index):
		global id_room
		global id_exit
		global exitList
		global roomList
		self.ui.scene.removeItem(roomList[index].box)
		self.ui.scene.removeItem(roomList[index].text)
		id_room = id_room - 1
		deleted = True
		while deleted:
			for x in xrange(len(exitList)): # First round, delete all sources
				if exitList[x].source == roomList[index].id:
					self.ui.scene.removeItem(exitList[x].line)
					del exitList[x]
					id_exit = id_exit - 1
					break
				else:
					deleted = False
			if not exitList:
				deleted = False
		for x in xrange(len(exitList)): # Next round, fix all destinations
			if exitList[x].dest == roomList[index].id: # The exits still exists, but without destination
				exitList[x].dest = -1
		del roomList[index]
		self.drawAll()

	def openExit(self):
		exitDialog = editExit(self)
		exitDialog.setWindowTitle("New Exit")
		exitDialog.setData()
		if exitDialog.exec_():
			global exitList
			global id_exit
			exitList.append(Exit(exitDialog.le.text(), id_exit, exitDialog.rDict[str(exitDialog.combo3.currentText())]))
			if exitDialog.checkBox.isChecked():
				exitList[id_exit].twoWay = True
				exitList[id_exit].returnName = exitDialog.le2.text()
			exitList[id_exit].dest = exitDialog.rDict[str(exitDialog.combo4.currentText())]
			exitList[-1].desc = exitDialog.te1.toPlainText()
			exitList[-1].returnDesc = exitDialog.te2.toPlainText()
			for x in xrange(exitDialog.list1.count()):
				exitList[-1].alias.append(exitDialog.list1.item(x).text())
			for x in xrange(exitDialog.list2.count()):
				exitList[-1].returnAlias.append(exitDialog.list2.item(x).text())
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

	def editExitProperties(self, index):
		editDialog = editExit()
		editDialog.setData()
		editDialog.fillData(index)
		if editDialog.exec_():
			global exitList
			exitList[index].name = editDialog.le.text()
			exitList[index].returnName = editDialog.le2.text()
			if editDialog.checkBox.isChecked():
				exitList[index].twoWay = True
			else:
				exitList[index].twoWay = False
			exitList[index].dest = editDialog.rDict[str(editDialog.combo4.currentText())]
			exitList[index].source = editDialog.rDict[str(editDialog.combo3.currentText())]
			exitList[index].desc = editDialog.te1.toPlainText()
			exitList[index].returnDesc = editDialog.te2.toPlainText()
			exitList[index].alias = []
			exitList[index].returnAlias = []
			for x in xrange(editDialog.list1.count()):
				exitList[index].alias.append(editDialog.list1.item(x).text())
			for x in xrange(editDialog.list2.count()):
				exitList[index].returnAlias.append(editDialog.list2.item(x).text())

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
	app = QtGui.QApplication(sys.argv)
	window = Main()
	window.show()
	sys.exit(app.exec_())
