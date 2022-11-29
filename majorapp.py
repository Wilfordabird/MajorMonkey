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

def courses_2_go(reqs, elec):
    courses = 0
    for req in reqs:
        if len(req) == 1:
            courses += 1
        else:
            if type(req[1]) != list:
                num = req[2]
                courses += int(num)
            else:
                courses += 1

    for req in elec:
        if len(req) == 1:
            courses += 1
        else:
            if type(req[1]) != list:
                num = int(req[2])
                courses += num
            else:
                courses += 1

    return courses


def inmajor(reqs, course):
    if reqs == None:
        return []
    res = reqs
    for req in reqs:
        # handle if there is just a single course
        if len(req) == 1:
            check = req[0].split()
            if course == check:
                res.remove(req)
                return res
        else:
            if type(req[1]) != list:
                
                dept_name = req[0]
                cond = req[1]
                mult = int(req[2])
                # # req is an elective with a condition
                # print("Condition")
                if "<" in cond:
                    # if there are 2 < in the condition
                    if cond.count("<") == 1:
                        course_num = course[1]
                        course_dept = course[0]
                        nnum = cond.split("<")[1].strip()
                        try:
                            num = int(nnum)
                        except:
                            print(nnum)
                            print(cond)

                        if course_dept == dept_name and course_num < num:
                            mult -= 1
                            res.remove(req)
                            if mult > 0:
                                newreq = (dept_name, cond, mult)
                                res.append(newreq)
                            return res
                    else:
                        course_num = course[1]
                        course_dept = course[0]
                        lownum = cond.split("<")[0].strip()
                        highnum = cond.split("<")[2].strip()
                        try:
                            low = int(lownum)
                            high = int(highnum)
                        except:
                            print(lownum)
                            print(highnum)
                            print(cond)
                        
                        if course_dept == dept_name and course_num < high and course_num > low:
                            mult -= 1
                            res.remove(req)
                            if mult > 0:
                                newreq = (dept_name, cond, mult)
                                res.append(newreq)
                            return res
                elif ">" in cond:
                    course_num = int(course[1])
                    course_dept = course[0]
                    nnum = cond.split(">")[1].strip()
                    try:
                        num = int(nnum)
                    except:
                        print(cond)
                        print(nnum)
                    if course_dept == dept_name and course_num > int(num):
                        mult -= 1
                        res.remove(req)
                        if mult > 0:
                            newreq = (dept_name, cond, mult)
                            res.append(newreq)
                        return res
                elif "DUS" in cond:
                    mult -= 1
                    res.remove(req)
                    if mult > 0:
                        newreq = (dept_name, cond, mult)
                        res.append(newreq)
                    return res
                elif "==" in cond:
                    # CHECK the equals of a skill
                    course_num = course[1]
                    course_dept = course[0]
                    skill = cond.split("==")[1].strip()
                    print(skill)
                    if skill == "HU":
                        coursese = CourseSearch(QueryArgs(course_dept, course_num, ""))
                        coursese.search()
                        if "YCHU" in coursese.data[0][3]:
                            mult -= 1
                            res.remove(req)
                            if mult > 0:
                                newreq = (dept_name, cond, mult)
                                res.append(newreq)
                            return res
                    elif skill == "SO":
                        coursese = CourseSearch(QueryArgs(course_dept, course_num, ""))
                        coursese.search()
                        print(coursese.data[0][3])
                        if "YCSO" in coursese.data[0][3]:
                            mult -= 1
                            res.remove(req)
                            if mult > 0:
                                newreq = (dept_name, cond, mult)
                                res.append(newreq)
                            return res
                    else:
                        print("ERROR: Skill not found")
                    return res
            else:
                # it is an or statement and each needs to be checked
                for r in req:
                    if len(r) == 1:
                        r = r[0].split()
                        if course == r:
                            res = reqs.remove(req)
                            return res
    return res
        
            

@app.route('/major', methods=['GET'])
def major():
    """Determines the user's major and generates html"""

    username = authenticate()
    user_history = get_user_courses(username)
    print("User history")
    print(user_history)
    print("------------------")

    client = DegreeSearch()
    client.search()


    
    best = []

    # Loop through all possible degrees
    for degree in client.data:
        
        
        name = degree[DEGREE_NAME]
        requirements = degree[REQUIREMENTS]
        electives = degree[ELECTIVES]

        print(name)
        print("----------------------------------")

        req_client = RequisiteSearch(requirements)
        req_client.search()
        ele_client = RequisiteSearch(electives)
        ele_client.search()

        req_courses = req_client.data
        ele_courses = ele_client.data

        count = 0
        amount_to_take = courses_2_go(req_courses, ele_courses)

        req_to_go = req_courses
        elc_to_go = ele_courses

        # run search with 
        for course in user_history:
            req_to_go = inmajor(req_to_go, course)
            elc_to_go = inmajor(elc_to_go, course)
        
        amount_still_to_take = courses_2_go(req_to_go, elc_to_go)

        # see if it is in the three lowest to take
        if len(best) < 3:
            best.append((name, amount_to_take - amount_still_to_take, amount_still_to_take))
        else:
            for i in range(len(best)):
                if amount_still_to_take < best[i][2]:
                    best[i] = (name, amount_to_take - amount_still_to_take, amount_still_to_take)
                    break

    html = render_template('major.html',
            data=best,
            user_history=user_history)

    response = make_response(html)

    return response