import json
import os

with open("mo_acs.json", "r", encoding="utf-8") as f:
	data = json.load(f)
	def cr_ac(name, email, password):
		new_data = {
			"name": name,
			"email": email,
			"password": password
		}
		return new_data