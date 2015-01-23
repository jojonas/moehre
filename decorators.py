import inspect

_funcs = []
_outputFunctions = []

class ParameterType:
	def __init__(self, type, hasEditable=False, hasKnob=False):
		self.hasEditable = hasEditable
		self.hasKnob = hasKnob
		self.type = type
		
	def __call__(self, *args, **kwargs):
		return self.type(*args, **kwargs)
		
def StreamOnly(type): return ParameterType(type, hasEditable=False, hasKnob=True)		
def StreamOrProperty(type): return ParameterType(type, hasEditable=True, hasKnob=True)		
def PropertyOnly(type): return ParameterType(type, hasEditable=True, hasKnob=False)


def registerFunction(func):
	_funcs.append(func)
	signature = inspect.signature(func)
	for parameter in signature.parameters.values():
		if parameter.kind == inspect.Parameter.KEYWORD_ONLY:
			raise ValueError("Cannot wrap keyword arguments of function %s(...)" % func.__name__)
		elif parameter.kind == inspect.Parameter.VAR_POSITIONAL:
			raise ValueError("Cannot wrap argument lists of function %s(...)" % func.__name__)
		elif parameter.annotation != inspect.Parameter.empty and parameter.default == inspect.Parameter.empty:
			raise ValueError("Non data parameters must have default values.")
	return func

def registerOutputFunction(func):
	# Implemented as a output function list, even though just a single output function is allowed, because
	# in case it is decided to support multiple outputs, the implementation of this feature only requires
	# removing this check
	if _outputFunctions:
		raise TypeError("Output node function already registered (only one output allowed).")
	else:
		_outputFunctions.append(func)
	return registerFunction(func)
	
def getRegisteredFunctions():
	return tuple(_funcs)
	
def getRegisteredOutputFunctions():
	return tuple(_outputFunctions)

def printReport():
	for func in _funcs:
		signature = inspect.signature(func)
		print(func.__name__, signature)
