class ServerProfile:
	def __init__(self, name, mass_positions, roles_available, dates_unavailable, days_available, times_available, capacity):
		self.name = name
		self.mass_positions = mass_positions
		self.roles_available = roles_available
		self.dates_unavailable = dates_unavailable
		self.days_available = days_available
		self.times_available = times_available
		self.capacity = capacity
