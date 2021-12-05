from re import I
from flask.wrappers import Request
from requests.models import encode_multipart_formdata
from uk_covid19 import Cov19API
import json
from global_vars import *
from covid_news_handling import news_API_request

with open('config.json') as file:
    config = json.load(file)


def parse_csv_data(csv_filename):
    covid_csv_data = []  # empty to list to put covid data strings created from each row
    covid_data_file = open(csv_filename, 'r')  # opens the file in reading mode
    for i in covid_data_file:
        row = i.strip()  # removes any unneed characters (e.g. white spaces) from each row to uncompliate later on
        covid_csv_data.append(row)

    return covid_csv_data


def process_covid_csv_data(covid_csv_data):
    """[summary]

    Args:
        covid_csv_data ([type]): [description]

    Returns:
        [type]: [description]
    """
    # get cases in last 7 days
    counter = 0
    last7days_cases = 0
    while counter < 7:
        day = covid_csv_data[counter + 2]  # getting data from rows 2 - 9
        # getting data between 6th and 7th commas on those rows
        last7days_cases = last7days_cases + \
            int(",".join(day.split(",", 7)[6:]))
        counter = counter + 1

    # current number of hostpital cases
    # intex is 1 as taking data from 2nd row, and extected between 5th and 6th comma in str
    current_hospital_cases = (",".join((covid_csv_data[1]).split(",", 6)[5:6]))

    # cumulative number of deaths
    # intex is 14 as taking data from 15th row, and extected between 4th and 5th comma in str
    total_deaths = (",".join((covid_csv_data[14]).split(",", 5)[4:5]))

    return last7days_cases, current_hospital_cases, total_deaths


def covid_API_request(location=config["l_location"], location_type=config["l_location_type"]):
    england_only = [
        'areaType='+location_type,
        'areaName='+location
    ]
    cases_and_deaths = {
        "date": "date",
        "areaName": "areaName",
        "areaCode": "areaCode",
        "newCasesByPublishDate": "newCasesByPublishDate",
        "newCasesBySpecimenDate": "newCasesBySpecimenDate",
        "cumCasesByPublishDate": "cumCasesByPublishDate",
        "cumDeaths28DaysByDeathDate": "cumDeaths28DaysByDeathDate",
        "hospitalCases": "hospitalCases",
        "cumDeaths28DaysByDeathDate": "cumDeaths28DaysByDeathDate"
    }

    api = Cov19API(filters=england_only, structure=cases_and_deaths)
    covid_json = api.get_json()
    covid_data = covid_json['data']
    return covid_data


def get_exeter_data():
    exeter_covid_dict = covid_API_request()
    last_7days_api = 0
    for i in range(0, 7):
        last_7days_api = last_7days_api + \
            int(exeter_covid_dict[i]["newCasesByPublishDate"])

    return last_7days_api


def get_nation_data():
    england_covid_dict = covid_API_request(
        config["n_location"], config["n_location_type"])

    last_7days_national_api = 0
    for i in range(0, 7):
        last_7days_national_api = last_7days_national_api + \
            int(england_covid_dict[i]["newCasesByPublishDate"])
    print(last_7days_national_api)

    x = 0
    checkH = False
    hospital_cases_api = 0
    while checkH == False:
        if england_covid_dict[x]["hospitalCases"] != None:
            hospital_cases_api += int(england_covid_dict[x]["hospitalCases"])
            checkH = True
        else:
            x += 1

    print(hospital_cases_api)

    p = 0
    checkD = False
    # print(england_covid_dict)
    cumdeaths_api = 0
    while checkD == False:
        if england_covid_dict[p]["cumDeaths28DaysByDeathDate"] != None:
            cumdeaths_api += int(england_covid_dict[p]
                                 ["cumDeaths28DaysByDeathDate"])
            checkD = True
        else:
            p += 1

    print(cumdeaths_api)

    return last_7days_national_api, hospital_cases_api, cumdeaths_api


def all_data():
    covid_data = []
    covid_data.append(get_exeter_data())
    covid_data.append(get_nation_data()[0])
    covid_data.append(get_nation_data()[1])
    covid_data.append(get_nation_data()[2])
    return covid_data
