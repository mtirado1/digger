# Digger
Design MUSH worlds through a graphical interface.

This is a program to design, edit and save MUSH worlds (rooms, exits) using a graphical interface, without requiring any softcoding skills.

Digger can export worlds to [PennMUSH](https://github.com/pennmush/pennmush),
[RhostMUSH](https://github.com/RhostMUSH/trunk), and
[TinyMUX](https://github.com/brazilofmux/tinymux)  mushcode.

* * *

![Alt](media/example.png "Example capture")

## Features

* Create, edit and describe individual rooms.

	* Rooms can be color coded

	* Execute custom mushcode on rooms

	* Import mushcode files to your worlds

* Connect rooms with exits

	* Custom aliases

* No mushcode required

* Exports to XML, JSON, and mushcode

* Labels

	* Add titles; store notes, TODOs, and more.

	* Labels can be exported as messages to the player


## Running

To run Digger, you need to install python3 on your system and the Qt4 Library.

On Ubuntu:

`sudo apt-get install python-qt4`

`python3 main.py`
