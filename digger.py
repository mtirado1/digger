# -*- coding: utf-8 -*-


import sys
import math
import xml.dom.minidom
from xml.dom.minidom import parse
from PyQt4 import QtCore, QtGui
from diggerUi import *
from diggerfuncs import __version__
import platform



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
		self.ui.actionSaveAs.triggered.connect(self.saveFileAs)
		self.ui.actionNewRoom.triggered.connect(lambda: self.digRoom(self.ui.scene.width()/2, self.ui.scene.height()/2))
		self.ui.actionNewExit.triggered.connect(lambda: self.openExit(self.ui.scene.width()/2, self.ui.scene.height()/2))
		self.ui.actionNewLabel.triggered.connect(lambda: self.addLabel(self.ui.scene.width()/2, self.ui.scene.height()/2))
		
		self.isNewFile = 1
		self.fileName = "Untitled"
		self.bColor = "#FFFFFF"
		self.roomBColor = "#FF0000"
		self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))


	def toggleText(self):
		self.drawAll()

	def readMapNode(self, element):
		global roomList
		global exitList
		global labelList

		def getText(element):
			return element.childNodes[0].data

		def readLabelNode(element):
			load_label_x = int(element.getAttribute("x"))
			load_label_y = int(element.getAttribute("y"))
			load_label_text = getText(element)
			labelList.append(Label(load_label_text, load_label_x, load_label_y))
			self.ui.scene.addItem(labelList[-1].text)
			self.ui.scene.addItem(labelList[-1].box)
		def readRoomNode(element):
			load_room_id = int(element.getAttribute("id"))
			load_room_x = int(element.getAttribute("x"))
			load_room_y = int(element.getAttribute("y"))
			load_room_bcolor = element.getAttribute("bcolor")
			load_room_name = getText(element.getElementsByTagName("name")[0])
			load_room_desc = ""
			if element.getElementsByTagName("description"):
				load_room_desc = getText(element.getElementsByTagName("description")[0])

			roomList.append(Room(load_room_name, load_room_id, self))
			roomList[-1].desc = mushUnEscape(load_room_desc)
			roomList[-1].x = load_room_x
			roomList[-1].y = load_room_y
			roomList[-1].bColor = load_room_bcolor
			self.ui.scene.addItem(roomList[-1].box)
			self.ui.scene.addItem(roomList[-1].text)

		def readExitNode(element):
			global exitList
			load_exit_id = int(element.getAttribute("id"))
			load_exit_source = int(element.getAttribute("source"))
			load_exit_dest = int(element.getAttribute("destination"))
			load_exit_alias = []
			load_exit_name = getText(element.getElementsByTagName("name")[0])
			load_exit_desc = ""
			if element.getElementsByTagName("description"):
				load_exit_desc = getText(element.getElementsByTagName("description")[0])
			for i in element.getElementsByTagName("alias"):
				load_exit_alias.append(getText(i))
			exitList.append(Exit(load_exit_name, load_exit_id, load_exit_source))
			exitList[-1].alias = load_exit_alias
			exitList[-1].dest = load_exit_dest
			exitList[-1].desc = mushUnEscape(load_exit_desc)
			self.ui.scene.addItem(exitList[-1].line)

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
		self.ui.scene.setSceneRect(0, 0, load_map_width, load_map_height)

	def populateFromDOM(self, fname):
		global roomList
		global exitList
		global labelList
		del roomList[:]
		del exitList[:]
		del labelList[:]
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
			self.isNewFile = 0


	def saveFile(self):
		if self.isNewFile == 1:
			fname = QFileDialog.getSaveFileName(self, 'Save file', '/', "XML Files (*.xml)")
			if fname:
				self.fileName = fname
				self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))
				self.isNewFile = 0
				saveToFile(fname, self)
		else:
			fname = self.fileName
			saveToFile(fname, self)
	def saveFileAs(self):
		fname = QFileDialog.getSaveFileName(self, 'Save As', '/', "XML Files (*.xml)")
		if fname:
			self.fileName = fname
			self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))
			saveToFile(fname, self)
			self.isNewFile = 0


	def isRGB(self, number):
		check = 1
		for x in list(number[1:]):
			if (ord(x) >= 48 and ord(x) <= 57) or ((ord(x) >= 65 and ord(x) <= 70) or (ord(x) >= 97 and ord(x) <= 102)):
				check = check * 1
			else:
				check = 0
		return check and (number[0] == '#')

	def viewAbout(self):
		global __version__
		QMessageBox.about(self, "About Digger", """<b>Digger</b> v %s<p>Copyright &copy; 2016 Martin Tirado. All rights reserved. <p> This program can be used to design MUSH words through a graphical interface. <p> Python %s - Qt %s - PyQt %s on %s <p> Hosted on <a href='https://github.com/mtirado1/digger'> Github </a>""" % (__version__, platform.python_version(), QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

	def setOptions(self):
		optionsDialog = optionsClass(self)
		optionsDialog.setData()
		if optionsDialog.exec_():
			colorString = str(optionsDialog.le3.text())
			if self.isRGB(colorString):
				self.bColor = colorString
				self.ui.scene.setBackgroundBrush(QColor(colorString))
			if self.isRGB(str(optionsDialog.le4.text())):
				self.roomBColor = str(optionsDialog.le4.text())
			if is_number(optionsDialog.le.text()) and is_number(optionsDialog.le2.text()):
				#self.resize(int(optionsDialog.le.text()), int(optionsDialog.le2.text()))
				#self.ui.graphicsView.setGeometry(QtCore.QRect(0, 0, int(optionsDialog.le.text()), int(optionsDialog.le2.text())))
				#self.ui.menubar.setGeometry(QtCore.QRect(0, 0, int(optionsDialog.le.text()), int(optionsDialog.le2.text())))
				self.ui.scene.setSceneRect(QRectF(0, 0, int(optionsDialog.le.text()), int(optionsDialog.le2.text())))
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
			if self.ui.actionToggleText.isChecked():
				roomList[j].text.setHtml(roomString + "</p>")
			else:
				roomList[j].text.setHtml("")
			roomList[j].text.setPos(QPointF(roomList[j].x + ROOM_CENTER + 2 - (roomList[j].text.boundingRect().width() / 2), roomList[j].y + ROOM_SIZE + 5))
			roomList[j].box.setBrush(QColor(roomList[j].bColor))
			roomList[j].box.setRect(0, 0, ROOM_SIZE, ROOM_SIZE)
			self.ui.scene.addItem(roomList[j].box)
			self.ui.scene.addItem(roomList[j].text)
			roomList[j].box.setZValue(1)
		for j in xrange(len(labelList)):
			labelList[j].box.index = j
			labelList[j].text.setZValue(10)
			labelList[j].box.setZValue(9)
			labelList[j].text.setPos(labelList[j].x, labelList[j].y)
			labelList[j].box.setPos(labelList[j].x, labelList[j].y)

	def digRoom(self, x_, y_):
		global roomList
		roomDialog = newRoom(self)
		if roomDialog.exec_():
			global roomList
			if roomDialog.le.text() != "":
				roomList.append(Room(roomDialog.le.text(), findNewId(roomList), self))
			roomList[-1].x = x_
			roomList[-1].y = y_
			roomList[-1].bColor = self.roomBColor
			roomList[-1].box.move_restrict_rect = QRectF(0, 0, self.ui.scene.width(), self.ui.scene.height())
			self.ui.scene.addItem(roomList[-1].box)
			self.ui.scene.addItem(roomList[-1].text)
			self.drawAll()
			roomDialog.close()

	def deleteRoom(self, index):
		global exitList
		global roomList
		self.ui.scene.removeItem(roomList[index].box)
		self.ui.scene.removeItem(roomList[index].text)
		deleted = True
		while deleted:
			for x in xrange(len(exitList)): # First round, delete all sources
				if exitList[x].source == roomList[index].id:
					self.ui.scene.removeItem(exitList[x].line)
					del exitList[x]
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
			exitList.append(Exit(exitDialog.le.text(), findNewId(exitList), exitDialog.rDict[str(exitDialog.combo1.currentText())]))
			exitList[-1].dest = exitDialog.rDict[str(exitDialog.combo2.currentText())]
			exitList[-1].desc = exitDialog.te1.toPlainText()
			for x in xrange(exitDialog.list1.count()):
				exitList[-1].alias.append(exitDialog.list1.item(x).text())
			self.ui.scene.addItem(exitList[-1].line)
			self.drawAll()
			exitDialog.close()
	def openExitName(self, source, destination):
		global roomList
		global exitList
		exitList.append(Exit("##placeholder##", findNewId(exitList), roomList[source].id)) # User will be asked for name soon
		exitList[-1].dest = destination
		self.ui.scene.addItem(exitList[-1].line)
		exitDialog = newExitName()
		if exitDialog.exec_():
			exitList[-1].name = exitDialog.le.text()
			if exitDialog.checkBox.isChecked():
				exitList.append(Exit(exitDialog.le2.text(), findNewId(exitList), roomList[destination].id))
				exitList[-1].dest = source
				self.ui.scene.addItem(exitList[-1].line)
		else:
			self.ui.scene.removeItem(exitList[-1])
			del exitList[-1]
		self.drawAll()

	def editExitProperties(self, index):
		editDialog = editExit()
		editDialog.setData()
		editDialog.fillData(index)
		if editDialog.exec_():
			global exitList
			exitList[index].name = editDialog.le.text()
			exitList[index].source = editDialog.rDict[str(editDialog.combo1.currentText())]
			exitList[index].dest = editDialog.rDict[str(editDialog.combo2.currentText())]
			exitList[index].desc = editDialog.te1.toPlainText()
			exitList[index].alias = []
			for x in xrange(editDialog.list1.count()):
				exitList[index].alias.append(editDialog.list1.item(x).text())

	def addLabel(self, x_, y_):
		labelDialog = addLabel()
		if labelDialog.exec_():
			global labelList
			newIndex = len(labelList)
			labelList.append(Label(labelDialog.le.text(), x_, y_))
			labelList[-1].box.index = newIndex
			self.ui.scene.addItem(labelList[-1].text)
			self.ui.scene.addItem(labelList[-1].box)
			self.drawAll()
			labelDialog.close()
	def deleteLabel(self, id_):
		global labelList
		self.ui.scene.removeItem(labelList[id_].text)
		self.ui.scene.removeItem(labelList[id_].box)
		del labelList[id_]
		self.drawAll()


if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	window = Main()
	window.show()
	sys.exit(app.exec_())
