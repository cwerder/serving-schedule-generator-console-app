class MassDay:
	def __init__(self, day, dayTS, dayYMD, dayDMJ, dayATCFormat, masses):
		self.day = day
		self.dayTS = dayTS
		self.dayYMD = dayYMD
		self.dayDMJ = dayDMJ
		self.dayATCFormat = dayATCFormat
		self.masses = [Mass(**mass_data) for mass_data in masses]

	def __str__(self, indent = 0):
		result = ""
		for key, value in vars(self).items():
			if isinstance(value, MassDay):
				result += " " * indent + f"{key}:\n"
				result += value.__str__(indent + 4)
			elif isinstance(value, (list, tuple, set)):
				result += " " * indent + f"{key}:\n"
				for item in value:
					if isinstance(item, MassDay):
						result += item.__str__(indent + 4)
					else:
						result += " " * (indent + 4) + str(item) + "\n"
			elif isinstance(value, dict):
				result += " " * indent + f"{key}:\n"
				for k, v in value.items():
					if isinstance(v, MassDay):
						result += v.__str__(indent + 4)
					else:
						result += " " * (indent + 4) + f"{k}: {v}\n"
			else:
				result += " " * indent + f"{key}: {value}\n"
		return result


class Mass:
	def __init__(self, time, timeATC, description, skip):
		self.time = time
		self.timeATC = timeATC
		self.description = description
		self.skip = skip

	def __str__(self, indent=0):
		result = ""
		for key, value in vars(self).items():
			if isinstance(value, Mass):
				result += " " * indent + f"{key}:\n"
				result += value.__str__(indent + 4)
			elif isinstance(value, (list, tuple, set)):
				result += " " * indent + f"{key}:\n"
				for item in value:
					if isinstance(item, Mass):
						result += item.__str__(indent + 4)
					else:
						result += " " * (indent + 4) + str(item) + "\n"
			elif isinstance(value, dict):
				result += " " * indent + f"{key}:\n"
				for k, v in value.items():
					if isinstance(v, Mass):
						result += v.__str__(indent + 4)
					else:
						result += " " * (indent + 4) + f"{k}: {v}\n"
			else:
				result += " " * indent + f"{key}: {value}\n"
		return result
