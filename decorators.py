import inspect

_funcs = []

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
		elif parameter.annotation == inspect.Parameter.empty and parameter.default != inspect.Parameter.empty:
			raise ValueError("Data parameters may not have default values.")
	return func
	
def getRegisteredFunctions():
	return tuple(_funcs)

def printReport():
	for func in _funcs:
		signature = inspect.signature(func)
		print(func.__name__, signature)
