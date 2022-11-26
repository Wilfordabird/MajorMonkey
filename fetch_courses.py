"""Fetching course data"""

import warnings
import requests
import pandas as pd
from database import CourseInsert

warnings.simplefilter(action='ignore', category=FutureWarning)

# All the terms to be logged in the database
# YEARS = ['201901', '201902', '201903', '202001', '202002', "202003",
#             "202101", "202102", "202103", "202201", "202202", "202203"]

# Temporary for small scale testing
YEARS = ['202203']

COURSE_URL = "https://gw.its.yale.edu/soa-gateway/courses/webservice/v3/index"
SUBJ_URL = "https://gw.its.yale.edu/soa-gateway/course/webservice/v2/subjects"
AUTH = "l7bd270a3f771c47c8a15e46876de3a3d8"

def main():
    """Queries yale api for course data to create a csv"""

    # Initialize dataframe
    dateframe = pd.DataFrame(columns=['subjectCode', 'courseNumber', 'distDesg', 'courseTitle'])

    progress_index = 0

    # Loop through all majors and terms
    for year in YEARS:

        # First acquire all of the subjects within a given term
        subjects = []
        params = {"apikey": AUTH, "termCode": year, "mode": "json"}
        response = requests.get(SUBJ_URL, params=params)

        for subj in response.json():
            subjects.append(subj["code"])

        print(subjects)

        # Loop through all of the available subjects
        for subj in subjects:

            # Query Yale Courses Api
            params = {"apikey": AUTH, "subjectCode": subj, 'termCode': year}
            response = requests.get(COURSE_URL, params=params)

            # Parse courses response
            for course in response.json():

                progress_index += 1
                if progress_index % 100 == 0:
                    print(progress_index)

                # Data verification
                try:
                    assert course['subjectCode'] == subj
                    assert course['termCode'] == year
                    assert course['courseNumber'] != None
                    assert course['distDesg'] != None
                except AssertionError:
                    print('Data verification failed')
                    print(course)
                    continue

                # Saving data
                dateframe = dateframe.append({'subjectCode': course['subjectCode'],
                                            'courseNumber': course['courseNumber'],
                                            'distDesg': course['distDesg'],
                                            'courseTitle': course['courseTitle']},
                                            ignore_index=True)

    # Drop duplicate courses (eg. offered in multiple terms with same code and num)
    dateframe = dateframe.drop_duplicates(subset=['subjectCode', 'courseNumber'])

    # Save in json format (to maintain distDesg as a list)
    # Serves as a backup in case of database corruption
    dateframe.to_json('course_data.json')

    for _, row in dateframe.iterrows():
        course_client = CourseInsert(row['subjectCode'], row['courseNumber'], row['distDesg'], row['courseTitle'])
        course_client.insert()


if __name__ == "__main__":
    main()
