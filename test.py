import requests
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

counter = 0

years = ['201901', '201902', '201903', '202001', '202002', "202003", "202101", "202102", "202103", "202201", "202202", "202203"]
url = "https://gw.its.yale.edu/soa-gateway/courses/webservice/v3/index"
auth = "l7bd270a3f771c47c8a15e46876de3a3d8"
majors = ['ACCT', 'USAF', 'AFAM', 'AFST', 'AKKD', 'ASL', 'AMST', 'GREK', 'ANTH', 'AMTH', 'APHY', 'ARBC', 'ARCG', 'ARCH', 'ARMN', 'ART', 'ASTR', 'BIOL', 'BENG', 'SBCR', 'BRST', 'BURM', 'CENG', 'CHEM', 'CHLD', 'CHNS', 'CLCV', 'CLSS', 'CGSC', 'LITR', 'CSEC', 'CPSC', 'CPAR', 'CZEC', 'DRST', 'DUTC', 'EPS', 'EALL', 'EAST', 'E&EB', 'ECON', 'EDST', 'EGYP', 'EENG', 'ENRG', 'ENAS', 'ENGL', 'ENVE', 'EVST', 'EP&E', 'ER&M', 'FILM', 'FNSH', 'F&ES', 'FREN', 'GMAN', 'GLBL', 'HLTH', 'HEBR', 'HNDI', 'HIST', 'HSAR', 'HSHM', 'HUMS', 'HMRT', 'HGRN', 'INDN', 'ITAL', 'JAPN', 'JDST', 'KHMR', 'SWAH', 'KREN', 'LAST', 'LATN', 'LING', 'MATH', 'MENG', 'MGRK', 'MMES', 'MTBT', 'MB&B', 'MCDB', 'MUSI', 'NAVY', 'NELC', 'NSCI', 'OTTM', 'PERS', 'PHIL', 'PHYS', 'PLSH', 'PLSC', 'PORT', 'PSYC', 'PNJB', 'RLST', 'ROMN', 'RSEE', 'RUSS', 'SKRT', 'SCIE', 'SNHL', 'SLAV', 'SOCY', 'SAST', 'SPAN', 'SPEC', 'S&DS', 'STCY', 'TAML', 'THST', 'DEVN', 'TBTN', 'TKSH', 'TWI', 'UKRN', 'URBN', 'VIET', 'WLOF', 'WGSS', 'YORU', 'ZULU']
#store subjectCode, courseNumber, distDesg, courseTitle
db = pd.DataFrame(columns=['subjectCode', 'courseNumber', 'distDesg', 'courseTitle'])
for year in years:
    for major in majors:
        params = {"apikey": auth, "subjectCode": major, 'termCode': year}
        x = requests.get(url, params=params)
        for i in x.json():
            counter += 1
            if counter % 100 == 0:
                print(counter)
            #add to db
            db = db.append({'subjectCode': i['subjectCode'], 'courseNumber': i['courseNumber'], 'distDesg': i['distDesg'], 'courseTitle': i['courseTitle']}, ignore_index=True)

#save to csv
db.to_csv("db.csv")

newdb = pd.read_csv("db.csv")
newdb = newdb.drop_duplicates()
#save to csv "courses.csv"
newdb.to_csv("courses.csv", index=False)

#read the courses.csv file and delete the first column
db = pd.read_csv("courses.csv")
# db = db.drop(columns=['Unnamed: 0'])
db = db.drop_duplicates()
#save to csv "courses.csv"
db.to_csv("courses.csv", index=False)
