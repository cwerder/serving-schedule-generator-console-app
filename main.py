import os
import requests
from bs4 import BeautifulSoup
import json
import warnings
import datetime
from errors import StartDateError
import pandas as pd
from pandas.io.excel import ExcelWriter

from DTOs.MassDay import MassDay


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
	# script_tags = soup.find_all('script')
	# json_data = None
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
			end_date = input("Please enter an end date (YYYY-MM-DD): ")
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
	return [mass_day for mass_day in original_mass_days if start_date <= mass_day.dayTS <= end_date]


def create_excel_writer(filename: str, engine: str = 'xlsxwriter') -> ExcelWriter:
	return pd.ExcelWriter(filename, engine=engine)


def convert_unix_timestamp(timestamp):
	# Convert Unix timestamp to a datetime object
	dt_object = datetime.datetime.fromtimestamp(timestamp)

	# Format the datetime object as per the specified format
	formatted_date = dt_object.strftime('%A, %B %d, %Y')

	return formatted_date


def write_to_table(mass_days: list[MassDay], date_range_input: tuple[float, float]):
	# Write the DataFrame to an Excel file
	excel_file = 'server_schedules/output.xlsx'  # Specify the name of your Excel file
	sheet_name = 'Sheet1'  # Specify the name of the sheet in the Excel file
	# Define your data
	data = [
		{'Day': 'Monday', 'Time': '10:00 AM', 'Ceremony': 'Meeting'},
		{'Day': 'Tuesday', 'Time': '2:00 PM', 'Ceremony': 'Presentation'},
		{'Day': 'Wednesday', 'Time': '1:30 PM', 'Ceremony': 'Training'},
		{'Day': 'Thursday', 'Time': '11:00 AM', 'Ceremony': 'Seminar'}
	]

	# Create a DataFrame from the data
	server_df = pd.DataFrame(data)

	if os.path.exists(excel_file):
		os.remove(excel_file)  # Delete the existing file

	with create_excel_writer(excel_file) as writer:
		# Write the DataFrame to an Excel sheet
		server_df.to_excel(writer, sheet_name='Ceremony Schedule', index=False, startrow=2)

		# Get the workbook and the sheet
		workbook = writer.book
		worksheet = writer.sheets['Ceremony Schedule']

		# Add title
		title = "Server Schedule"
		# https: // xlsxwriter.readthedocs.io / format.html  # format
		title_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'bg_color': 'red'})
		title_range = 'A1:C1'  # Assuming the table starts from A2
		worksheet.merge_range(title_range, title, title_format)

		# Add subtitle
		subtitle = f"{convert_unix_timestamp(date_range_input[0])} to {convert_unix_timestamp(date_range_input[1])}"
		subtitle_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 12, 'bg_color': 'red'})
		worksheet.merge_range('A2:C2', subtitle, subtitle_format)

		# Add header formatting
		header_format = workbook.add_format(
			{'bold': True, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#4444FF', 'font_color': 'white'})
		for col_num, value in enumerate(server_df.columns.values):
			worksheet.write(2, col_num, value, header_format)

		worksheet.set_column('A:A', 15)  # Day column
		worksheet.set_column('B:B', 15)  # Time column
		worksheet.set_column('C:C', 20)  # Ceremony column

		# Add alternating row colors
		blue_format = workbook.add_format({'bg_color': '#08f0f7'})

		for row_num in range(3, len(server_df) + 3):  # Start from row 3, skipping the header, title, and column rows
			if row_num % 2 != 0:
				worksheet.set_row(row_num, None, blue_format)

if __name__ == "__main__":
	print('✝️ Server Schedule Generator ✝️')
	print()
	try:
		all_mass_days: list[MassDay] = fetch_mass_schedule()
	except requests.exceptions.RequestException as e:
		print(f'Unable to fetch mass schedule. Error {e}')
		raise e
	# date_range = prompt_for_dates()
	date_range = (1706813288, 1707590888)
	mass_days_subset: list[MassDay] = get_masses_in_date_range(all_mass_days, date_range[0], date_range[1])

	write_to_table(mass_days_subset, date_range)

	print(f'mass day subset {mass_days_subset}')



