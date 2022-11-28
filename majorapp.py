"""Manages html pages"""
import ast
import urllib.parse as url
from html import escape
from datetime import datetime
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from database import (
    CourseSearch, QueryArgs, UserSearch, UserUpdate, DegreeSearch, RequisiteSearch,
    DEGREE_NAME, REQUIREMENTS, ELECTIVES
)

app = Flask(__name__, template_folder='templates')
app.secret_key = b'\xcdM\x8dA\xe1J\xbdOR\x9dMON\fK\xa3EY~/'

from auth import authenticate

# Helper Functions
# -----------------------------------------------------------------------------

def get_user_courses(username):
    """Returns a list of courses for a given user"""

    crn_add = request.args.get('crn_add')
    subj_add = request.args.get('subj_add')
    course_add = (subj_add, crn_add)

    crn_remove = request.args.get('crn_remove')
    subj_remove = request.args.get('subj_remove')
    course_remove = (subj_remove, crn_remove)

    if None not in course_add:
        client = UserUpdate(username, course_add[0], course_add[1])
        client.update()

    if None not in course_remove:
        client = UserUpdate(username, course_remove[0], course_remove[1], False)
        client.update()

    client = UserSearch(username)
    client.search()

    return client.data

def get_user_query():
    """Returns the user's query args: subj, crn, and title"""
    subj = request.args.get('subj')
    crn = request.args.get('crn')
    title = request.args.get('title')

    if None in (crn, subj, title):
        subj = request.cookies.get('prev_subj')
        crn = request.cookies.get('prev_crn')
        title = request.cookies.get('prev_title')

    return subj, crn, title

# -----------------------------------------------------------------------------


@app.route('/', methods=['GET'])
@app.route('/homepage', methods=['GET'])
def homepage():
    """Generates html for homepage"""

    # CaaS authenication
    username = authenticate()

    # Process search arguemnts
    subj, crn, title = get_user_query()
    # Process history of courses
    user_history = get_user_courses(username)

    # Fetches courses from database
    client = CourseSearch(QueryArgs(subj, crn, title))
    client.search()

    # Ignores courses that are already in user's history
    data = []
    for _subj, _crn, _title in client.data:
        if [_subj, _crn] not in user_history:
            data.append((_subj, _crn, _title))

    # Generate the html
    html = render_template('homepage.html',
            data=data,
            crn=crn if crn else "",
            subj=subj if subj else "",
            title=title if title else "",
            added_data=user_history)

    response = make_response(html)

    if None not in (subj, crn, title):
        response.set_cookie('prev_crn', crn)
        response.set_cookie('prev_subj', subj)
        response.set_cookie('prev_title', title)

    return response

@app.route('/major', methods=['GET'])
def major():
    """Determines the user's major and generates html"""

    username = authenticate()

    user_history = get_user_courses(username)

    print(user_history)

    client = DegreeSearch()
    client.search()

    best = []

    # Loop through all possible degrees
    for degree in client.data:
        print("CLIENT DATA - DEGREES TABLE")
        print(degree)
        print("----------------------------------")
        
        name = degree[DEGREE_NAME]
        requirements = degree[REQUIREMENTS]
        electives = degree[ELECTIVES]

        req_client = RequisiteSearch(requirements)
        req_client.search()
        ele_client = RequisiteSearch(electives)
        ele_client.search()

        req_courses = req_client.data[0]
        ele_courses = ele_client.data[0]
        print("REQ COURSES")

        #cut out the first character and last char of the string
        req_courses = req_courses[1][1:-1].replace("\"", "").replace("[", "").split("],")
        #remove ] from the last element
        req_courses[-1] = req_courses[-1][:-1]
        #strip each course of whitespace
        req_courses = [y.strip() for y in req_courses]
        print(req_courses)
        print("----------------------------------")
        print("ELE COURSES")
        #cut out the first character and last char of the string
        ele_courses = ele_courses[1][1:-1].replace("\"", "").replace("[", "").split("],")
        #remove ] from the last element
        ele_courses[-1] = ele_courses[-1][:-1]
        # strip every element of the list
        ele_courses = [x.strip() for x in ele_courses]
        print(ele_courses)
        print("----------------------------------")

        # TODO: Develop algorithm to determine best degree
        count = 0
        left_to_take = len(req_courses) + len(ele_courses)
        takencourses = []
        for i in user_history:
            takencourses.append(i[0] + ' ' + i[1])
        courses = req_courses + ele_courses
        for course in courses:
            if ',' not in course:
                if course in takencourses:
                    count += 1
                    left_to_take -= 1
            if ',' in course:
                course = course.split(',')
                if len(course) == 2:
                    if course[0] in takencourses or course[1] in takencourses:
                        count += 1
                        left_to_take -= 1
                elif len(course) == 3:
                    print(len(course))
                    if 'num' in course[1]:
                        #add course[3] to the to take
                        print(course[2].strip())
            #             left_to_take += int(course[2])
            #             #CHECK CONDITIONAL
                        
            #             if "==" and "skill" in course[2]:
            #                 print("CHECK IF COURSE HAS SAID SKILL")
                        
            #             if "<" in course [1]:
            #                 cond = course[1].split("<")
            #                 if "num" in cond[0]:
            #                     #CHECK IF a course in user history that isn't in anything else has a number less than the number in the condition
            #                     for i in takencourses:
            #                         if i not in courses:
            #                             if i.split(' ')[1] < cond[1]:
            #                                 count += 1
            #                                 left_to_take -= 1
            #                 else:
            #                     #CHECK IF a course in user history that isn't in anything else has a number higher than the skill in the condition
            #                     for i in takencourses:
            #                         if i not in courses:
            #                             if i.split(' ')[1] > cond[1]:
            #                                 count += 1
            #                                 left_to_take -= 1
            #             if ">" in course [1]:
            #                 cond = course[1].split(">")
            #                 if "num" in cond[0]:
            #                     #CHECK IF a course in user history that isn't in anything else has a number higher than the number in the condition
            #                     for i in takencourses:
            #                         if i not in courses:
            #                             if i.split(' ')[1] > cond[1]:
            #                                 count += 1
            #                                 left_to_take -= 1
            #                 else:
            #                     #CHECK IF a course in user history that isn't in anything else has a number less than the skill in the condition
            #                     for i in takencourses:
            #                         if i not in courses:
            #                             if i.split(' ')[1] < cond[1]:
            #                                 count += 1
            #                                 left_to_take -= 1
                    elif course[0] in takencourses or course[1] in takencourses or course[2] in takencourses:
                        count += 1
                        left_to_take -= 1

        if count > 0:
            best.append((name, count, left_to_take))

        # check if count is higher than the third one
        if len(best) > 3:
            best.sort(key=lambda x: x[1], reverse=True)
            best.pop()
        # Deal with complex requiesites (eg. 4 courses > 400 level)

        # Keep log of the degree with the least missing courses
        # Return the top 3 degrees

    # # Dummy example
    # best = [
    #     ["Computer Science BA", "7", "3"],
    #     ["Economics BA", "6", "6"],
    #     ["Mathematics BA", "3", "7"]
    # ]

    html = render_template('major.html',
            data=best,
            user_history=user_history)

    response = make_response(html)

    return response