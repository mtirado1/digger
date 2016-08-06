# -*- coding: utf-8 -*-


import sys
import math
import xml.dom.minidom
from xml.dom.minidom import parse
from PyQt4 import QtCore, QtGui
from diggerUi import *
from diggerfuncs import __version__
import platform
import diggerconf


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
		self.ui.actionExportToFile.triggered.connect(exportCodeToFile)
		self.ui.actionNew.triggered.connect(self.newFile)
		self.ui.actionOptions.triggered.connect(self.setOptions)
		self.ui.actionAbout.triggered.connect(self.viewAbout)
		self.ui.actionOpen.triggered.connect(self.openFile)
		self.ui.actionSave.triggered.connect(self.saveFile)
		self.ui.actionToggleText.triggered.connect(self.toggleText)
		self.ui.actionResetZoom.triggered.connect(self.ui.graphicsView.resetZoom)
		self.ui.actionSaveAs.triggered.connect(self.saveFileAs)
		self.ui.actionNewRoom.triggered.connect(lambda: self.digRoom(self.ui.scene.width()/2, self.ui.scene.height()/2))
		self.ui.actionNewExit.triggered.connect(self.openExit)
		self.ui.actionNewLabel.triggered.connect(lambda: self.addLabel(self.ui.scene.width()/2, self.ui.scene.height()/2))

		self.statusRoom = QLabel("")
		self.ui.statusbar.addWidget(self.statusRoom)
		self.statusExit = QLabel("")
		self.ui.statusbar.addWidget(self.statusExit)
		self.statusLabel = QLabel("")
		self.ui.statusbar.addWidget(self.statusLabel)
		self.isNewFile = 1
		self.fileName = "Untitled"
		self.bColor = diggerconf.mapColor
		self.ui.scene.setBackgroundBrush(QColor(self.bColor))
		self.roomBColor = diggerconf.roomColor
		self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))

	def toggleText(self):
		for room in roomList:
			self.drawRoom(room)

	def readMapNode(self, element):
		global roomList
		global exitList
		global labelList
		load_map_width = 0
		load_map_height = 0
		def getText(element):
			if element.childNodes:
				return element.childNodes[0].data
			return "" # Empty tag

		def readLabelNode(element):
			load_label_x = int(element.getAttribute("x"))
			load_label_y = int(element.getAttribute("y"))
			load_label_text = getText(element)
			labelList.append(Label(load_label_text, load_label_x, load_label_y))
			self.ui.scene.addItem(labelList[-1].text)
			self.ui.scene.addItem(labelList[-1].box)
			labelList[-1].box.move_restrict_rect = QRectF(0, 0, load_map_width, load_map_height)
		def readRoomNode(element):
			load_room_id = int(element.getAttribute("id"))
			load_room_x = int(element.getAttribute("x"))
			load_room_y = int(element.getAttribute("y"))
			load_room_bcolor = element.getAttribute("bcolor")
			load_room_name = getText(element.getElementsByTagName("name")[0])
			load_room_desc = ""
			load_room_code = []
			if element.getElementsByTagName("description"):
				load_room_desc = getText(element.getElementsByTagName("description")[0])
			for i in element.getElementsByTagName("code"):
				load_room_code.append(getText(i))
			roomList.append(Room(load_room_name, load_room_id, self))
			roomList[-1].desc = mushUnEscape(load_room_desc)
			roomList[-1].x = load_room_x
			roomList[-1].y = load_room_y
			roomList[-1].bColor = load_room_bcolor
			roomList[-1].code = load_room_code
			self.ui.scene.addItem(roomList[-1].box)
			roomList[-1].box.move_restrict_rect = QRectF(0, 0, load_map_width, load_map_height)
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
			self.ui.scene.setSceneRect(QRectF(0, 0, optionsDialog.sp.value(), optionsDialog.sp2.value()))
			global roomList
			global labelList
			for x in roomList:
				x.box.move_restrict_rect = QRectF(0, 0, self.ui.scene.width(), self.ui.scene.height())
			for x in labelList:
				x.box.move_restric_rect = QRectF(0, 0, self.ui.scene.width(), self.ui.scene.height())

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

	def getPosOfRoom(self, room_id_):
		for x in roomList:
			if x.id == room_id_:
				return x
		return None

	def updateStatusRoom(self):
		if len(roomList) > 0:
			self.statusRoom.setText("Rooms: " + str(len(roomList)))
		else:
			self.statusRoom.setText("")

	def updateStatusExit(self):
		if len(exitList) > 0:
			self.statusExit.setText("Exits: " + str(len(exitList)))
		else:
			self.statusExit.setText("")

	def updateStatusLabel(self):
		if len(labelList) > 0:
			self.statusLabel.setText("Labels: " + str(len(labelList)))
		else:
			self.statusLabel.setText("")

	def drawAll(self): # Draw all items, only used when opening files
		for r in roomList:
			self.drawRoom(r)
		for e in exitList:
			self.drawExit(e)
		for l in labelList:
			self.drawLabel(l)
		self.updateStatusRoom()
		self.updateStatusExit()
		self.updateStatusLabel()

	def drawRoom(self, room):
		if not room:
			return
		global roomList
		room.box.setPos(room.x, room.y)
		room.box.index=roomList.index(room)

		roomString = "<p><b>" + room.name + "</b>"
		roomString += "<br />Exits:<br />"
		for k in exitList:
			if k.source == room.id:
				coord_a = room.x + diggerconf.roomCenter
				coord_b = room.y + diggerconf.roomCenter
				if k.dest == -1:
					coord_c = coord_a + 2 * diggerconf.roomCenter
					coord_d = coord_b + 2 * diggerconf.roomCenter
				else:
					coord_c = k.line.line().x2()
					coord_d = k.line.line().y2()
				k.line.setLine(coord_a, coord_b, coord_c, coord_d)
				roomString += Qt.escape(k.name) + "<br />"
			elif k.dest == room.id:
				coord_c = room.x + diggerconf.roomCenter
				coord_d = room.y + diggerconf.roomCenter
				coord_a = k.line.line().x1()
				coord_b = k.line.line().y1()
				k.line.setLine(coord_a, coord_b, coord_c, coord_d)
		if self.ui.actionToggleText.isChecked():
			room.text.setHtml(roomString + "</p>")
		else:
			room.text.setHtml("")
		room.text.setPos(QPointF(room.x + diggerconf.roomCenter + 2 - (room.text.boundingRect().width() / 2), room.y + diggerconf.roomSize + 5))
		room.box.setBrush(QColor(room.bColor))
		room.box.setRect(0, 0, diggerconf.roomSize, diggerconf.roomSize)
		room.box.setZValue(1)


	def drawExit(self, exit):
		global exitList

		coord_a = self.getPosOfRoom(exit.source).x + diggerconf.roomCenter
		coord_b = self.getPosOfRoom(exit.source).y + diggerconf.roomCenter
		if exit.dest == -1:
			coord_c = coord_a + 2 * diggerconf.roomCenter
			coord_d = coord_b + 2 * diggerconf.roomCenter
		else:
			coord_c = self.getPosOfRoom(exit.dest).x + diggerconf.roomCenter
			coord_d = self.getPosOfRoom(exit.dest).y + diggerconf.roomCenter
		exit.line.setLine(coord_a, coord_b, coord_c, coord_d)
		exit.line.setZValue(0)

	def drawLabel(self, label):
		global labelList
		label.box.index = labelList.index(label)
		label.text.setZValue(10)
		label.box.setZValue(9)
		label.text.setPos(label.x, label.y)
		label.box.setPos(label.x, label.y)

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
			for codeLine in diggerconf.roomCode:
				roomList[-1].code.append(str(codeLine))
			self.ui.scene.addItem(roomList[-1].box)
			self.ui.scene.addItem(roomList[-1].text)
			self.drawRoom(roomList[-1])
			self.updateStatusRoom()

	def deleteRoom(self, index):
		global exitList
		global roomList
		self.ui.scene.removeItem(roomList[index].box)
		self.ui.scene.removeItem(roomList[index].text)
		deleted = True
		while deleted:
			for x in xrange(len(exitList)): # First round, delete all sources
				deleted = False
				if exitList[x].source == roomList[index].id:
					self.ui.scene.removeItem(exitList[x].line)
					del exitList[x]
					deleted = True
					break
			if not exitList:
				deleted = False
		for x in xrange(len(exitList)): # Next round, fix all destinations
			if exitList[x].dest == roomList[index].id: # The exits still exists, but without destination
				exitList[x].dest = -1
				self.drawExit(exitList[x])
		del roomList[index]
		for x in xrange(len(roomList)):
			roomList[x].box.index = x
		self.updateStatusRoom()
		self.updateStatusExit()

	def openExit(self):
		exitDialog = editExit(self)
		exitDialog.setWindowTitle("New Exit")
		exitDialog.setData()
		if exitDialog.exec_():
			global exitList

			exitList.append(Exit(exitDialog.le.text(), findNewId(exitList), exitDialog.rDict[str(exitDialog.combo1.currentText())]))
			exitList[-1].dest = exitDialog.rDict[str(exitDialog.combo2.currentText())]
			exitList[-1].desc = exitDialog.te1.toPlainText()

			if exitDialog.le.text() not in diggerconf.aliasDict: # Don't override alias tab
				for x in xrange(exitDialog.list1.count()):
					exitList[-1].alias.append(exitDialog.list1.item(x).text())

			self.ui.scene.addItem(exitList[-1].line)
			self.drawExit(exitList[-1])
			self.drawRoom(self.getPosOfRoom(exitList[-1].source))
			self.drawRoom(self.getPosOfRoom(exitList[-1].dest))
			self.updateStatusExit()

	def openExitName(self, source, destination):
		global roomList
		global exitList
		exitDialog = newExitName()
		if exitDialog.exec_():
			exitList.append(Exit(exitDialog.le.text(), findNewId(exitList), source))
			exitList[-1].dest = destination
			self.drawExit(exitList[-1])
			self.ui.scene.addItem(exitList[-1].line)
			if exitDialog.checkBox.isChecked():
				exitList.append(Exit(exitDialog.le2.text(), findNewId(exitList), destination))
				exitList[-1].dest = source
				self.drawExit(exitList[-1])
				self.ui.scene.addItem(exitList[-1].line)
		self.drawRoom(self.getPosOfRoom(source))
		self.drawRoom(self.getPosOfRoom(destination))
		self.updateStatusExit()

	def editRoomProperties(self, index):
		editDialog = editRoom()
		editDialog.setData(index)
		if editDialog.exec_():
			global roomList
			roomList[index].name=editDialog.le.text()
			roomList[index].desc=editDialog.te.toPlainText()
			roomList[index].x=int(editDialog.le2.text())
			roomList[index].y=int(editDialog.le3.text())

			codeList = editDialog.te2.toPlainText().split("\n")
			roomList[index].code = []
			for codeLine in codeList:
				roomList[index].code.append(str(codeLine))
			# Draw ONLY the modified room
			self.drawRoom(roomList[index])
			editDialog.close()

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
			# Draw ONLY the modified exit and the affected rooms
			self.drawExit(exitList[index])
			self.drawRoom(self.getPosOfRoom(exitList[index].source))
			self.drawRoom(self.getPosOfRoom(exitList[index].dest))

	def addLabel(self, x_, y_):
		labelDialog = addLabel()
		if labelDialog.exec_():
			global labelList
			newIndex = len(labelList)
			labelList.append(Label(labelDialog.le.text(), x_, y_))
			labelList[-1].box.index = newIndex
			self.ui.scene.addItem(labelList[-1].text)
			self.ui.scene.addItem(labelList[-1].box)
			labelList[-1].box.move_restrict_rect = QRectF(0, 0, self.ui.scene.width(), self.ui.scene.height())
			self.drawLabel(labelList[-1])
			labelDialog.close()
			self.updateStatusLabel()

	def deleteLabel(self, id_):
		global labelList
		self.ui.scene.removeItem(labelList[id_].text)
		self.ui.scene.removeItem(labelList[id_].box)
		del labelList[id_]
		self.updateStatusLabel()

	def deleteLabelProperties(self, id_):
		editDialog = addLabel()
		editDialog.setWindowTitle("Edit Label")
		editDialog.le.setText(labelList[objectClicked].normalText)
		if editDialog.exec_():
			labelList[objectClicked].setText(editDialog.le.text())
			labelList[objectClicked].box.setRect(0, 0, labelList[objectClicked].text.boundingRect().width(), labelList[objectClicked].text.boundingRect().height())

if __name__ == "__main__":
	diggerconf.loadConfigFile()
	app = QtGui.QApplication(sys.argv)
	window = Main()
	window.show()
	sys.exit(app.exec_())
