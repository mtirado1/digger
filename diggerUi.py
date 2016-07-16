
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

	def isWithin(self, a, b, r):
		#Checks if a is within b+r and b-r
		return (a >= b) and (a <= b+r)

	def contextMenuEvent(self, event):
		#Check if the user clicked on a room
		global roomList
		global labelList
		check = 0
		k = 0
		for i in range(len(roomList)):
			if self.isWithin(event.x(), roomList[i].x, ROOM_SIZE) and self.isWithin(event.y(), roomList[i].y, ROOM_SIZE):
				k = i
				check = 1
		if check == 0:
			for i in xrange(len(labelList)):
				if self.isWithin(event.x(), labelList[i].x, labelList[i].box.boundingRect().width()) and self.isWithin(event.y(), labelList[i].y, labelList[i].box.boundingRect().height()):
					k = i
					check = 2
		#User clicked on a room
		if check == 1:
			menu = QMenu()
			actionViewDetails = menu.addAction("#" + str(k) + ": " + roomList[k].name)
			actionEditRoom = menu.addAction("Edit Properties")
			actionDeleteRoom = menu.addAction("Delete Room")
			action = menu.exec_(event.globalPos())
			if action == actionEditRoom:
				editDialog = editRoom()
				editDialog.setData(k)
				if editDialog.exec_():
					roomList[k].name=editDialog.le.text()
					roomList[k].desc=editDialog.le2.text()
					roomList[k].x=int(editDialog.le3.text())
					roomList[k].y=int(editDialog.le4.text())
					self.parent().parent().drawAll()
					editDialog.close()
			elif action == actionDeleteRoom:
				self.parent().parent().deleteRoom(k)
		#User clicked on a label
		elif check == 2:
			menu = QMenu()
			actionEditLabel = menu.addAction("Edit Properties")
			actionDeleteLabel = menu.addAction("Delete Label")
			action = menu.exec_(event.globalPos())
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

		self.actionNew = QtGui.QAction(MainWindow)
		self.actionNew.setObjectName(_fromUtf8("actionNew"))
		self.actionOpen = QtGui.QAction(MainWindow)
		self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
		self.actionSave = QtGui.QAction(MainWindow)
		self.actionSave.setObjectName(_fromUtf8("actionSave"))
		self.menuFile.addSeparator()

		self.menuFile.addAction(self.actionNew)
		self.menuFile.addAction(self.actionOpen)
		self.menuFile.addAction(self.actionSave)
		self.menuFile.addAction(self.actionExport)

		self.menubar.addAction(self.menuFile.menuAction())
		self.menubar.addAction(self.menuEdit.menuAction())
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
		self.actionOptions.setText(_translate("MainWindow", "Options", None))
		self.actionAbout.setText(_translate("MainWindow", "About", None))

		self.actionExport.setText(_translate("MainWindow", "Export", None))
		self.actionNew.setText(_translate("MainWindow", "&New", None))
		self.actionOpen.setText(_translate("MainWindow", "&Open", None))
		self.actionSave.setText(_translate("MainWindow", "&Save", None))
