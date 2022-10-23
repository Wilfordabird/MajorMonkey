"""Fetching course data"""

import warnings
import requests
import pandas as pd
from constants import MAJORS

warnings.simplefilter(action='ignore', category=FutureWarning)

YEARS = ['201901', '201902', '201903', '202001', '202002', "202003",
            "202101", "202102", "202103", "202201", "202202", "202203"]
URL = "https://gw.its.yale.edu/soa-gateway/courses/webservice/v3/index"
AUTH = "l7bd270a3f771c47c8a15e46876de3a3d8"

def main():
    """Queries yale api for course data to create a csv"""

    dateframe = pd.DataFrame(columns=['subjectCode', 'courseNumber', 'distDesg', 'courseTitle'])
    for year in YEARS:
        for major in MAJORS:
            params = {"apikey": AUTH, "subjectCode": major, 'termCode': year}
            response = requests.get(URL, params=params)
            for i in response.json():
                dateframe = dateframe.append({'subjectCode': i['subjectCode'],
                                            'courseNumber': i['courseNumber'],
                                            'distDesg': i['distDesg'],
                                            'courseTitle': i['courseTitle']},
                                            ignore_index=True)

    # save to csv and rm dups
    dateframe.to_csv("courses.csv", index=False)
    newdb = pd.read_csv("courses.csv")
    newdb = newdb.drop_duplicates()
    newdb.to_csv("courses.csv", index=False)

if __name__ == "__main__":
    main()
