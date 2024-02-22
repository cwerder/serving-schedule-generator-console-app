class MassDay:
	def __init__(self, day, dayTS, dayYMD, dayDMJ, dayATCFormat, masses):
		self.day = day
		self.dayTS = dayTS
		self.dayYMD = dayYMD
		self.dayDMJ = dayDMJ
		self.dayATCFormat = dayATCFormat
		self.masses = [Mass(**mass_data) for mass_data in masses]

	def __repr__(self):
		return self.day


class Mass:
	def __init__(self, time, timeATC, description, skip):
		self.time = time
		self.timeATC = timeATC
		self.description = description
		self.skip = skip
