"""Processes args into SQL command and queries data"""
from sqlite3 import connect
from contextlib import closing
import sqlite3
import sys
from dataclasses import dataclass


@dataclass
class QueryArgs:
    """Collection of arguments for query calls"""
    subjectcode: str
    coursenum: str
    title: str

    def valid(self):
        """Determines whether the query has any valid informations"""

        if (self.coursenum is None and self.subjectcode is None and self.title is None):
            return False
        return True


class CourseSearch:
    """Processes args into SQL command and queries data"""

    def __init__(self, args: QueryArgs):

        self.args = args
        self._data = None
        self._query_string = ""
        self._prepared_values = []

        if not self.args.valid():
            return

        self.run_query()

    @property
    def data(self):
        """Returns the data in from RegLookup query"""
        return self._data

    def run_query(self):
        """Manages the execution of the SQL query"""

        try:
            with connect("file:reg.sqlite?mode=ro", uri=True) as conn:
                with closing(conn.cursor()) as crsr:
                    self.generate_query()
                    crsr.execute(self._query_string, self._prepared_values)
                    self._data = crsr.fetchall()

        except sqlite3.DatabaseError as ex:
            print(ex, file=sys.stderr)
            sys.exit(1)

    def generate_query(self):
        """Generates the SQL query string based on user query args"""

        self._query_string = """SELECT subjectcode, cast(coursenum as text), title FROM courses \
                                NATURAL JOIN departments NATURAL JOIN sections """

        # Selection based on filters
        filters = vars(self.args)
        self._prepared_values = []

        first_clause = True
        for filter_name in filters.keys():

            if filters[filter_name] is not None:

                # All clauses except first require "AND"
                if not first_clause:
                    self._query_string += 'AND '
                else:
                    first_clause = False
                    self._query_string += 'WHERE '

                self._query_string += filter_name
                self._query_string += " LIKE ? "

                # Save filter value in prepared statement list
                self._prepared_values.append(f"%{filters[filter_name]}%")

        self._query_string += "ORDER BY deptname ASC, coursenum ASC;"
