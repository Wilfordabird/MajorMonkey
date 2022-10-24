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

    crn_add = request.args.get('crn_add')
    subj_add = request.args.get('subj_add')
    title_add = request.args.get('title_add')

    added_history = request.cookies.get('added_history')
    if added_history is None:
        added_history = ""

    # Fetch added courses
    if crn_add is not None:
        new_entry = f"({subj_add},{crn_add},{title_add})"
        added_history += new_entry

    # Process added courses string into table
    added_data = []
    if added_history:
        for i in added_history.split(")"):
            try:
                i = i.split("(")
                added_data.append(tuple(i[1].split(",")))
            except IndexError:
                pass

    searchdata = CourseSearch(QueryArgs(subj, crn, title)).data
    data = []
    for entry in searchdata:
        if entry not in added_data:
            data.append(entry)


    html = render_template('homepage.html',
            data=data,
            added_data=added_data)

    response = make_response(html)

    if crn is not None:
        response.set_cookie('prev_crn', crn)
        response.set_cookie('prev_subj', subj)
        response.set_cookie('prev_title', title)

    response.set_cookie('added_history', added_history)

    return response
