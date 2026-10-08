VEROS = 0.1
NAMEOS = "MarikOS"
pres = ["SyntaxError", "ArgError"]
def mo_error(pr, des):
	if not pr in pres:
		print(f"PRER Name {pr} not defined")
	else:
		print(f"""MarikOS Error:
{pr}: {des}""")

def npr_moe(name):
	pres.append(name)