def MathResult(a, oper, b):
	if oper == "+" :
		rslt = a + b
		return rslt
	elif oper == "-" :
		rslt = a - b
		return rslt
	elif oper == "/" :
		rslt = a / b
		return rslt
	elif oper == "*" :
		rslt = a * b
		return rslt
	else:
		return "Invalid operation"