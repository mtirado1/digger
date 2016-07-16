# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'digger.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!
import sys
import math
from PyQt4 import QtCore, QtGui, QtXml
#from diggerfuncs import *
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
		self.isNewFile = 1
		self.fileName = "Untitled"
		self.bColor = "#FFFFFF"
		self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))

	def resizeEvent(self, event):
		self.ui.graphicsView.setGeometry(QtCore.QRect(0, 0, event.size().width(), event.size().height()))
		self.ui.scene.setSceneRect(0, 0, event.size().width(), event.size().height() - 14)

	def readMapNode(self, element):
		global roomList
		global exitList
		global labelList
		global id_room
		global id_exit
		global id_label
		def intFromQStr(qstr):
			return int(str(qstr))
		def getText(node):
			child = node.firstChild()
			text = QString()
			while not child.isNull():
				if child.nodeType() == QtXml.QDomNode.TextNode:
					text += child.toText().data()
				child = child.nextSibling()
			return text.trimmed()
		def readLabelNode(element):
			load_label_x = intFromQStr(element.attribute("x"))
			load_label_y = intFromQStr(element.attribute("y"))
			load_label_text = getText(element)
			labelList.append(Label(load_label_text, load_label_x, load_label_y))
			self.ui.scene.addItem(labelList[id_label].text)
			self.ui.scene.addItem(labelList[id_label].box)
			id_label = id_label + 1
		def readRoomNode(element):
			global id_room
			load_room_id = intFromQStr(element.attribute("id"))
			load_room_x = intFromQStr(element.attribute("x"))
			load_room_y = intFromQStr(element.attribute("y"))
			load_room_name = load_room_desc = None
			node = element.firstChild()
			while load_room_name is None or load_room_desc is None:
				if node.isNull():
					raise ValueError, "Missing name or description"
				if node.toElement().tagName() == "name":
					load_room_name = getText(node)
				elif node.toElement().tagName() == "description":
					load_room_desc = getText(node)
				node = node.nextSibling()
			roomList.append(Room(load_room_name, load_room_id, self))
			roomList[id_room].desc = load_room_desc
			roomList[id_room].x = load_room_x
			roomList[id_room].y = load_room_y
			self.ui.scene.addItem(roomList[id_room].box)
			self.ui.scene.addItem(roomList[id_room].text)
			id_room = id_room + 1

		def readExitNode(element):
			global id_exit
			global exitList
			load_exit_id = intFromQStr(element.attribute("id"))
			load_exit_source = intFromQStr(element.attribute("source"))
			load_exit_dest = intFromQStr(element.attribute("destination"))
			load_exit_name = load_exit_alias = None
			node = element.firstChild()
			while load_exit_name is None or load_exit_alias is None:
				if node.isNull():
					raise ValueError, "Missing name or alias"
				if node.toElement().tagName() == "name":
					load_exit_name = getText(node)
				elif node.toElement().tagName() == "alias":
					load_exit_alias = getText(node)
				node = node.nextSibling()
			exitList.append(Exit(load_exit_name, load_exit_id, load_exit_source))
			exitList[id_exit].alias = load_exit_alias
			exitList[id_exit].dest = load_exit_dest
			self.ui.scene.addItem(exitList[id_exit].line)
			id_exit = id_exit + 1


		load_map_width = intFromQStr(element.attribute("width"))
		load_map_height = intFromQStr(element.attribute("height"))
		load_map_bcolor = str(element.attribute("bcolor"))
		node = element.firstChild()
		while not node.isNull():
			if node.toElement().tagName() == "room":
				readRoomNode(node.toElement())
			elif node.toElement().tagName() == "exit":
				readExitNode(node.toElement())
			elif node.toElement().tagName() == "label":
				readLabelNode(node.toElement())
			node = node.nextSibling()
		self.bColor = load_map_bcolor
		self.ui.scene.setBackgroundBrush(QColor(load_map_bcolor))
		self.resize(load_map_width, load_map_height)
		self.ui.graphicsView.setGeometry(QtCore.QRect(0, 0, load_map_width, load_map_height))
		self.ui.menubar.setGeometry(QtCore.QRect(0, 0, load_map_width, load_map_height))
		self.ui.scene.setSceneRect(0, 0, load_map_width, load_map_height - 14)

	def populateFromDOM(self, dom):
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
		root = dom.documentElement()
		if root.tagName() != "DIGGER":
			raise ValueError, "not a Digger XML file"
		node = root.firstChild()
		while not node.isNull():
			if node.toElement().tagName() == "map":
				self.readMapNode(node.toElement())
			node = node.nextSibling()
		self.drawAll()

	def openFile(self):
		fname = QFileDialog.getOpenFileName(self, 'Open file', '/',"")
		if fname:
			dom = QtXml.QDomDocument()
			error = None
			fh = None
			try:
				fh = QFile(fname)
				if not fh.open(QIODevice.ReadOnly):
					raise IOError, unicode(fh.errorString())
				if not dom.setContent(fh):
					raise ValueError, "could not parse XML"
			except (IOError, OSError, ValueError), e:
				error = "Failed to import: %s" % e
			finally:
				if fh is not None:
					fh.close()
				if error is not None:
					return False, error
			try:
				self.populateFromDOM(dom)
				self.fileName = fname
				self.setWindowTitle(_translate("MainWindow", self.fileName + " - Digger", None))
			except ValueError, e:
				return False, "Failed to import: %s" % e


	def saveFile(self):
		fname = QFileDialog.getSaveFileName(self, 'Save file', '/', "")
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
				stream << "<?xml version='1.0' encoding='UTF-8'?>\n" << "<!DOCTYPE DIGGER>\n" << "<DIGGER VERSION='1.0'>\n"
				stream << ("<map width='%d' height='%d' bcolor='%s'>\n" % (self.ui.graphicsView.width(), self.ui.graphicsView.height(), self.bColor))
				global roomList
				global exitList
				for x in xrange(len(roomList)):
					stream << ("\t<room id='%d' x='%d' y='%d'>\n" % (roomList[x].id, roomList[x].x, roomList[x].y))
					stream << "\t\t<name> " << Qt.escape(roomList[x].name) << " </name>\n"
					stream << "\t\t<description> " << Qt.escape(roomList[x].desc) << " </description>\n"
					stream << "\t</room>\n"
				for x in xrange(len(exitList)):
					stream << ("\t<exit id='%d' source='%d' destination='%d'>\n" % (exitList[x].id, exitList[x].source, exitList[x].dest))
					stream << "\t\t<name> " << Qt.escape(exitList[x].name) << " </name>\n"
					stream << "\t\t<alias> " << Qt.escape(exitList[x].alias) << " </alias>\n"
					stream << "\t</exit>\n"
				for x in xrange(len(labelList)):
					stream << ("\t<label x='%d' y='%d'> " % (labelList[x].x(), labelList[x].y()))
					stream << "\t\t" << Qt.escape(labelList[x].text())
					stream << "\t</label>\n"
				stream << "</map>\n"

	def isRGB(self, number):
		check = 1
		for x in list(number[1:]):
			if (ord(x) >= 48 and ord(x) <= 57) or ((ord(x) >= 65 and ord(x) <= 70) or (ord(x) >= 97 and ord(x) <= 102)):
				check = check * 1
			else:
				check = 0
		return check and (number[0] == '#')

	def viewAbout(self):
		QMessageBox.about(self, "About Digger", """<b>Digger</b> v %s<p>Copyright &copy; 2016 Martin Tirado. All rights reserved. <p> This program can be used to design MUSH words through a graphical interface. <p> Python %s - Qt %s - PyQt %s on %s""" % (__version__, platform.python_version(), QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

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
		self.ui.scene.setBackgroundBrush(self.bColor)
		self.isNewFile = 1
		global roomList
		global exitList
		global labelList
		global id_room
		id_room = 0
		del roomList[:]
		del exitList[:]
		del labelList[:]
		self.ui.scene.clear()

	def drawAll(self):
		# TODO:
		# Room, label, exit removal and editing
		# SAVE AND OPEN file
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
			roomList[j].text.setHtml(roomString + "</p>")
			roomList[j].text.setPos(QPointF(roomList[j].x + ROOM_CENTER + 2 - (roomList[j].text.boundingRect().width() / 2), roomList[j].y + ROOM_SIZE + 5))
			roomList[j].box.setBrush(QColor("#FF0000"))
			roomList[j].box.setRect(0, 0, ROOM_SIZE, ROOM_SIZE)
			self.ui.scene.addItem(roomList[j].box)
			self.ui.scene.addItem(roomList[j].text)
			roomList[j].box.setZValue(1)
		for j in xrange(len(labelList)):
			labelList[j].text.setZValue(1)
			labelList[j].box.setZValue(0)
			labelList[j].text.setPos(labelList[j].x, labelList[j].y)
			labelList[j].box.setPos(labelList[j].x, labelList[j].y)

	def digRoom(self, x_, y_):
		roomDialog = newRoom(self)
		if roomDialog.exec_():
			global roomList
			global id_room
			if roomDialog.le.text() != "":
				roomList.append(Room(roomDialog.le.text(), id_room, self))
			roomList[id_room].x = x_
			roomList[id_room].y = y_
			self.ui.scene.addItem(roomList[id_room].box)
			self.ui.scene.addItem(roomList[id_room].text)
			self.drawAll()
			id_room = id_room + 1
			roomDialog.close()

	def deleteRoom(self, id_):
		self.ui.scene.removeItem(roomList[id_].box)
		self.ui.scene.removeItem(roomList[id_].text)
		del roomList[id_]
		global id_room
		global id_exit
		id_room = id_room - 1
		check = 1
		p = 0
		while check == 1:
			for x in xrange(len(exitList)):
				if exitList[x].source == id_:
					p = x
					check = 1
					break
				else:
					check = 0
			if not exitList:
				check = 0
			if check == 1:
				self.ui.scene.removeItem(exitList[p].line)
				del exitList[p]
				id_exit = id_exit - 1
		self.drawAll()

	def openExit(self):
		exitDialog = newExit(self)
		if exitDialog.exec_():
			global exitList
			global id_exit
			if int(exitDialog.le2.text()) < len(roomList) and int(exitDialog.le2.text()) >= 0:
				exitList.append(Exit(exitDialog.le.text(), id_exit, int(exitDialog.le2.text())))
			if exitDialog.le3.text() != "" and int(exitDialog.le3.text()) < len(roomList):
				exitList[id_exit].dest = int(exitDialog.le3.text())
			elif exitDialog.le3.text() == "": #No destination
				exitList[id_exit].dest = -1
			self.ui.scene.addItem(exitList[id_exit].line)
			self.drawAll()
			id_exit = id_exit + 1
			exitDialog.close()

	def addLabel(self, x_, y_):
		global labelDialog
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


if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	window = Main()
	window.show()
	sys.exit(app.exec_())
