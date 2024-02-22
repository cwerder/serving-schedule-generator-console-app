import requests
from bs4 import BeautifulSoup
import json
import warnings
import datetime
from errors import StartDateError

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


if __name__ == "__main__":
	print('✝️ Server Schedule Generator ✝️')
	print()
	try:
		all_mass_days: list[MassDay] = fetch_mass_schedule()
	except requests.exceptions.RequestException as e:
		print(f'Unable to fetch mass schedule. Error {e}')
		raise e
	date_range = prompt_for_dates()
	# date_range = (1706813288, 1707590888)
	mass_day_subset = get_masses_in_date_range(all_mass_days, date_range[0], date_range[1])
	print(f'mass day subset {mass_day_subset}')



