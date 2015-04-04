# Möhre

Möhre, a node based software synthesizer written in Python 3.

![Main Window Screenshot](https://raw.githubusercontent.com/jojonas/moehre/master/screenshots/main-window.png "Möhre Main Window")

## Usage
Start `mainwindow.py` using python: `python mainwindow.py`. The window consist of three main parts: a node view, a property view and a tool bar. Right click into the node view to create a new node of the specified type. Connect nodes by dragging an output knob to the input knob of another input node. Change node properties by clicking the node and editing in the "Node Properties" view. Delete a node by selecting it and pressing the Delete key. Delete a connection by right-clicking the output. There can only be one connection per input, but multiple per output.
	To play back any sample you have generated, connect something to the output node (which is always created first and cannot be deleted) and press the play button. You can save the Möhre-file using the floppy-disk-icon and open one using the folder icon. 
	The created samples can be exported using the checkmark button. They will be exported as Wave-file using the sample rate as specified as property of the output node.
![Usage Anmation](http://zippy.gfycat.com/BasicSmartJellyfish.gif "Möhre Usage Animation")

## Dependencies
* [PyQt5](http://www.riverbankcomputing.com/software/pyqt/download5)
* [PyOpenGL](http://pyopengl.sourceforge.net/)
* [PyAudio](http://people.csail.mit.edu/hubert/pyaudio/)
* [Numpy](http://www.scipy.org/scipylib/download.html)
* [SciPy](http://www.scipy.org/scipylib/download.html)

## Platforms
It has only been tested yet using Windows, although it should generally be platform-indpendent and as such work on Linux and Mac OS X, too.

## License
This project is released under MIT license. 
Copyright (c) 2015 Jonas Lieb, Joel Schumacher.
