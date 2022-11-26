"""Manages html pages"""

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
            crn=crn,
            subj=subj,
            title=title,
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

    client = DegreeSearch()
    client.search()

    best = []

    # Loop through all possible degrees
    for degree in client.data:
        name = degree[DEGREE_NAME]
        requirements = degree[REQUIREMENTS]
        electives = degree[ELECTIVES]

        req_client = RequisiteSearch(requirements)
        req_client.search()
        ele_client = RequisiteSearch(electives)
        ele_client.search()

        req_courses = req_client.data
        ele_courses = ele_client.data

        # Determine how many requisites are satisfied given user's history

        # TODO: Develop algorithm to determine best degree

        # This could potentially remove the unique required courses? Needs to be tested
        # Eg. Comp Sci. BA requires CPSC 201. CPSC 201 in user_history so removes it from req_courses
        req_courses = [course for course in req_courses if course not in user_history]
        ele_courses = [course for course in ele_courses if course not in user_history]
        
        # Deal with complex requiesites (eg. 4 courses > 400 level)

        # Keep log of the degree with the least missing courses
        # Return the top 3 degrees

    # Dummy example
    best = [
        ["Computer Science BA", "7", "3"],
        ["Economics BA", "6", "6"],
        ["Mathematics BA", "3", "7"]
    ]

    html = render_template('major.html',
            data=best,
            user_history=user_history)

    response = make_response(html)

    return response