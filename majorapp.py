"""Manages html pages"""

import urllib.parse as url
from html import escape
from datetime import datetime
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from course_search import CourseSearch, QueryArgs

app = Flask(__name__, template_folder='templates')

@app.route('/', methods=['GET'])
@app.route('/homepage', methods=['GET'])
def homepage():
    """Generates html for homepage"""

    crn = request.args.get('crn')
    subj = request.args.get('subj')
    title = request.args.get('title')

    if crn is None:
        crn = request.cookies.get('prev_crn')
        subj = request.cookies.get('prev_subj')
        title = request.cookies.get('prev_title')

    print("THE QUERY!")
    print(subj, crn ,title)

    crn_add = request.args.get('crn_add')
    subj_add = request.args.get('subj_add')

    crn_remove = request.args.get('crn_remove')
    subj_remove = request.args.get('subj_remove')
    course_remove = (subj_remove, crn_remove)

    added_history = request.cookies.get('added_historys')
    if added_history is None:
        added_history = ""

    # Fetch added courses
    if crn_add is not None:
        new_entry = f"({subj_add},{crn_add})"
        added_history += new_entry

    # Process added courses string into table
    added_data = []
    if added_history:
        for i in added_history.split(")"):
            try:
                i = i.split("(")
                course = tuple(i[1].split(","))
                # Process remove request
                if course == course_remove:
                    continue
                added_data.append(course)
            except IndexError:
                pass


    searchdata = CourseSearch(QueryArgs(subj, crn, title)).data
    data = []

    print(subj, crn ,title)

    print(added_data)
    print(searchdata)
    for _subj, _crn, _title in searchdata:
        if (_subj, _crn) in added_data:
            continue
        data.append((_subj, _crn, _title))


    html = render_template('homepage.html',
            data=data,
            added_data=added_data)

    response = make_response(html)

    if crn is not None:
        response.set_cookie('prev_crn', crn)
        response.set_cookie('prev_subj', subj)
        response.set_cookie('prev_title', title)

    # Stringify history
    stringed_history = ""
    for _subj, _crn in added_data:
        stringed_history +=  f"({_subj},{_crn})"

    response.set_cookie('added_historys', stringed_history)

    return response
