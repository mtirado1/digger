# -*- coding: utf-8 -*-


import sys
from PyQt5 import QtCore, QtGui, uic
from diggerUi import *
import mush
import diggerconf
import platform
import diggerconf

try:
	_encoding = QtGui.QApplication.UnicodeUTF8
	def _translate(context, text, disambig):
		return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
	def _translate(context, text, disambig):
		return QtWidgets.QApplication.translate(context, text, disambig)


class Main(QtWidgets.QMainWindow):
	def __init__(self):
		QtWidgets.QMainWindow.__init__(self, parent = None)
		uic.loadUi('ui/digger.ui', self)

		self.resize(1080, 683)
		self.scene = QGraphicsScene(self.graphicsView)
		self.scene.setSceneRect(0, 0, diggerconf.mapWidth, diggerconf.mapHeight)
		self.graphicsView.setScene(self.scene)

		self.actionExportToFile.triggered.connect(lambda: exportCodeToFile(self.fileName))
		self.actionNewRoom.triggered.connect(lambda: self.digRoom(self.scene.width()/2, self.scene.height()/2))
		self.actionNewLabel.triggered.connect(lambda: self.addLabel(self.scene.width()/2, self.scene.height()/2))

		self.actionKeyCopy = QtWidgets.QAction(self)
		self.actionKeyCopy.setShortcut("Ctrl+C")
		self.addAction(self.actionKeyCopy)
		self.actionKeyPaste = QtWidgets.QAction(self)
		self.actionKeyPaste.setShortcut("Ctrl+V")
		self.addAction(self.actionKeyPaste)
		self.actionKeyPaste.triggered.connect(lambda: self.pasteRoom(self.graphicsView.posX, self.graphicsView.posY))
		self.actionKeyCopy.triggered.connect(lambda: self.copyRoom(self.graphicsView.selectedRoom))

		self.statusRoom = QLabel("")
		self.statusbar.addWidget(self.statusRoom)
		self.statusExit = QLabel("")
		self.statusbar.addWidget(self.statusExit)
		self.statusLabel = QLabel("")
		self.statusbar.addWidget(self.statusLabel)
		self.isNewFile = True
		self.fileName = "Untitled"
		self.bColor = diggerconf.mapColor
		self.scene.setBackgroundBrush(QColor(self.bColor))
		self.roomBColor = diggerconf.roomColor
		self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))


		self.copyID = -1 # No room selected

	def toggleText(self):
		for room in roomList:
			self.drawRoom(room)

	def loadMap(self, Map):
		self.bColor = Map.bcolor
		self.scene.setBackgroundBrush(QColor(Map.bcolor))
		self.scene.setSceneRect(0, 0, Map.width, Map.height)
		for i in Map.rooms: # Load all rooms to scene
			roomList[i] = Map.rooms[i]
			self.scene.addItem(roomList[i].box)
			roomList[i].box.move_restrict_rect = QRectF(0, 0, Map.width, Map.height)
			self.scene.addItem(roomList[i].text)

		for i in Map.exits: # Load exits
			exitList[i] = Map.exits[i]
			self.scene.addItem(exitList[i].line)

		for i in Map.labels: # Finally, load labels
			labelList[i] = Map.labels[i]
			self.scene.addItem(labelList[i].text)
			self.scene.addItem(labelList[i].box)
			labelList[i].box.move_restrict_rect = QRectF(0, 0, Map.width, Map.height)
		self.drawAll()

	def populateFromDOM(self, fname):
		roomList.clear()
		exitList.clear()
		labelList.clear()
		self.scene.clear()

		fmap = importXml(self, fname)
		self.loadMap(fmap) # Load map

	def populateFromJson(self, fname):
		roomList.clear()
		exitList.clear()
		labelList.clear()
		self.scene.clear()

		fmap = importJson(self, fname)
		self.loadMap(fmap) # Load map


	def openFile(self):
		fname = QFileDialog.getOpenFileName(self, 'Open file', '/','XML files (*.xml);;JSON files (*.json)')[0]
		if fname:
			diggerconf.exportType = fname.split('.')[-1]
			if diggerconf.exportType == 'xml':
				self.populateFromDOM(fname)
			elif diggerconf.exportType == 'json':
				self.populateFromJson(fname)
			self.fileName = fname
			self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))
			self.isNewFile = False


	def saveFile(self):
		fname = ""
		if self.isNewFile:
			if diggerconf.exportType == 'xml':
				fname = QFileDialog.getSaveFileName(self, 'Save file', '/', "XML Files (*.xml)")[0]
			elif diggerconf.exportType == 'json':
				fname = QFileDialog.getSaveFileName(self, 'Save file', '/', "JSON Files (*.json)")[0]
			if fname:
				self.fileName = fname
				self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))
				self.isNewFile = False
		else:
			fname = self.fileName
		if fname:
			if diggerconf.exportType == 'xml':
				mush.saveToXml(fname, self, roomList, exitList, labelList)
			elif diggerconf.exportType == 'json':
				mush.saveToJson(fname, self, roomList, exitList, labelList)

	def saveFileAs(self):
		fname = QFileDialog.getSaveFileName(self, 'Save As', '/', 'XML files (*.xml);;JSON files (*.json)')[0]
		if fname:
			self.fileName = fname
			extension = fname.split('.')[-1]
			self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))
			if extension == 'xml':
				mush.saveToXml(fname, self, roomList, exitList, labelList)
			if extension == 'json':
				mush.saveToJson(fname, self, roomList, exitList, labelList)
			self.isNewFile = False

	def viewAbout(self):

		text = """<b>Digger</b> v %s<p>Copyright &copy; 2017 Martin Tirado. All rights reserved. <p>
				This program can be used to design MUSH words through a graphical interface. <p>
				Python %s - Qt %s - PyQt %s on %s <p>
				Hosted on <a href='https://github.com/mtirado1/digger'> Github </a>"""
		QMessageBox.about(self, "About Digger", text % (diggerconf.version, platform.python_version(), QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

	def setOptions(self):
		optionsDialog = optionsClass(self)
		optionsDialog.setData()
		if optionsDialog.exec_():
			self.bColor = optionsDialog.bColor.name()
			self.scene.setBackgroundBrush(optionsDialog.bColor)
			self.roomBColor = optionsDialog.rColor.name()
			self.scene.setSceneRect(QRectF(0, 0, optionsDialog.sp.value(), optionsDialog.sp2.value()))
			for x, room in roomList.items():
				room.box.move_restrict_rect = QRectF(0, 0, self.scene.width(), self.scene.height())
			for x, label in labelList.items():
				label.box.move_restric_rect = QRectF(0, 0, self.scene.width(), self.scene.height())

	def exportDump(self):
		exportWindow = exportClass(self)
		exportWindow.exportAll(self.fileName)
		exportWindow.show()

	def newFile(self): # New Map
		self.fileName = "Untitled"
		self.bColor = diggerconf.mapColor
		self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))
		self.scene.setBackgroundBrush(QColor(self.bColor))
		self.isNewFile = True
		roomList.clear()
		exitList.clear()
		labelList.clear()
		self.scene.clear()

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
		for i, k in exitList.items():
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
				roomString += escape(k.name) + "<br />"
			elif k.dest == id:
				coord_c = roomList[id].x + roomList[id].center
				coord_d = roomList[id].y + roomList[id].center
				coord_a = k.line.line().x1()
				coord_b = k.line.line().y1()
				k.line.setLine(coord_a, coord_b, coord_c, coord_d)
		if self.actionToggleText.isChecked():
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
			roomList[id_].box.move_restrict_rect = QRectF(0, 0, self.scene.width(), self.scene.height())
			for codeLine in diggerconf.roomCode:
				roomList[id_].code.append(str(codeLine))
			self.scene.addItem(roomList[id_].box)
			self.scene.addItem(roomList[id_].text)
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
		roomList[id].box.move_restrict_rect = QRectF(0, 0, self.scene.width(), self.scene.height())
		roomList[id].code = list(room.code)
		self.scene.addItem(roomList[id].box)
		self.scene.addItem(roomList[id].text)
		self.drawRoom(id)
		self.updateStatusRoom()


	def deleteRoom(self, index):
		self.scene.removeItem(roomList[index].box)
		self.scene.removeItem(roomList[index].text)
		deleted = True
		while deleted:
			for x in exitList: # First round, delete all sources
				deleted = False
				if exitList[x].source == index:
					self.scene.removeItem(exitList[x].line)
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
				for x in range(exitDialog.list1.count()):
					items.append(exitDialog.list1.item(x).text())
				exitList[id_].alias = ";".join(items)

			self.scene.addItem(exitList[id_].line)
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
			self.scene.addItem(exitList[id_].line)
			if exitDialog.checkBox.isChecked():
				id = findNewId(exitList)
				exitList[id] = Exit(exitDialog.le2.text(), destination)
				exitList[id].dest = source
				self.drawExit(id)
				self.scene.addItem(exitList[id].line)
		self.drawRoom(source)
		self.drawRoom(destination)
		self.updateStatusExit()

	def openExitChain(self):
		exitDialog = newExitName()
		if exitDialog.exec_():
			for x in range(len(self.graphicsView.chainRoom) - 1): # Skip the last room
				source = self.graphicsView.chainRoom[x]
				destination = self.graphicsView.chainRoom[x+1]
				id = findNewId(exitList)
				exitList[id] = Exit(exitDialog.le.text(), source)
				exitList[id].dest = destination
				self.drawExit(id)
				self.scene.addItem(exitList[id].line)
				if exitDialog.checkBox.isChecked():
					id = findNewId(exitList)
					exitList[id] = Exit(exitDialog.le2.text(), destination)
					exitList[id].dest = source
					self.drawExit(id)
					self.scene.addItem(exitList[id].line)
				self.drawRoom(self.graphicsView.chainRoom[x])
				self.drawRoom(self.graphicsView.chainRoom[x+1])
			self.updateStatusExit()

	def editRoomProperties(self, index):
		editDialog = editRoom()
		editDialog.setData(index)
		if editDialog.exec_():
			roomList[index].name=editDialog.le_name.text()
			roomList[index].desc=editDialog.te_description.toPlainText()
			roomList[index].x=editDialog.sb_pos_x.value()
			roomList[index].y=editDialog.sb_pos_y.value()
			roomList[index].size = (2 * editDialog.sb_size.value()) + 1
			roomList[index].center = editDialog.sb_size.value()
			if editDialog.color.isValid():
				roomList[index].bColor = editDialog.color.name()
			codeList = editDialog.te_code.toPlainText().split("\n")
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

			for i in verbList:
				exitList[index].verbs[i] = editDialog.msgLineEdit[i].text()

			items = []
			for x in range(editDialog.list1.count()):
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
			labelList[id] = Label(labelDialog.te.toPlainText(), id, x_, y_)
			self.scene.addItem(labelList[id].text)
			self.scene.addItem(labelList[id].box)
			labelList[id].box.move_restrict_rect = QRectF(0, 0, self.scene.width(), self.scene.height())
			self.drawLabel(id)
			labelDialog.close()
			self.updateStatusLabel()

	def deleteLabel(self, id_):
		self.scene.removeItem(labelList[id_].text)
		self.scene.removeItem(labelList[id_].box)
		del labelList[id_]
		self.updateStatusLabel()

	def editLabelProperties(self, id_):
		objectClicked = id_
		editDialog = addLabel()
		editDialog.setWindowTitle("Edit Label")
		editDialog.te.document().setPlainText(labelList[objectClicked].normalText)
		if editDialog.exec_():
			labelList[objectClicked].setText(editDialog.te.toPlainText())
			labelList[objectClicked].box.setRect(0, 0, labelList[objectClicked].text.boundingRect().width(), labelList[objectClicked].text.boundingRect().height())

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	diggerconf.loadConfigFile(len(sys.argv) > 2)
	window = Main()
	if len(sys.argv) > 2:
		if sys.argv[1] == "--export" or sys.argv[1] == "-e":
			if not os.path.exists(sys.argv[2]):
				print("Error: File not found.")
				sys.exit()
			window.fileName = sys.argv[2]
			if diggerconf.exportType == 'xml':
				window.populateFromDOM(window.fileName)
			elif diggerconf.exportType == 'json':
				window.populateFromJson(window.fileName)

			print(mush.generateCode(window.fileName, roomList, exitList, labelList))
	else:
		window.show()
		sys.exit(app.exec_())
