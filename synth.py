from decorators import *

@registerFunction
def foo(data, x, y:int=0):
	print("Bar", x)
	
@registerFunction
def bar(koko, loo, aa, pepe:str="popo", nana:int=0):
	pass
	
@registerFunction
def bar2(koko, loo, aa, pepe:str="popo", nana:int=0):
	pass
	
@registerFunction
def bar3(koko, loo, aa, pepe:str="popo", nana:int=0):
	pass

@registerOutputFunction
def Output(input):
	pass
	
