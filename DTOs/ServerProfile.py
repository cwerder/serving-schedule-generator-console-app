class ServerProfile:
	def __init__(
				self,
				name,
				low_mass_levels,
				high_mass_levels,
				benediction_levels,
				dates_unavailable,
				days_available,
				sunday_times_available,
				capacity):
		self.name = name
		self.low_mass_levels = low_mass_levels
		self.high_mass_levels = high_mass_levels
		self.benediction_levels = benediction_levels
		self.dates_unavailable = dates_unavailable
		self.days_available = days_available
		self.sunday_times_available = sunday_times_available
		self.capacity = capacity
