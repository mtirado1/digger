
from PyQt4 import QtCore, QtGui
from diggerfuncs import *

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
			self.tempLine.setLine(roomList[self.source].x + ROOM_CENTER, roomList[self.source].y + ROOM_CENTER, event.x(), event.y())

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
					self.parent().parent().openExitName(self.source, iRoom.id)
					self.parent().parent().ui.scene.removeItem(self.tempLine)
					break
			if check == 0:
				self.parent().parent().ui.scene.removeItem(self.tempLine)
			self.joinExit = 0

	def contextMenuEvent(self, event):
		#Check if the user clicked on a room
		global roomList
		global labelList
		global exitList
		global id_exit
		check = 0
		objectClicked = 0
		for i in range(len(roomList)):
			if self.isWithin(event.x(), roomList[i].x, ROOM_SIZE) and self.isWithin(event.y(), roomList[i].y, ROOM_SIZE):
				objectClicked = i
				check = 1
		if check == 0:
			for i in xrange(len(labelList)):
				if self.isWithin(event.x(), labelList[i].x, labelList[i].box.boundingRect().width()) and self.isWithin(event.y(), labelList[i].y, labelList[i].box.boundingRect().height()):
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
				if exitList[f].twoWay and exitList[f].dest == roomList[objectClicked].id:
					menuEnabled = True
					actionExitId.append(f)
					actionExitList.append(exitMenu.addAction(exitList[f].returnName))
			exitMenu.setEnabled(menuEnabled)
			action = menu.exec_(event.globalPos())
			if action == actionEditRoom:
				editDialog = editRoom()
				editDialog.setData(objectClicked)
				if editDialog.exec_():
					roomList[objectClicked].name=editDialog.le.text()
					roomList[objectClicked].desc=editDialog.le2.text()
					roomList[objectClicked].x=int(editDialog.le3.text())
					roomList[objectClicked].y=int(editDialog.le4.text())
					self.parent().parent().drawAll()
					editDialog.close()
			elif action == actionAddExit:
				self.joinExit = 1
				self.source = objectClicked
				self.parent().parent().ui.scene.addItem(self.tempLine)
			elif action == actionDeleteRoom:
				self.parent().parent().deleteRoom(objectClicked)
			else:
				for k in xrange(len(actionExitList)):
					if action == actionExitList[k]:
						self.parent().parent().editExitProperties(actionExitId[k])
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
				self.parent().parent().deleteLabel(objectClicked)
		#Map Actions, user clicked on scene
		elif check == 0:
			menu = QMenu()
			actionNewRoom = menu.addAction("New Room")
			actionNewExit = menu.addAction("New Exit")
			actionAddLabel = menu.addAction("Add Label")
			action = menu.exec_(event.globalPos())
			if action == actionNewRoom:
				self.parent().parent().digRoom(event.x(), event.y())
			elif action == actionNewExit:
				self.parent().parent().openExit()
			elif action == actionAddLabel:
				self.parent().parent().addLabel(event.x(), event.y())

class Ui_MainWindow(object):
	def setupUi(self, MainWindow):
		MainWindow.setObjectName(_fromUtf8("MainWindow"))
		MainWindow.resize(1080, 683)
		self.centralwidget = QtGui.QWidget(MainWindow)
		self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
		self.graphicsView = mapView(self.centralwidget)
		self.graphicsView.setGeometry(QtCore.QRect(0, 0, VIEW_X, VIEW_Y))
		self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
		MainWindow.setCentralWidget(self.centralwidget)
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
		self.actionToggleText = QtGui.QAction(MainWindow, checkable=True)
		self.actionToggleText.setChecked(True)
		self.actionSave.setObjectName(_fromUtf8("actionToggleText"))

		self.menuFile.addAction(self.actionNew)
		self.menuFile.addAction(self.actionOpen)
		self.menuFile.addSeparator()
		self.menuFile.addAction(self.actionSave)
		self.menuFile.addAction(self.actionExport)

		self.menuView.addAction(self.actionToggleText)

		self.menubar.addAction(self.menuFile.menuAction())
		self.menubar.addAction(self.menuEdit.menuAction())
		self.menubar.addAction(self.menuView.menuAction())
		self.menubar.addAction(self.actionOptions)
		self.menubar.addAction(self.actionAbout)
		self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)

		# Prepare scene
		self.scene = QGraphicsScene(self.centralwidget)
		self.scene.setSceneRect(0 , 0, SCENE_X, SCENE_Y)
		self.graphicsView.setScene(self.scene)

	def retranslateUi(self, MainWindow):
		MainWindow.setWindowTitle(_translate("MainWindow", "Digger", None))
		self.menuFile.setTitle(_translate("MainWindow", "File", None))
		self.menuEdit.setTitle(_translate("MainWindow", "Edit", None))
		self.menuView.setTitle(_translate("MainWindow", "View", None))
		self.actionOptions.setText(_translate("MainWindow", "Options", None))
		self.actionAbout.setText(_translate("MainWindow", "About", None))

		self.actionExport.setText(_translate("MainWindow", "&Export", None))
		self.actionNew.setText(_translate("MainWindow", "&New", None))
		self.actionOpen.setText(_translate("MainWindow", "&Open", None))
		self.actionSave.setText(_translate("MainWindow", "&Save", None))
		self.actionToggleText.setText(_translate("MainWindow", "Show details", None))
