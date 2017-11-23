import os

version = "1.3.1"

aliasDict = {}
roomCode  = []
roomColor = "#FF0000"
mapColor  = "#FFFFFF"
attributePrefix = "ROOM.ID."

mapWidth  = 1065
mapHeight = 628
roomSize = 31
roomCenter = 15

enableImports = False
monospaceEdit = True
exportLabels = False
clearAttributes = True
exportType = "xml"

def toBoolean(str):
	return str == "True"

def loadConfigFile(export): # Load and store configuration variables
	global aliasDict
	global roomCode
	global roomColor
	global mapColor
	global mapWidth
	global mapHeight
	global enableImports
	global monospaceEdit
	global exportLabels
	global clearAttributes
	global exportType
	global attributePrefix
	global roomSize
	global roomCenter
	fname = "digger.conf"
	if (not os.path.exists(fname)) and not export: # File exists?
		print("Config file " + fname + " not found. Using default values")
	else:
		with open(fname) as f:
			lines = f.readlines()
		for line in lines:
			words = line[:-1].split(" ")
			words = list(filter(None, words)) # Remove empty elements
			if len(words) > 0: # Line is not empty
				if words[0] == "alias": # alias config option
					aliasDict[words[1]] = " ".join(words[2:]).split(";") # load alias list
				elif words[0] == "room_code": # Default room code
					roomCode.append(str(" ".join(words[1:])))
				elif words[0] == "room_color":
					roomColor = words[1]
				elif words[0] == "background_color":
					mapColor = words[1]
				elif words[0] == "width":
					mapWidth = int(words[1])
				elif words[0] == "height":
					mapHeight = int(words[1])
				elif words[0] == "enable_imports":
					enableImports = toBoolean(words[1])
				elif words[0] == "monospace_edit":
					monospaceEdit = toBoolean(words[1])
				elif words[0] == "export_labels":
					exportLabels = toBoolean(words[1])
				elif words[0] == "attr_prefix":
					attributePrefix = words[1]
				elif words[0] == "clear_attrs":
					clearAttributes = toBoolean(words[1])
				elif words[0] == "export_type":
					exportType = words[1]
				elif words[0] == "room_size":
					size = int(words[1])
					if size % 2 != 0:
						size += 1
					roomSize = size
					roomCenter = (size - 1) / 2
	if not export:
		print("Successfully loaded config options")
