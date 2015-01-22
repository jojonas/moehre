import string
from collections import namedtuple

from PyQt5 import QtCore, QtWidgets, QtGui, uic

def camelCaseToWords(text):
	words = ""
	for char in text:
		if not char in string.ascii_uppercase:
			words += char
		else:
			words += " " + char.lower()
	return words.strip()
	
_Property = namedtuple("Property", ["name", "type", "value", "hasKnob", "hasEditable", "knob"])
def Property(name, type, value, *, hasKnob=False, hasEditable=True, knob=None):
	return _Property(name, type, value, hasKnob, hasEditable, knob)

class PropertyWidget(QtWidgets.QTableWidget):
	itemRolePropertyName = QtCore.Qt.UserRole + 1
	itemRolePropertyType = QtCore.Qt.UserRole + 2
	itemRolePropertyParse = QtCore.Qt.UserRole + 3
	
	def __init__(self, parent=None):
		QtWidgets.QTableWidget.__init__(self, parent)
		
		self.setColumnCount(2)
		self.setHorizontalHeaderLabels(["Property", "Value"])
		
		self.itemChanged.connect(self.propertyChanged)
		
		self._currentList = None
		
	def loadProperties(self, properties):
		self.clearContents()
		
		self._currentList = properties
		
		editables = [property for property in self._currentList.values() if property.hasEditable]
		self.setRowCount(len(editables))
		
		for i, property in enumerate(editables):
			if property.hasEditable:
				itemName = QtWidgets.QTableWidgetItem(camelCaseToWords(property.name))
				itemName.setFlags(itemName.flags() & ~QtCore.Qt.ItemIsEditable)
				self.setItem(i, 0, itemName)
				
				itemValue = QtWidgets.QTableWidgetItem(str(property.value))
				itemValue.setData(self.itemRolePropertyName, property.name)
				if property.hasKnob and property.knob.isConnected():
					itemValue.setText("<FROM GRAPH>")
					itemValue.setData(self.itemRolePropertyParse, False)
					itemValue.setFlags(itemName.flags() & ~QtCore.Qt.ItemIsEditable)
				else:
					itemValue.setData(self.itemRolePropertyParse, True)
					itemValue.setData(self.itemRolePropertyType, property.type)
					
				self.setItem(i, 1, itemValue)
						
		self.verticalHeader().hide()
		self.resizeColumnsToContents()
		
	def propertyChanged(self, item):
		if item.data(self.itemRolePropertyParse):
			name = item.data(self.itemRolePropertyName)
			type = item.data(self.itemRolePropertyType)
			if name and type:
				value = type(item.text())
				self._currentList[name] = self._currentList[name]._replace(value=value)
					
				