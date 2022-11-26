"""Proccesses the data from the degrees csv into sql db"""

from database import DegreeInsert, RequisiteInsert
import pandas as pd

def main():

    requirements = pd.read_csv("requirements.csv")

    # Loop through requirements
    for _, requirement in requirements.iterrows():
        requisitename = requirement[0]
        raw_requisite = requirement[1]

        # TODO: Parse the requisite string into a list of lists!!!
        # Must processes raw_requisite into a structured list format
        clean_requisite = raw_requisite.split(";")

        requisite_client = RequisiteInsert(requisitename, clean_requisite)
        requisite_client.insert()

    degrees_df = pd.read_csv("degrees.csv")
    for _, degree in degrees_df.iterrows():
        degreename = degree[0]
        requirements = degree[1]
        electives = degree[2]
        degree_client = DegreeInsert(degreename, requirements, electives)
        degree_client.insert()

if __name__ == "__main__":
    main()