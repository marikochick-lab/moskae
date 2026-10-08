def Check(a, opr, b):
	if opr == ">" :
		if a > b :
			return "Правда"
		else:
			return "Ложь"
	if opr == "<" :
		if a < b :
			return "Правда"
		else:
			return "Ложь"
	if opr == "=" :
		if a == b :
			return "Правда"
		else:
			return "Ложь"