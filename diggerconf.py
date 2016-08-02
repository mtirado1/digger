import os

aliasDict = {}
roomCode  = []
roomColor = "#FF0000"
mapColor  = "#FFFFFF"

mapWidth  = 1065
mapHeight = 628

def loadConfigFile(): # Load and store configuration variables
	global aliasDict
	global roomCode
	global roomColor
	global mapColor
	global mapWidth
	global mapHeight
	fname = "digger.conf"
	if not os.path.exists(fname): # File exists?
		raise ValueError("Config file: " + fname  + " not found")
	with open(fname) as f:
		lines = f.readlines()
	for line in lines:
		words = line[:-1].split(" ")
		words = filter(None, words) # Remove empty elements
		if len(words) > 0: # Line is not empty
			if words[0] == "alias": # alias config option
				aliasDict[words[1]] = " ".join(words[2:]).split(";") # load alias list
			elif words[0] == "room_code": # Default room code
				roomCode.append(" ".join(words[2:]))
			elif words[0] == "room_color":
				roomColor = words[1]
			elif words[0] == "background_color":
				mapColor = words[1]
			elif words[0] == "width":
				mapWidth = int(words[1])
			elif words[0] == "height":
				mapHeight = int(words[1])

	print("Successfully loaded config options")
