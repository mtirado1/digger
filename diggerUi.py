
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
		self.tempLine = QGraphicsLineItem()
		self.setMouseTracking(True)

	def isWithin(self, a, b, r):
		#Checks if a is within b+r and b-r
		return (a >= b) and (a <= b+r)

	def mouseMoveEvent(self, event):
		QGraphicsView.mouseMoveEvent(self, event)
		if self.joinExit == 1:
			self.tempLine.setLine(roomList[self.source].x + ROOM_CENTER, roomList[self.source].y + ROOM_CENTER, self.mapToScene(event.x(), event.y()).x(), self.mapToScene(event.x(), event.y()).y())

	def mousePressEvent(self, event):
		global roomList
		global exitList
		global id_exit
		QGraphicsView.mousePressEvent(self, event)
		if self.joinExit == 1:
			check = 0
			for iRoom in roomList:
				if self.isWithin(event.x(), iRoom.x, ROOM_SIZE) and self.isWithin(event.y(), iRoom.y, ROOM_SIZE):
					check = 1
					self.parent().openExitName(self.source, iRoom.id)
					self.parent().ui.scene.removeItem(self.tempLine)
					break
			if check == 0:
				self.parent().ui.scene.removeItem(self.tempLine)
			self.joinExit = 0

	def contextMenuEvent(self, event):
		#Check if the user clicked on a room
		global roomList
		global labelList
		global exitList
		global id_exit
		eventPos = QPoint(event.x(), event.y())
		scenePos = self.mapToScene(eventPos)
		check = 0
		objectClicked = 0
		for i in range(len(roomList)):
			if self.isWithin(self.mapToScene(eventPos).x(), roomList[i].x, ROOM_SIZE) and self.isWithin(self.mapToScene(eventPos).y(), roomList[i].y, ROOM_SIZE):
				objectClicked = i
				check = 1
		if check == 0:
			for i in xrange(len(labelList)):
				if self.isWithin(self.mapToScene(eventPos).x(), labelList[i].x, labelList[i].box.boundingRect().width()) and self.isWithin(self.mapToScene(eventPos).y(), labelList[i].y, labelList[i].box.boundingRect().height()):
					objectClicked = i
					check = 2
		#User clicked on a room
		if check == 1:
			global exitList
			menu = QMenu()
			actionViewDetails = menu.addAction("#" + str(roomList[objectClicked].id) + ": " + roomList[objectClicked].name)
			actionEditRoom = menu.addAction("Edit Properties")
			actionAddExit = menu.addAction("Add Exit")
			exitMenu = menu.addMenu("Exits")
			actionDeleteRoom = menu.addAction("Delete Room")
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
			elif action == actionDeleteRoom: # Delete a room
				self.parent().deleteRoom(objectClicked)
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
				editDialog = addLabel()
				editDialog.setWindowTitle("Edit Label")
				editDialog.le.setText(labelList[objectClicked].normalText)
				if editDialog.exec_():
					labelList[objectClicked].setText(editDialog.le.text())
					labelList[objectClicked].box.setRect(0, 0, labelList[objectClicked].text.boundingRect().width(), labelList[objectClicked].text.boundingRect().height())
			elif action == actionDeleteLabel:
				self.parent().deleteLabel(objectClicked)
		#Map Actions, user clicked on scene
		elif check == 0:
			menu = QMenu()
			actionNewRoom = menu.addAction("New Room")
			actionNewExit = menu.addAction("New Exit")
			actionAddLabel = menu.addAction("Add Label")
			action = menu.exec_(event.globalPos())
			if action == actionNewRoom:
				self.parent().digRoom(scenePos.x(), scenePos.y())
			elif action == actionNewExit:
				self.parent().openExit()
			elif action == actionAddLabel:
				self.parent().addLabel(scenePos.x(), scenePos.y())

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
		self.actionSave.setObjectName(_fromUtf8("actionToggleText"))

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

		self.menuEdit.addAction(self.actionNewRoom)
		self.menuEdit.addAction(self.actionNewExit)
		self.menuEdit.addAction(self.actionNewLabel)

		self.menuView.addAction(self.actionToggleText)

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

		self.actionExport.setText(_translate("MainWindow", "&Export", None))
		self.actionNew.setText(_translate("MainWindow", "&New", None))
		self.actionOpen.setText(_translate("MainWindow", "&Open", None))
		self.actionSave.setText(_translate("MainWindow", "&Save", None))
		self.actionSaveAs.setText(_translate("MainWindow", "Save As", None))
		self.actionToggleText.setText(_translate("MainWindow", "Show details", None))
