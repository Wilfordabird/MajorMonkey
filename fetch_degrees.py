"""Proccesses the data from the degrees csv into sql db"""

from database import DegreeInsert, RequisiteInsert
import pandas as pd
from sqlite3 import connect
import sqlite3
import re

def main():

    requirements = pd.read_csv("requirements.csv")

    # Loop through requirements
    for _, requirement in requirements.iterrows():
        requisitename = requirement[0]
        raw_requisite = requirement[1]

        #FORMAT:
            # [name, [list of requisites]]
            #course = [dept, num]
            #list of requisites:
            # regular prereq classes
            # [course, course, course]
            # when there are options to fufill the requisite
            # [course, [course or course], course]
            # when there are multiple options to fufill the requisite with a cond
            # [course, [course or course], [course, cond, 4]]
            # Must processes raw_requisite into a structured list format
            # split at a comma or ;
        clean_requisite = re.split(';|,', raw_requisite)
        #get rid of the last entry if it is empty
        if clean_requisite[-1] == '' or clean_requisite[-1] == ' ':
            clean_requisite = clean_requisite[:-1]

        #check for ors
        for i in range(len(clean_requisite)):
            clean_requisite[i] = clean_requisite[i].strip()
            #split it at an or
            dept_name = clean_requisite[i].split(' ')[0]
            clean_requisite[i] = re.split(' or ', clean_requisite[i])
            
            if len(clean_requisite[i]) > 1:
                #  print(clean_requisite[i])
                #split it at a space, and if it is only 1, then make the dept the same as the first part of the or
                for j in range(len(clean_requisite[i])):
                    if len(clean_requisite[i][j].split()) == 1:
                        clean_requisite[i][j] = dept_name + ' ' + clean_requisite[i][j]
                        print(clean_requisite[i][j])
                
                print(clean_requisite[i])
                for j in range(len(clean_requisite[i])):
                    clean_requisite[i][j] = clean_requisite[i][j].split()
                    print(clean_requisite[i][j])

            
    
        #check for * and conditions
        for i in range(len(clean_requisite)):
            for j in range(len(clean_requisite[i])):
                if '*' in clean_requisite[i][j]:
                    try:
                        mulitple = clean_requisite[i][j].split('*')[1].strip()
                    except IndexError: #if there is no number after the * it must be that you only take 1 course
                        mulitple = 1
                    try: #if there is a condition it is a dus class
                        condition = clean_requisite[i][j].split('where')[1].split(")")[0].strip()
                    except IndexError:
                        condition = "DUS"
                    dept = clean_requisite[i][j].split('num')[0].strip()
                    print(condition)
                    clean_requisite[i] = [dept, condition, mulitple]
                
    
        print(requisitename, clean_requisite)
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
    # run sql command to delete all entries in degrees and requiresites tables
    conn = sqlite3.connect('MajorMonkey.db')
    c = conn.cursor()
    c.execute("DELETE FROM Degrees;")
    c.execute("DELETE FROM Requisites;")
    conn.commit()
    conn.close()
    main()