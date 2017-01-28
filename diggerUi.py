
from PyQt4 import QtCore, QtGui
from diggerfuncs import *
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


class mapView(QtGui.QGraphicsView):
	def __init__(self, parent=None):
		super(mapView, self).__init__(parent)
		self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
		self.joinExit = 0
		self.source = -1
		self.selectedRoom = -1
		self.oldPos = 0
		self.newPos = 0
		self.posX = 0
		self.posY = 0
		self.isPanning = False
		self.tempLine = QGraphicsLineItem()

		# Exit chaining
		self.chainRoom = []
		self.chainLine = []

		self.setMouseTracking(True)
		self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
		self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.zoomFactor = 1

	def resetZoom(self):
		self.scale(1.0/self.zoomFactor, 1.0/self.zoomFactor)
		self.zoomFactor = 1

	def wheelEvent(self, event):
		factor = -event.delta() // 120
		if factor == 1: # Zoom in
			factor = 1.25
			self.zoomFactor *= factor
			self.scale(factor, factor)
		elif factor == -1: # Zoom out
			factor = 0.8
			#if self.zoomFactor*factor >=1:
			if self.parent().ui.scene.width()*self.zoomFactor != self.width() and self.parent().ui.scene.width()*self.zoomFactor*factor >= self.width():
				self.zoomFactor *= factor
				self.scale(factor, factor)

	def isWithin(self, a, b, r):
		#Checks if a is within b+r and b-r
		return (a >= b) and (a <= b+r)

	def mouseMoveEvent(self, event):
		QGraphicsView.mouseMoveEvent(self, event)
		scenePos = self.mapToScene(QPoint(event.x(), event.y()))
		self.posX = scenePos.x()
		self.posY = scenePos.y()
		if self.joinExit == 1:
			self.tempLine.setLine(roomList[self.source].x + roomList[self.source].center, roomList[self.source].y + roomList[self.source].center, scenePos.x(), scenePos.y())
		elif self.joinExit == 2: # Chain exit
			val_x = roomList[self.chainRoom[-1]].x + roomList[self.chainRoom[-1]].center
			val_y = roomList[self.chainRoom[-1]].y + roomList[self.chainRoom[-1]].center
			self.tempLine.setLine(val_x, val_y, scenePos.x(), scenePos.y())
		elif self.isPanning == True:
			self.newPos = event.pos() - self.oldPos
			self.oldPos = event.pos()
			self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - self.newPos.x())
			self.verticalScrollBar().setValue(self.verticalScrollBar().value() - self.newPos.y())

	def mouseReleaseEvent(self, event):
		QGraphicsView.mouseReleaseEvent(self, event)
		if event.button() == Qt.LeftButton:
			self.isPanning = False

	def mousePressEvent(self, event):
		eventPos = QPoint(event.x(), event.y())
		scenePos = self.mapToScene(eventPos)
		QGraphicsView.mousePressEvent(self, event)
		if self.joinExit == 1:
			check = 0
			for iRoom in roomList:
				if self.isWithin(scenePos.x(), iRoom.x, iRoom.size) and self.isWithin(scenePos.y(), iRoom.y, iRoom.size):
					check = 1
					self.parent().openExitName(roomList[self.source].id, iRoom.id)
					self.parent().ui.scene.removeItem(self.tempLine)
					break
			if check == 0:
				self.parent().ui.scene.removeItem(self.tempLine)
			self.joinExit = 0
		elif self.joinExit == 2: # Chain exit
			check = 0
			for x in xrange(len(roomList)):
				if self.isWithin(scenePos.x(), roomList[x].x, roomList[x].size) and self.isWithin(scenePos.y(), roomList[x].y, roomList[x].size):
					check = 1
					self.chainRoom.append(x)
					self.chainLine.append(QGraphicsLineItem())
					self.parent().ui.scene.addItem(self.chainLine[-1])
					val_x = roomList[self.chainRoom[-2]].x + roomList[self.chainRoom[-2]].center
					val_y = roomList[self.chainRoom[-2]].y + roomList[self.chainRoom[-2]].center
					last_x = roomList[self.chainRoom[-1]].x + roomList[self.chainRoom[-1]].center
					last_y = roomList[self.chainRoom[-1]].y + roomList[self.chainRoom[-1]].center
					self.tempLine.setLine(last_x, last_y, scenePos.x(), scenePos.y())
					self.chainLine[-1].setLine(val_x, val_y, last_x, last_y)
					break
			if check == 0:
				self.parent().ui.scene.removeItem(self.tempLine)
				self.parent().openExitChain()
				del self.chainRoom[:]
				for x in self.chainLine:
					self.parent().ui.scene.removeItem(x)
				del self.chainLine[:]
				self.joinExit = 0

		else: # Pan scene across graphicsView
			check = False
			for iRoom in roomList: # Is the cursor over a room?
				if self.isWithin(scenePos.x(), iRoom.x, iRoom.size) and self.isWithin(scenePos.y(), iRoom.y, iRoom.size): # Pan View
					self.selectedRoom = iRoom.id
					check = True
					break
			for iLabel in labelList: # Is the cursor over a label?
				if self.isWithin(scenePos.x(), iLabel.x, iLabel.box.boundingRect().width()) and self.isWithin(scenePos.y(), iLabel.y, iLabel.box.boundingRect().height()):
					check = True
					break
			if event.button() == Qt.LeftButton and not check:
				self.selectedRoom = -1
				self.isPanning = True # Start panning
				self.oldPos = event.pos()

	def contextMenuEvent(self, event):
		#Check if the user clicked on a room
		eventPos = QPoint(event.x(), event.y())
		scenePos = self.mapToScene(eventPos)
		check = 0
		objectClicked = 0

		if scenePos.x() > self.parent().ui.scene.width() or scenePos.y() > self.parent().ui.scene.height(): # Cursor outside of scene
			return

		for i in range(len(roomList)):
			if self.isWithin(self.mapToScene(eventPos).x(), roomList[i].x, roomList[i].size) and self.isWithin(self.mapToScene(eventPos).y(), roomList[i].y, roomList[i].size):
				objectClicked = i
				check = 1
		if check == 0: # If not, check if user right-clicked on a label
			for i in xrange(len(labelList)):
				if self.isWithin(self.mapToScene(eventPos).x(), labelList[i].x, labelList[i].box.boundingRect().width()) and self.isWithin(self.mapToScene(eventPos).y(), labelList[i].y, labelList[i].box.boundingRect().height()):
					objectClicked = i
					check = 2
		#User clicked on a room
		if check == 1:
			menu = QMenu()
			actionViewDetails = menu.addAction("#" + str(roomList[objectClicked].id) + ": " + roomList[objectClicked].name)
			actionEditRoom = menu.addAction("Edit Properties")
			actionAddExit = menu.addAction("Add Exit")
			actionAddExitChain = menu.addAction("Add Exit Chain")
			exitMenu = menu.addMenu("Exits")
			actionDeleteRoom = menu.addAction("Delete Room")
			menu.addSeparator()
			actionCopy = menu.addAction("Copy")
			actionCopy.setShortcut(QtGui.QKeySequence("Ctrl+C"))
			actionExitList = []
			actionExitId = []
			menuEnabled = False
			for f in xrange(len(exitList)):
				if exitList[f].source == roomList[objectClicked].id:
					menuEnabled = True
					actionExitId.append(f)
					actionExitList.append(exitMenu.addAction(exitList[f].name))
			exitMenu.setEnabled(menuEnabled)
			action = menu.exec_(event.globalPos())
			if action == actionEditRoom: # Edit a room
				self.parent().editRoomProperties(objectClicked)
			elif action == actionAddExit: # Add new exit
				self.joinExit = 1
				self.source = objectClicked
				self.parent().ui.scene.addItem(self.tempLine)
			elif action == actionAddExitChain:
				self.joinExit = 2 # Chain exits
				del self.chainLine[:]
				del self.chainRoom[:]
				self.chainRoom.append(objectClicked)
				self.parent().ui.scene.addItem(self.tempLine)

			elif action == actionDeleteRoom: # Delete a room
				self.parent().deleteRoom(objectClicked)
			elif action == actionCopy: # Copy this Room
				self.parent().copyRoom(roomList[objectClicked].id)
			else:
				for k in xrange(len(actionExitList)):
					if action == actionExitList[k]:
						self.parent().editExitProperties(actionExitId[k])
						break
		#User clicked on a label
		elif check == 2:
			menu = QMenu()
			actionEditLabel = menu.addAction("Edit Properties")
			actionDeleteLabel = menu.addAction("Delete Label")
			action = menu.exec_(event.globalPos())
			if action == actionEditLabel:
				self.parent().editLabelProperties(objectClicked)
			elif action == actionDeleteLabel:
				self.parent().deleteLabel(objectClicked)
		#Map Actions, user clicked on scene
		elif check == 0:
			menu = QMenu()
			actionNewRoom = menu.addAction("New Room")
			actionNewExit = menu.addAction("New Exit")
			actionAddLabel = menu.addAction("Add Label")
			menu.addSeparator()
			actionPaste = menu.addAction("Paste")
			actionPaste.setShortcut(QtGui.QKeySequence("Ctrl+V"))
			action = menu.exec_(event.globalPos())
			if action == actionNewRoom:
				self.parent().digRoom(scenePos.x(), scenePos.y())
			elif action == actionNewExit:
				self.parent().openExit()
			elif action == actionAddLabel:
				self.parent().addLabel(scenePos.x(), scenePos.y())
			elif action == actionPaste:
				self.parent().pasteRoom(scenePos.x(), scenePos.y())

class Ui_MainWindow(object):
	def setupUi(self, MainWindow):
		MainWindow.setObjectName(_fromUtf8("MainWindow"))
		MainWindow.resize(1080, 683)
		self.graphicsView = mapView(MainWindow)
		self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
		MainWindow.setCentralWidget(self.graphicsView)
		self.menubar = QtGui.QMenuBar(MainWindow)
		self.menubar.setGeometry(QtCore.QRect(0, 0, 1080, 25))
		self.menubar.setObjectName(_fromUtf8("menubar"))
		self.menuFile = QtGui.QMenu(self.menubar)
		self.menuFile.setObjectName(_fromUtf8("menuFile"))
		self.menuEdit = QtGui.QMenu(self.menubar)
		self.menuEdit.setObjectName(_fromUtf8("menuEdit"))
		self.menuView = QtGui.QMenu(self.menubar)
		self.menuView.setObjectName(_fromUtf8("menuView"))
		self.actionOptions = QtGui.QAction(self.menubar)
		self.actionOptions.setObjectName(_fromUtf8("actionOptions"))
		self.actionAbout = QtGui.QAction(self.menubar)
		self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
		MainWindow.setMenuBar(self.menubar)
		self.statusbar = QtGui.QStatusBar(MainWindow)
		self.statusbar.setObjectName(_fromUtf8("statusbar"))
		MainWindow.setStatusBar(self.statusbar)

		self.actionExport = QtGui.QAction(MainWindow)
		self.actionExport.setObjectName(_fromUtf8("actionExport"))
		self.actionExport.setShortcut("Ctrl+E")
		self.actionExportToFile = QtGui.QAction(MainWindow)
		self.actionExportToFile.setObjectName(_fromUtf8("actionExportToFile"))
		self.actionExportToFile.setShortcut("Ctrl+F")
		self.actionNew = QtGui.QAction(MainWindow)
		self.actionNew.setObjectName(_fromUtf8("actionNew"))
		self.actionNew.setShortcut("Ctrl+N")
		self.actionOpen = QtGui.QAction(MainWindow)
		self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
		self.actionOpen.setShortcut("Ctrl+O")
		self.actionSave = QtGui.QAction(MainWindow)
		self.actionSave.setObjectName(_fromUtf8("actionSave"))
		self.actionSave.setShortcut("Ctrl+S")
		self.actionSaveAs = QtGui.QAction(MainWindow)
		self.actionSaveAs.setObjectName(_fromUtf8("actionSaveAs"))
		self.actionSaveAs.setShortcut("Ctrl+Shift+S")
		self.actionToggleText = QtGui.QAction(MainWindow, checkable=True)
		self.actionToggleText.setChecked(True)
		self.actionToggleText.setObjectName(_fromUtf8("actionToggleText"))

		self.actionResetZoom = QtGui.QAction(MainWindow)
		self.actionResetZoom.setObjectName(_fromUtf8("actionResetZoom"))

		self.actionNewRoom = QtGui.QAction(MainWindow)
		self.actionNewRoom.setObjectName(_fromUtf8("actionNewRoom"))
		self.actionNewRoom.setShortcut("Ctrl+Shift+R")
		self.actionNewExit= QtGui.QAction(MainWindow)
		self.actionNewExit.setObjectName(_fromUtf8("actionNewExit"))
		self.actionNewExit.setShortcut("Ctrl+Shift+E")
		self.actionNewLabel= QtGui.QAction(MainWindow)
		self.actionNewLabel.setObjectName(_fromUtf8("actionNewLabel"))
		self.actionNewLabel.setShortcut("Ctrl+Shift+L")

		self.menuFile.addAction(self.actionNew)
		self.menuFile.addAction(self.actionOpen)
		self.menuFile.addSeparator()
		self.menuFile.addAction(self.actionSave)
		self.menuFile.addAction(self.actionSaveAs)
		self.menuFile.addSeparator()
		self.menuFile.addAction(self.actionExport)
		self.menuFile.addAction(self.actionExportToFile)


		self.menuEdit.addAction(self.actionNewRoom)
		self.menuEdit.addAction(self.actionNewExit)
		self.menuEdit.addAction(self.actionNewLabel)

		self.menuView.addAction(self.actionToggleText)
		self.menuView.addAction(self.actionResetZoom)

		self.menubar.addAction(self.menuFile.menuAction())
		self.menubar.addAction(self.menuEdit.menuAction())
		self.menubar.addAction(self.menuView.menuAction())
		self.menubar.addAction(self.actionOptions)
		self.menubar.addAction(self.actionAbout)
		self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)

		# Prepare scene
		self.scene = QGraphicsScene(self.graphicsView)
		self.scene.setSceneRect(0 , 0, diggerconf.mapWidth, diggerconf.mapHeight)
		self.graphicsView.setScene(self.scene)
		self.graphicsView.setAlignment(Qt.AlignLeft|Qt.AlignTop)

	def retranslateUi(self, MainWindow):
		MainWindow.setWindowTitle(_translate("MainWindow", "Digger", None))
		self.menuFile.setTitle(_translate("MainWindow", "File", None))
		self.menuEdit.setTitle(_translate("MainWindow", "Edit", None))
		self.menuView.setTitle(_translate("MainWindow", "View", None))
		self.actionOptions.setText(_translate("MainWindow", "Options", None))
		self.actionAbout.setText(_translate("MainWindow", "About", None))

		self.actionNewRoom.setText(_translate("MainWindow", "Add &Room", None))
		self.actionNewExit.setText(_translate("MainWindow", "Add &Exit", None))
		self.actionNewLabel.setText(_translate("MainWindow", "Add &Label", None))

		self.actionExportToFile.setText(_translate("MainWindow", "Export to &File", None))
		self.actionExport.setText(_translate("MainWindow", "&Export", None))
		self.actionNew.setText(_translate("MainWindow", "&New", None))
		self.actionOpen.setText(_translate("MainWindow", "&Open", None))
		self.actionSave.setText(_translate("MainWindow", "&Save", None))
		self.actionSaveAs.setText(_translate("MainWindow", "Save As", None))
		self.actionToggleText.setText(_translate("MainWindow", "Show details", None))
		self.actionResetZoom.setText(_translate("MainWindow", "Reset Zoom", None))
