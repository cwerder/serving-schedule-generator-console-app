class StartDateError(Exception):
	def __str__(self):
		return "Start date is ahead of end date. Please try again."
