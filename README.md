# Serving-Schedule-Generator-Console-App

## Description
The purpose of this application is to easily generate a serving schedule. The user passes in the starting and ending dates and the application gets the list of ceremonies for those dates and randomly assigns servers to each ceremony based on a number of constraints.


## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#Architecture)
- [Nice-to-Haves](#Nice-to-Haves)

## Installation
There are two ways two install and run the application.
- Run via Python
    - Run `pip install -r requirements.txt` to install all dependencies
    - Run `python3 main.py`

- Run via executable
    - If you don't already have the executable, run `pyinstaller server-schedule-generator.spec`
    - Navigate to `dist`. You will find the `server-schedule-generator` binary available to run.


## Usage
This application is only as useful as the data in `db/ServerProfiles.json` since the application keys off that to know which servers are available for a given mass.
Every server has the following properties:
1. **name** - Name of server. It should be unique to avoid confusion.
2. **lowMassLevels** - Low Mass roles the server can perform.
3. **highMassLevels** - High Mass roles the server can perform.
4. **datesUnavailable** - Dates the server is unavailable.
5. **daysAvailable** - Days the server is available
6. **sundayTimesAvailable** - Sundays are a special case and the only day we consider the time at which the server is available.
7. **capacity** - How many times a server should be scheduled. Note that is does not consider time duration. For now, I've set 3 for every server with the expectation that these schedules will be generated monthly. What this means is that no server will be scheduled for more masses than they have capacity for.

Once this JSON file is properly tuned, schedule generation is fairly straightforward. It still requires that you inspect before converting to a PDF. For instance, when the application does not assign servers for Benediction. As such, you will see **No Server Assigned** values for those cells. The expectation is that the user manually assign them. This is pretty straightforward though since you can just assign servers from the pool that will serve the mass following Benediction.

When updating the ServerProfiles.json, try to keep the same casing as what I've already used (eg 'Ac1', not 'ac1'). While I've tried to keep it case-invariant, I'm sure cases can be found where this breaks the application in certain places unless the casing follows the convention I've established. Just follow my example data and you should be fine.


## Architecture
I've described below at a high level how this application works.

1. Fetches mass schedule available at https://fsspx.today/chapel/fl-davie/. Parses the response for the JSON specifying the mass schedule. Note that there doesn't appear to be a way to specify a date range.
2. Prompts user for start and end dates. This is required to establish a date range for the ceremonies that need servers assigned to them.
3. Generate server assignments. This is done by reading the data in /db/ServerProfiles.json to get the constraints for each server so it knows which servers are eligible for each mass. From there, it randomly selects from the pool of available servers and adds them to a dataframe.
4. Write the dataframe to an Excel file located in the `/server_schedules` directory. The file uses a YYYY-MM-DD.xlsx naming convention. From there, the expectation is that the user checks the schedule and makes any adjustments as needed before publishing to the servers. Note that if you have trouble when converting from xlsx to pdf format where it creates multiple pdf pages, you can fix this by going to `Page Layout` > `Page Setup` in Excel and selecting `Fit to One Page`.


## Nice-to-Haves
1. Store server profiles in a DB instead of on JSON.
2. Have a site where the users can enter their availability instead of having to reach out to the Serving Coordinator.
3. Have a notifications system that notifies servers the day before they are supposed to serve.


