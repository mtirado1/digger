# -*- coding: utf-8 -*-


import sys
import math
import xml.dom.minidom
from xml.dom.minidom import parse
from PyQt4 import QtCore, QtGui
from diggerUi import *
from mush import *
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
		self.ui.actionExportToFile.triggered.connect(lambda: exportCodeToFile(self.fileName))
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

		self.actionKeyCopy = QtGui.QAction(self)
		self.actionKeyCopy.setShortcut("Ctrl+C")
		self.addAction(self.actionKeyCopy)
		self.actionKeyPaste = QtGui.QAction(self)
		self.actionKeyPaste.setShortcut("Ctrl+V")
		self.addAction(self.actionKeyPaste)


		self.actionKeyPaste.triggered.connect(lambda: self.pasteRoom(self.ui.graphicsView.posX, self.ui.graphicsView.posY))
		self.actionKeyCopy.triggered.connect(lambda: self.copyRoom(self.ui.graphicsView.selectedRoom))

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


		self.copyID = -1 # No room selected

	def toggleText(self):
		for room in roomList:
			self.drawRoom(room)

	def readMapNode(self, element):
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
			id = findNewId(labelList)
			labelList[id] = Label(load_label_text, id, load_label_x, load_label_y)
			self.ui.scene.addItem(labelList[id].text)
			self.ui.scene.addItem(labelList[id].box)
			labelList[id].box.move_restrict_rect = QRectF(0, 0, load_map_width, load_map_height)
		def readRoomNode(element):
			load_room_id = int(element.getAttribute("id"))
			load_room_x = int(element.getAttribute("x"))
			load_room_y = int(element.getAttribute("y"))
			load_room_bcolor = element.getAttribute("bcolor")
			load_room_center = int(element.getAttribute("size"))
			load_room_name = getText(element.getElementsByTagName("name")[0])
			load_room_desc = ""
			load_room_code = []
			if element.getElementsByTagName("description"):
				load_room_desc = getText(element.getElementsByTagName("description")[0])
			for i in element.getElementsByTagName("code"):
				load_room_code.append(getText(i))
			roomList[load_room_id] = Room(load_room_name, load_room_id, self)
			roomList[load_room_id].desc = mushUnEscape(load_room_desc)
			roomList[load_room_id].x = load_room_x
			roomList[load_room_id].y = load_room_y
			roomList[load_room_id].bColor = load_room_bcolor
			roomList[load_room_id].center = load_room_center
			roomList[load_room_id].size = (load_room_center * 2) + 1
			roomList[load_room_id].code = load_room_code
			self.ui.scene.addItem(roomList[load_room_id].box)
			roomList[load_room_id].box.move_restrict_rect = QRectF(0, 0, load_map_width, load_map_height)
			self.ui.scene.addItem(roomList[load_room_id].text)

		def readExitNode(element):
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
			exitList[load_exit_id] = Exit(load_exit_name, load_exit_source)
			exitList[load_exit_id].alias = ";".join(load_exit_alias)
			exitList[load_exit_id].dest = load_exit_dest
			exitList[load_exit_id].desc = mushUnEscape(load_exit_desc)
			self.ui.scene.addItem(exitList[load_exit_id].line)

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
		roomList.clear()
		exitList.clear()
		labelList.clear()
		self.ui.scene.clear()
		DOMTree = xml.dom.minidom.parse(str(fname))
		root = DOMTree.documentElement
		if root.tagName != "DIGGER":
			raise ValueError, "not a Digger XML file"
			return 1
		maps = root.getElementsByTagName("map")[0]
		self.readMapNode(maps)
		self.drawAll()
		return 0

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
				saveToFile(fname, self, roomList, exitList, labelList)
		else:
			fname = self.fileName
			saveToFile(fname, self, roomList, exitList, labelList)
	def saveFileAs(self):
		fname = QFileDialog.getSaveFileName(self, 'Save As', '/', "XML Files (*.xml)")
		if fname:
			self.fileName = fname
			self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))
			saveToFile(fname, self, roomList, exitList, labelList)
			self.isNewFile = 0

	def viewAbout(self):
		QMessageBox.about(self, "About Digger", """<b>Digger</b> v %s<p>Copyright &copy; 2016 Martin Tirado. All rights reserved. <p> This program can be used to design MUSH words through a graphical interface. <p> Python %s - Qt %s - PyQt %s on %s <p> Hosted on <a href='https://github.com/mtirado1/digger'> Github </a>""" % (diggerconf.version, platform.python_version(), QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

	def setOptions(self):
		optionsDialog = optionsClass(self)
		optionsDialog.setData()
		if optionsDialog.exec_():
			self.bColor = optionsDialog.bColor.name()
			self.ui.scene.setBackgroundBrush(optionsDialog.bColor)
			self.roomBColor = optionsDialog.rColor.name()
			self.ui.scene.setSceneRect(QRectF(0, 0, optionsDialog.sp.value(), optionsDialog.sp2.value()))
			for x, room in roomList.iteritems():
				room.box.move_restrict_rect = QRectF(0, 0, self.ui.scene.width(), self.ui.scene.height())
			for x, label in labelList.iteritems():
				label.box.move_restric_rect = QRectF(0, 0, self.ui.scene.width(), self.ui.scene.height())

	def exportDump(self):
		exportWindow = exportClass(self)
		exportWindow.exportAll(self.fileName)
		exportWindow.show()

	def newFile(self): # New Map
		self.fileName = "Untitled"
		self.bColor = diggerconf.mapColor
		self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))
		self.ui.scene.setBackgroundBrush(QColor(self.bColor))
		self.isNewFile = 1
		roomList.clear()
		exitList.clear()
		labelList.clear()
		self.ui.scene.clear()

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

	def drawRoom(self, id):
		roomList[id].box.setPos(roomList[id].x, roomList[id].y)

		roomString = "<p><b>" + roomList[id].name + "</b>"
		roomString += "<br />Exits:<br />"
		for i, k in exitList.iteritems():
			if k.source == id:
				coord_a = roomList[id].x + roomList[id].center
				coord_b = roomList[id].y + roomList[id].center
				if k.dest == -1:
					coord_c = coord_a + 2 * roomList[id].center
					coord_d = coord_b + 2 * roomList[id].center
				else:
					coord_c = k.line.line().x2()
					coord_d = k.line.line().y2()
				k.line.setLine(coord_a, coord_b, coord_c, coord_d)
				roomString += Qt.escape(k.name) + "<br />"
			elif k.dest == id:
				coord_c = roomList[id].x + roomList[id].center
				coord_d = roomList[id].y + roomList[id].center
				coord_a = k.line.line().x1()
				coord_b = k.line.line().y1()
				k.line.setLine(coord_a, coord_b, coord_c, coord_d)
		if self.ui.actionToggleText.isChecked():
			roomList[id].text.setHtml(roomString + "</p>")
		else:
			roomList[id].text.setHtml("")
		roomList[id].text.setPos(QPointF(roomList[id].x + roomList[id].center + 2 - (roomList[id].text.boundingRect().width() / 2), roomList[id].y + roomList[id].size + 5))
		roomList[id].box.setBrush(QColor(roomList[id].bColor))
		roomList[id].box.setRect(0, 0, roomList[id].size, roomList[id].size)
		roomList[id].box.setZValue(1)


	def drawExit(self, key):
		exit = exitList[key]
		roomSource = roomList[exitList[key].source]


		coord_a = roomSource.x + roomSource.center
		coord_b = roomSource.y + roomSource.center
		if exit.dest == -1:
			coord_c = coord_a + 2 * roomSource.center
			coord_d = coord_b + 2 * roomSource.center
		else:
			roomDest = roomList[exitList[key].dest]
			coord_c = roomDest.x + roomDest.center
			coord_d = roomDest.y + roomDest.center
		exit.line.setLine(coord_a, coord_b, coord_c, coord_d)
		exit.line.setZValue(0)

	def drawLabel(self, id):
		labelList[id].text.setZValue(10)
		labelList[id].box.setZValue(9)
		labelList[id].text.setPos(labelList[id].x, labelList[id].y)
		labelList[id].box.setPos(labelList[id].x, labelList[id].y)

	def digRoom(self, x_, y_):
		roomDialog = newRoom(self)
		if roomDialog.exec_():
			if roomDialog.le.text() == "":
				return
			id_ = findNewId(roomList)
			roomList[id_] = Room(roomDialog.le.text(), id_, self)
			roomList[id_].x = x_
			roomList[id_].y = y_
			roomList[id_].bColor = self.roomBColor
			roomList[id_].box.move_restrict_rect = QRectF(0, 0, self.ui.scene.width(), self.ui.scene.height())
			for codeLine in diggerconf.roomCode:
				roomList[id_].code.append(str(codeLine))
			self.ui.scene.addItem(roomList[id_].box)
			self.ui.scene.addItem(roomList[id_].text)
			self.drawRoom(id_)
			self.updateStatusRoom()

	def copyRoom(self, id_):
		self.copyID = id_

	def pasteRoom(self, x_, y_): # same as digRoom, but with the properties of another room
		if self.copyID == -1:
			return
		id = findNewId(roomList)
		room = roomList[self.copyID]
		roomList[id] = Room(room.name, id, self)
		roomList[id].desc = room.desc
		roomList[id].size = room.size
		roomList[id].center = room.center
		roomList[id].x = x_
		roomList[id].y = y_
		roomList[id].bColor = room.bColor
		roomList[id].box.move_restrict_rect = QRectF(0, 0, self.ui.scene.width(), self.ui.scene.height())
		roomList[id].code = list(room.code)
		self.ui.scene.addItem(roomList[id].box)
		self.ui.scene.addItem(roomList[id].text)
		self.drawRoom(id)
		self.updateStatusRoom()


	def deleteRoom(self, index):
		self.ui.scene.removeItem(roomList[index].box)
		self.ui.scene.removeItem(roomList[index].text)
		deleted = True
		while deleted:
			for x in exitList: # First round, delete all sources
				deleted = False
				if exitList[x].source == index:
					self.ui.scene.removeItem(exitList[x].line)
					del exitList[x]
					deleted = True
					break
			if not exitList:
				deleted = False
		for x in exitList: # Next round, fix all destinations
			if exitList[x].dest == index: # The exits still exists, but without destination
				exitList[x].dest = -1
				self.drawExit(x)
		del roomList[index]
		self.updateStatusRoom()
		self.updateStatusExit()

	def openExit(self):
		if len(roomList) == 0:
			return
		exitDialog = editExit(self)
		exitDialog.setWindowTitle("New Exit")
		exitDialog.setData()
		if exitDialog.exec_():
			id_ = findNewId(exitList)
			exitList[id_] = Exit(exitDialog.le.text(), exitDialog.rDict[str(exitDialog.combo1.currentText())])
			exitList[id_].dest = exitDialog.rDict[str(exitDialog.combo2.currentText())]
			exitList[id_].desc = exitDialog.te1.toPlainText()

			if exitDialog.le.text() not in diggerconf.aliasDict: # Don't override alias tab
				items = []
				for x in xrange(exitDialog.list1.count()):
					items.append(exitDialog.list1.item(x).text())
				exitList[id_].alias = ";".join(items)

			self.ui.scene.addItem(exitList[id_].line)
			self.drawExit(id_)
			self.drawRoom(exitList[id_].source)
			self.drawRoom(exitList[id_].dest)
			self.updateStatusExit()

	def openExitName(self, source, destination):
		exitDialog = newExitName()
		if exitDialog.exec_():
			id_ = findNewId(exitList)
			exitList[id_] = Exit(exitDialog.le.text(), source)
			exitList[id_].dest = destination
			self.drawExit(id_)
			self.ui.scene.addItem(exitList[id_].line)
			if exitDialog.checkBox.isChecked():
				id = findNewId(exitList)
				exitList[id] = Exit(exitDialog.le2.text(), destination)
				exitList[id].dest = source
				self.drawExit(id)
				self.ui.scene.addItem(exitList[id].line)
		self.drawRoom(source)
		self.drawRoom(destination)
		self.updateStatusExit()

	def openExitChain(self):
		exitDialog = newExitName()
		if exitDialog.exec_():
			for x in range(len(self.ui.graphicsView.chainRoom) - 1): # Skip the last room
				source = self.ui.graphicsView.chainRoom[x]
				destination = self.ui.graphicsView.chainRoom[x+1]
				id = findNewId(exitList)
				exitList[id] = Exit(exitDialog.le.text(), source)
				exitList[id].dest = destination
				self.drawExit(id)
				self.ui.scene.addItem(exitList[id].line)
				if exitDialog.checkBox.isChecked():
					id = findNewId(exitList)
					exitList[id] = Exit(exitDialog.le2.text(), destination)
					exitList[id].dest = source
					self.drawExit(id)
					self.ui.scene.addItem(exitList[id].line)
				self.drawRoom(self.ui.graphicsView.chainRoom[x])
				self.drawRoom(self.ui.graphicsView.chainRoom[x+1])
			self.updateStatusExit()

	def editRoomProperties(self, index):
		editDialog = editRoom()
		editDialog.setData(index)
		if editDialog.exec_():
			roomList[index].name=editDialog.le.text()
			roomList[index].desc=editDialog.te.toPlainText()
			roomList[index].x=int(editDialog.le2.text())
			roomList[index].y=int(editDialog.le3.text())
			roomList[index].size = (2 * editDialog.sp.value()) + 1
			roomList[index].center = editDialog.sp.value()
			if editDialog.color.isValid():
				roomList[index].bColor = editDialog.color.name()
			codeList = editDialog.te2.toPlainText().split("\n")
			roomList[index].code = []
			for codeLine in codeList:
				roomList[index].code.append(str(codeLine))
			# Draw ONLY the modified room
			self.drawRoom(index)
			editDialog.close()

	def editExitProperties(self, index):
		editDialog = editExit()
		editDialog.setData()
		editDialog.fillData(index)
		if editDialog.exec_():
			exitList[index].name = editDialog.le.text()
			exitList[index].source = editDialog.rDict[str(editDialog.combo1.currentText())]
			exitList[index].dest = editDialog.rDict[str(editDialog.combo2.currentText())]
			exitList[index].desc = editDialog.te1.toPlainText()
			items = []
			for x in xrange(editDialog.list1.count()):
				items.append(str(editDialog.list1.item(x).text()))
			exitList[index].alias = ";".join(items)

			# Draw ONLY the modified exit and the affected rooms
			self.drawExit(index)
			self.drawRoom(exitList[index].source)
			self.drawRoom(exitList[index].dest)

	def addLabel(self, x_, y_):
		labelDialog = addLabel()
		if labelDialog.exec_():
			id = findNewId(labelList)
			labelList[id] = Label(labelDialog.le.text(), id, x_, y_)
			self.ui.scene.addItem(labelList[id].text)
			self.ui.scene.addItem(labelList[id].box)
			labelList[id].box.move_restrict_rect = QRectF(0, 0, self.ui.scene.width(), self.ui.scene.height())
			self.drawLabel(id)
			labelDialog.close()
			self.updateStatusLabel()

	def deleteLabel(self, id_):
		self.ui.scene.removeItem(labelList[id_].text)
		self.ui.scene.removeItem(labelList[id_].box)
		del labelList[id_]
		self.updateStatusLabel()

	def editLabelProperties(self, id_):
		objectClicked = id_
		editDialog = addLabel()
		editDialog.setWindowTitle("Edit Label")
		editDialog.le.setText(labelList[objectClicked].normalText)
		if editDialog.exec_():
			labelList[objectClicked].setText(editDialog.le.text())
			labelList[objectClicked].box.setRect(0, 0, labelList[objectClicked].text.boundingRect().width(), labelList[objectClicked].text.boundingRect().height())

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	diggerconf.loadConfigFile(len(sys.argv) > 2)
	window = Main()
	if len(sys.argv) > 2:
		if sys.argv[1] == "--export" or sys.argv[1] == "-e":
			if not os.path.exists(sys.argv[2]):
				print "Error: File not found."
				sys.exit()
			fname = sys.argv[2]
			if window.populateFromDOM(fname):
				sys.exit()
			window.fileName = fname
			print generateCode(window.fileName, roomList, exitList, labelList)
	else:
		window.show()
		sys.exit(app.exec_())
