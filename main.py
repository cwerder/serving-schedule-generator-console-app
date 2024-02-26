import os
import requests
from bs4 import BeautifulSoup
import json
import warnings
import datetime
from errors import StartDateError
import pandas as pd
import xlsxwriter

from DTOs.MassDay import *
from DTOs.ServerProfile import *


def convert_dict_to_mass_days(mass_day_list_dict: list[dict]) -> list[MassDay]:
	return [MassDay(**mass_day) for mass_day in mass_day_list_dict]


def fetch_mass_schedule() -> list[MassDay]:
	warnings.filterwarnings("ignore")

	# Fetch HTML content from the webpage
	url = 'https://fsspx.today/chapel/fl-davie/'
	response = requests.get(url, verify=False)
	html_content = response.text

	# Parse HTML using BeautifulSoup
	soup = BeautifulSoup(html_content, 'html.parser')

	# Find the JSON string within the HTML (assuming it's embedded in a script tag)
	# Find all script tags
	script_tags = soup.find_all('script')

	# Search for the script tag containing the variable jsonDataPage
	for script_tag in script_tags:
		if 'jsonDataPage' in script_tag.text:
			# Extract the content of the variable jsonDataPage
			start_index = script_tag.text.find('{')
			end_index = script_tag.text.rfind('}')
			if start_index != -1 and end_index != -1:
				variable_value = script_tag.text[start_index:end_index + 1]
				result = json.loads(variable_value)
				return convert_dict_to_mass_days(result["massDays"])
			break
	else:
		print("No script tag containing variable jsonDataPage found.")
	print(f'Unable to fetch mass schedule. Error {e}')


def prompt_for_dates() -> tuple[float, float]:
	while True:
		try:
			# Attempt to parse the date string into a datetime object
			start_date = input("Please enter a start date (YYYY-MM-DD): ")
			# The user will be providing EST dates, but the system will be interpreting as UTC dates
			start_date_timestamp = datetime.datetime.strptime(start_date, '%Y-%m-%d').timestamp()
			print(f"start time {start_date_timestamp}")
			end_date = input("Please enter an end date (YYYY-MM-DD): (Note the end date is exclusive!) ")
			end_date_timestamp = datetime.datetime.strptime(end_date, '%Y-%m-%d').timestamp()
			print(f"end time {end_date_timestamp}")
			if start_date_timestamp > end_date_timestamp:
				raise StartDateError()
			return start_date_timestamp, end_date_timestamp
		except StartDateError as e:
			print(e)
		except ValueError:
			# If parsing fails (ValueError), print an error message and continue to the next iteration
			print("Invalid date format. Please enter the date in YYYY-MM-DD format.")


def get_masses_in_date_range(original_mass_days: list[MassDay], start_date: float, end_date: float) -> list[MassDay]:
	mass_dates_subset_result = [mass_day for mass_day in original_mass_days if start_date <= datetime.datetime.strptime(mass_day.dayYMD, '%Y-%m-%d').timestamp() <= end_date]
	return filter_for_masses(mass_dates_subset_result)


def convert_unix_timestamp(timestamp):
	# Convert Unix timestamp to a datetime object
	dt_object = datetime.datetime.fromtimestamp(timestamp)

	# Format the datetime object as per the specified format
	formatted_date = dt_object.strftime('%A, %B %d, %Y')

	return formatted_date


def write_to_table(server_assignments_inside: list[dict], date_range_input: tuple[float, float]):
	# Write the DataFrame to an Excel file
	excel_file = 'server_schedules/output.xlsx'  # Specify the name of your Excel file
	server_df = pd.DataFrame(server_assignments_inside)

	if os.path.exists(excel_file):
		os.remove(excel_file)

	# Create an Excel workbook and add a worksheet
	workbook = xlsxwriter.Workbook(excel_file)
	worksheet = workbook.add_worksheet('Mass Schedule')

	# Add title
	title = "Server Schedule"
	# https: // xlsxwriter.readthedocs.io / format.html  # format
	title_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'bg_color': 'white'})
	title_range = 'A1:N1'  # Assuming the table starts from A2
	worksheet.merge_range(title_range, title, title_format)

	# Add subtitle
	subtitle = f"{convert_unix_timestamp(date_range_input[0])} to {convert_unix_timestamp(date_range_input[1])}"
	subtitle_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 12})
	worksheet.merge_range('A2:N2', subtitle, subtitle_format)

	# Convert DataFrame to a list of lists
	data_list = server_df.values.tolist()

	# Add header formatting
	columns_format = workbook.add_format(
		{'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#4444FF', 'font_color': 'white'})

	for col_num, col_val in enumerate(server_df.columns.values):
		worksheet.write(2, col_num, col_val, columns_format)

	# Write data to the worksheet
	cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
	cell_format_blue = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bg_color': '#ADD8E6', 'border': 1})

	for row_num, row_data in enumerate(data_list):
		for col_num, value in enumerate(row_data):
			if row_num % 2 == 0:
				worksheet.write(3+row_num, col_num, value, cell_format_blue)
			else:
				worksheet.write(3+row_num, col_num, value, cell_format)

	worksheet.autofit()

	# Close the workbook
	workbook.close()

def get_date_from_timestamp(ts: float):
	dt_object = datetime.datetime.fromtimestamp(ts)

	# Get the weekday and month names
	weekday_name = dt_object.strftime("%A")
	month_name = dt_object.strftime("%B")

	# Format the string
	return f"{weekday_name}, {month_name} {dt_object.day}, {dt_object.year}"

def read_server_profiles(filename):
	try:
		with open(filename, 'r') as file:
			server_profiles_data = json.load(file)
			server_profiles: list[ServerProfile] = []
			for profile_data in server_profiles_data:
				profile = ServerProfile(
					profile_data['name'],
					profile_data['massesPositions'],
					profile_data['rolesAvailable'],
					profile_data['datesUnavailable'],
					profile_data['daysAvailable'],
					profile_data['timesAvailable'],
					profile_data['capacity']
				)
				server_profiles.append(profile)
			return server_profiles
	except FileNotFoundError as e:
		print(f"File '{filename}' not found.")
		raise e
	except json.JSONDecodeError as e:
		print(f"Error decoding JSON from file '{filename}'.")
		raise e


def select_server(server_set: set[str], position: str, server_profiles: list[ServerProfile], server_frequency: dict[str, int], mass_day: MassDay, mass: Mass) -> ServerProfile:
	return server_profiles[0]


def generate_mass_assignments(server_assignments_for_mass: dict[str, str], server_frequency: dict[str, int], mass_day: MassDay, mass: Mass) -> None:
	server_profiles = read_server_profiles('./db/ServerProfiles.json')

	server_positions: list[str] = ["Ac1", "Ac2", "MC", "Th", "Bb", "Cb", "Tb1", "Tb2", "Tb3", "Tb4"]
	server_set: set[str] = set()
	for position in server_positions:
		if position not in ("Ac1", "Ac2") and "low mass" in mass.description.lower():
			server_assignments_for_mass[position] = ""
		elif position not in ("Ac1", "Ac2", "MC", "Th") and "benediction" in mass.description.lower():
			server_assignments_for_mass[position] = ""
		else:
			selected_server = select_server(server_set, position, server_profiles, server_frequency, mass_day, mass)
			server_set.add(selected_server.name)
			server_assignments_for_mass[position] = selected_server.name

def generate_assignments(mass_days: list[MassDay], range_of_dates: tuple[float, float]) -> list[dict]:
	server_assignments_result: list[dict] = []
	server_frequency: dict[str, int] = {}
	for mass_day in mass_days:
		for mass in mass_day.masses:
			server_assignment_for_mass: dict = {}
			server_assignment_for_mass['Date'] = get_date_from_timestamp(datetime.datetime.strptime(mass_day.dayYMD, '%Y-%m-%d').timestamp())
			server_assignment_for_mass['Time'] = mass.time
			server_assignment_for_mass['Ceremony'] = mass.description
			if mass.description.lower() == "high mass":
				server_assignment_for_mass['Sacristan'] = "Rick"
			else:
				server_assignment_for_mass['Sacristan'] = "David/Richard"
				server_assignment_for_mass['Ac1'] = "CJ"
			generate_mass_assignments(server_assignment_for_mass, server_frequency, mass_day, mass)
			server_assignments_result.append(server_assignment_for_mass)
	return server_assignments_result


def filter_for_masses(mass_days_subset_internal: list[MassDay]) -> list[MassDay]:
	for key, value in enumerate(mass_days_subset_internal):
		filtered_for_masses: list[MassDay] = filter(
			lambda mass: any(keyword in mass.description.lower() for keyword in ("sung mass", "low mass", "benediction"))
			, mass_days_subset_internal[key].masses)
		mass_days_subset_internal[key].masses = list(filtered_for_masses)
	return list(filter(lambda mass_day: len(mass_day.masses) > 0, mass_days_subset_internal))


if __name__ == "__main__":
	print('✝️ Server Schedule Generator ✝️')
	print()
	try:
		all_mass_days: list[MassDay] = fetch_mass_schedule()
	except requests.exceptions.RequestException as e:
		print(f'Unable to fetch mass schedule. Error {e}')
		raise e
	# date_range = prompt_for_dates()
	# date_range = (1706813288, 1707590888)
	# GMT timestamp 1706832000 uses UTC on Friday at 12am
	date_range = (1705294800.0, 1709269200.0)
	mass_days_subset: list[MassDay] = get_masses_in_date_range(all_mass_days, date_range[0], date_range[1])

	server_assignments = generate_assignments(mass_days_subset, date_range)

	write_to_table(server_assignments, date_range)

	# print(f'mass day subset {mass_days_subset}')

	print('Server Schedule successfully generated! Please navigate to ./server_schedules/output.xlsx.')



