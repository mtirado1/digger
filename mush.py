from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json
import diggerconf
from cgi import escape

# MUSH-related functions and variables

verbList = ['success', 'osuccess', 'asuccess', 'failure', 'ofailure', 'afailure']

def mushUnEscape(str):
	retStr = ""
	x = 0
	while x != len(str):
		if str[x] == "%":
			x += 1
			if str[x] == "%":
				retStr += "%"
			elif str[x] == "r":
				retStr += "\n"
			else:
				retStr += str[x]
		else:
			retStr += str[x]
		x += 1
	return retStr

def mushEscape(str):
	retStr = ""
	x = 0
	while x != len(str):
		if str[x] == "%":
			retStr += "%%"
		elif str[x] == "\n":
			retStr += "%r"
		else:
			retStr += str[x]
		x += 1
	return retStr


def saveToJson(fname, parent, rooms, exits, labels):
	fsave = QFile(fname)
	if not fsave.open(QIODevice.WriteOnly):
		raise IOError(fsave.errorString())

	stream = QTextStream(fsave)
	stream.setCodec('UTF-8')

	jroomList = []
	for i, room in rooms.items():
		jroomList.append({
		'id':i,
		'x':room.x,
		'y':room.y,
		'bcolor':room.bColor,
		'size':room.center,
		'name':room.name,
		'description':mushEscape(room.desc),
		'code':room.code
		})

	jexitList = []
	for i, exit in exits.items():
		jexitList.append({
		'id':i,
		'source':exit.source,
		'destination':exit.dest,
		'name':exit.name,
		'description':mushEscape(exit.desc),
		'alias':exit.alias,
		'verbs':exit.verbs
		})

	jlabelList = []
	for i, label in labels.items():
		jlabelList.append({
		'x':label.x,
		'y':label.y,
		'text':label.normalText
		})

	jmap = {
			'version':diggerconf.version,
			'width':parent.ui.scene.width(),
			'height':parent.ui.scene.height(),
			'bcolor':parent.bColor,
			'rooms':jroomList,
			'exits':jexitList,
			'labels':jlabelList
			}
	stream << json.dumps({'map':jmap}, indent = 4)

def saveToXml(fname, parent, rooms, exits, labels):
	fsave = QFile(fname)
	if not fsave.open(QIODevice.WriteOnly):
		raise IOError(fsave.errorString())
	stream = QTextStream(fsave)
	stream.setCodec("UTF-8")
	stream << ("<?xml version='1.0' encoding='UTF-8'?>\n" + "<!DOCTYPE DIGGER>\n" + "<DIGGER VERSION='%s'>\n" % (diggerconf.version))
	stream << ("<map width='%d' height='%d' bcolor='%s'>\n" % (parent.ui.scene.width(), parent.ui.scene.height(), parent.bColor))
	for i, room in rooms.items():
		stream << ("\t<room id='%d' x='%d' y='%d' bcolor='%s' size='%d'>\n" % (i, room.x, room.y, room.bColor, room.center))
		stream << "\t\t<name>" << escape(room.name) << "</name>\n"
		if room.desc != "":
			stream << "\t\t<description>" << mushEscape(escape(room.desc)) << "</description>\n"
		if room.code:
			for codeLine in room.code:
				stream << "\t\t<code>" << escape(codeLine) << "</code>\n"
		stream << "\t</room>\n"
	for i, exit in exits.items():
		stream << ("\t<exit id='%d' source='%d' destination='%d'>\n" % (i, exit.source, exit.dest))
		stream << "\t\t<name>" << escape(exit.name) << "</name>\n"
		if exit.desc != "":
			stream <<"\t\t<description>" << mushEscape(escape(exit.desc)) << "</description>\n"
		if exit.alias != "":
			stream << "\t\t<alias>" << escape(exit.alias) << "</alias>\n"
		stream << '\t\t<verbs>\n'
		for key, val, in exit.verbs.items():
			if val:
				stream << '\t\t\t<%s>%s</%s>\n' % (key, val, key)
		stream << '\t\t</verbs>\n'
		stream << "\t</exit>\n"
	for i, label in labels.items():
		stream << ("\t<label x='%d' y='%d'>" % (label.x, label.y))
		stream << escape(label.normalText)
		stream << "</label>\n"
	stream << "</map>\n</DIGGER>"

def generateCode(title, rooms, exits, labels):
	def isCode(codelist):
		if codelist:
			if codelist[0] == "" and len(codelist) == 1:
				return False
			return True
		return False
	strExport = "@@ Generated by Digger v" + diggerconf.version + "\n" + "@@ " + title + "\n"
	for k, room in rooms.items():
		strExport += "@dig/teleport " + room.name + "\n"
		if room.desc != "":
			strExport += "@desc here=" + mushEscape(str(room.desc)) + "\n"
		strExport += "think set(me, " + diggerconf.attributePrefix + str(k) + ":%l)\n"

	for k, room in rooms.items():
		sourceExits = []
		for j, exit in exits.items():
			if exit.source == k: # Select source exits
				sourceExits.append(exit)
		if isCode(room.code) or sourceExits:
			strExport += "@tel [v(" + diggerconf.attributePrefix + str(k) + ")]\n"
		for j in sourceExits:
			aliasString = ""
			if j.alias != "":
				aliasString += ";" + j.alias
			if j.dest != -1:
				strExport += "@open " + j.name + aliasString + "=[v(" + diggerconf.attributePrefix + str(j.dest) + ")]\n"
			else:
				strExport += "@open " + j.name + aliasString + "\n"
			if j.desc != "":
				strExport += "@desc " + j.name + "=" + mushEscape(str(j.desc)) + "\n"
			for verb, value in j.verbs.items():
				strExport += '@%s %s=%s\n' % (verb, j.name, value)
		if isCode(room.code):
			if diggerconf.enableImports:
				for codeLine in room.code:
					codeWords = codeLine.split()
					if codeWords[0] == "@@@" and codeWords[1] == "import":
						fname = str(" ".join(codeWords[2:]))
						if os.path.isfile(fname):
							strExport += "@@ Import file: " + fname + "\n"
							with open(str(fname), 'r') as codeFile:
								strExport += codeFile.read() + "\n"
						else:
							strExport += "@@ Import file: " + fname + " not found.\n"
					else:
						strExport += codeLine + "\n"
			else:
				for codeLine in room.code:
					strExport += codeLine + "\n"
	if diggerconf.clearAttributes:
		for k in rooms:
			strExport += "&" + diggerconf.attributePrefix  + str(k) + " me\n"
	if diggerconf.exportLabels:
		for k, label in labels.items():
			strExport += "think LABEL: *** " + label.normalText + " ***\n"
	return strExport

