
from PyQt5 import QtCore, QtGui, QtWidgets, uic
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
		return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
	def _translate(context, text, disambig):
		return QtWidgets.QApplication.translate(context, text, disambig)


class mapView(QtWidgets.QGraphicsView):
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
		self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
		self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.zoomFactor = 1

	def resetZoom(self):
		self.scale(1.0/self.zoomFactor, 1.0/self.zoomFactor)
		self.zoomFactor = 1

	def wheelEvent(self, event):
		delta = event.angleDelta()
		factor = -(delta.x() + delta.y()) // 120
		if factor == 1: # Zoom in
			factor = 1.25
			self.zoomFactor *= factor
			self.scale(factor, factor)
		elif factor == -1: # Zoom out
			factor = 0.8
			if self.scene().width()*self.zoomFactor != self.width() and self.scene().width()*self.zoomFactor*factor >= self.width():
				self.zoomFactor *= factor
				self.scale(factor, factor)

	def cursorInObject(self, x, y, bx, rx, by, ry):
		return (x >= bx) and (x <= bx + rx) and (y >= by) and (y <= by + ry)
	def cursorInRoom(self, pos, room):
		return self.cursorInObject(pos.x(), pos.y(), room.x, room.size, room.y, room.size)
	def cursorInLabel(self, pos, label):
		return self.cursorInObject(pos.x(), pos.y(), label.x, label.box.boundingRect().width(), label.y, label.box.boundingRect().height())

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
			for i, room in roomList.items():
				if self.cursorInRoom(scenePos, room):
					check = 1
					self.parent().parent().openExitName(self.source, i)
					self.scene().removeItem(self.tempLine)
					break
			if check == 0:
				self.scene().removeItem(self.tempLine)
			self.joinExit = 0
		elif self.joinExit == 2: # Chain exit
			check = 0
			for i, room in roomList.items():
				if self.cursorInRoom(scenePos, room):
					check = 1
					self.chainRoom.append(i)
					self.chainLine.append(QGraphicsLineItem())
					self.scene().addItem(self.chainLine[-1])
					val_x = roomList[self.chainRoom[-2]].x + roomList[self.chainRoom[-2]].center
					val_y = roomList[self.chainRoom[-2]].y + roomList[self.chainRoom[-2]].center
					last_x = roomList[self.chainRoom[-1]].x + roomList[self.chainRoom[-1]].center
					last_y = roomList[self.chainRoom[-1]].y + roomList[self.chainRoom[-1]].center
					self.tempLine.setLine(last_x, last_y, scenePos.x(), scenePos.y())
					self.chainLine[-1].setLine(val_x, val_y, last_x, last_y)
					break
			if check == 0:
				self.scene().removeItem(self.tempLine)
				self.parent().parent().openExitChain()
				del self.chainRoom[:]
				for x in self.chainLine:
					self.scene().removeItem(x)
				del self.chainLine[:]
				self.joinExit = 0

		else: # Pan scene across graphicsView
			check = False
			for i, room in roomList.items(): # Is the cursor over a room?
				if self.cursorInRoom(scenePos, room):
					self.selectedRoom = i
					check = True
					break
			for i, label in labelList.items(): # Is the cursor over a label?
				if self.cursorInLabel(scenePos, label):
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

		if scenePos.x() > self.scene().width() or scenePos.y() > self.scene().height(): # Cursor outside of scene
			return

		for i, room in roomList.items():
			if self.cursorInRoom(scenePos, room):
				objectClicked = i
				check = 1
		if check == 0: # If not, check if user right-clicked on a label
			for i, label in labelList.items():
				if self.cursorInLabel(scenePos, label):
					objectClicked = i
					check = 2
		#User clicked on a room
		if check == 1:
			menu = QMenu()
			actionViewDetails = menu.addAction("#" + str(objectClicked) + ": " + roomList[objectClicked].name)
			actionEditRoom = menu.addAction("Edit Properties")
			actionAddExit = menu.addAction("Add Exit")
			actionAddExitChain = menu.addAction("Add Exit Chain")
			exitMenu = menu.addMenu("Exits")
			actionDeleteRoom = menu.addAction('Delete Room')
			actionDeleteRoom.setIcon(QIcon.fromTheme('edit-delete'))
			menu.addSeparator()
			actionCopy = menu.addAction('Copy')
			actionCopy.setShortcut('Ctrl+C')
			actionCopy.setIcon(QIcon.fromTheme('edit-copy'))
			actionExitList = {}
			menuEnabled = False
			for f in exitList:
				if exitList[f].source == objectClicked:
					menuEnabled = True
					actionExitList[f] = exitMenu.addAction(exitList[f].name)
			exitMenu.setEnabled(menuEnabled)
			action = menu.exec_(event.globalPos())
			if action == actionEditRoom: # Edit a room
				self.parent().parent().editRoomProperties(objectClicked)
			elif action == actionAddExit: # Add new exit
				self.joinExit = 1
				self.source = objectClicked
				self.scene().addItem(self.tempLine)
			elif action == actionAddExitChain:
				self.joinExit = 2 # Chain exits
				del self.chainLine[:]
				del self.chainRoom[:]
				self.chainRoom.append(objectClicked)
				self.scene().addItem(self.tempLine)

			elif action == actionDeleteRoom: # Delete a room
				self.parent().parent().deleteRoom(objectClicked)
			elif action == actionCopy: # Copy this Room
				self.parent().parent().copyRoom(objectClicked)
			else:
				for k in actionExitList:
					if action == actionExitList[k]:
						self.parent().parent().editExitProperties(k)
						break
		#User clicked on a label
		elif check == 2:
			menu = QMenu()
			actionEditLabel = menu.addAction("Edit Properties")
			actionDeleteLabel = menu.addAction("Delete Label")
			action = menu.exec_(event.globalPos())
			if action == actionEditLabel:
				self.parent().parent().editLabelProperties(objectClicked)
			elif action == actionDeleteLabel:
				self.parent().parent().deleteLabel(objectClicked)
		#Map Actions, user clicked on scene
		elif check == 0:
			menu = QMenu()
			actionNewRoom = menu.addAction("New Room")
			actionNewExit = menu.addAction("New Exit")
			actionAddLabel = menu.addAction("Add Label")
			menu.addSeparator()
			actionPaste = menu.addAction("Paste")
			actionPaste.setShortcut("Ctrl+V")
			actionPaste.setIcon(QIcon.fromTheme('edit-paste'))
			action = menu.exec_(event.globalPos())
			if action == actionNewRoom:
				self.parent().parent().digRoom(scenePos.x(), scenePos.y())
			elif action == actionNewExit:
				self.parent().parent().openExit()
			elif action == actionAddLabel:
				self.parent().parent().addLabel(scenePos.x(), scenePos.y())
			elif action == actionPaste:
				self.parent().parent().pasteRoom(scenePos.x(), scenePos.y())

class Ui_MainWindow(object):
	def setupUi(self, MainWindow):
		uic.loadUi('digger.ui', self)
