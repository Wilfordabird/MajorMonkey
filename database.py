"""Processes args into SQL command and queries data"""
from sqlite3 import connect
from contextlib import closing
import sqlite3
import sys
import json
from dataclasses import dataclass
from abc import ABC, abstractmethod

DEGREE_NAME = 0
REQUIREMENTS = 1
ELECTIVES = 2

@dataclass
class QueryArgs:
    """Collection of arguments for query calls"""
    subjectcode: str
    coursenum: str
    coursetitle: str

    def valid(self):
        """Determines whether the query has any valid informations"""

        if None in (self.subjectcode, self.coursenum, self.coursetitle):
            return False
        return True


class Database(ABC):

    def __init__(self):
        super().__init__()
        self._prepared_statements = []
        self._query_string = ""
        self._data = None

    @property
    def data(self):
        """Returns the data from the query"""
        return self._data

    def run_query(self):
        """Runs the query"""
        try:
            # Connect to database
            with connect('file:MajorMonkey.db?mode=rw', uri=True) as conn:
                with closing(conn.cursor()) as cursor:
                    # Insert course data
                    self.generate_query()
                    cursor.execute(self._query_string, self._prepared_statements)
                    self._data = cursor.fetchall()
        except sqlite3.DatabaseError as ex:
            print(ex, file=sys.stderr)
            print(self._prepared_statements, file=sys.stderr)
            sys.exit(1)

    @abstractmethod
    def generate_query(self):
        """Generates the SQL query string"""

class CourseInsert(Database):
    """Inserts course data into database"""

    def __init__(self, subjectcode, coursenum, distdeg, title):
        super().__init__()

        try:
            # Convert distdeg to json
            dist_json = json.dumps(distdeg)
        except TypeError:
            # If not a list, convert to list
            dist_json = json.dumps([])
            
        self._prepared_statements.extend([subjectcode, coursenum, dist_json, title])

    def insert(self):
        """Runs the query"""
        self.run_query()

    def generate_query(self):
        """Generates the query string"""
        self._query_string = "INSERT INTO courses VALUES (?, ?, ?, ?);"


class CourseSearch(Database):
    """Processes args into SQL command and queries data"""

    def __init__(self, args: QueryArgs):
        super().__init__()
        self.args = args

    def search(self):
        """Manages the execution of the SQL query"""
        self.run_query()

    def generate_query(self):
        """Generates the SQL query string based on user query args"""

        self._query_string = "SELECT subjectcode, coursenum, coursetitle, distdeg FROM courses "

        # Selection based on filters
        filters = vars(self.args)
        self._prepared_statements = []

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
                self._prepared_statements.append(f"%{filters[filter_name]}%")

        self._query_string += "ORDER BY subjectcode ASC, coursenum ASC;"

# -----------------------------------------------------------------------------

class UserSearch(Database):
    """Processes args into SQL command and queries data"""

    def __init__(self, username):
        super().__init__()
        self._prepared_statements.extend([username])

    @property
    def data(self):
        """Returns the data from the query"""
        if self._data:
            
            return json.loads(self._data[0][0])
        return self._data

    def search(self):
        """Manages the execution of the SQL query"""
        self.run_query()

    def generate_query(self):
        """Generates the SQL query string based on user query args"""
        self._query_string = "SELECT courses FROM users "
        self._query_string += "WHERE username = ?;"


class UserUpdate:
    """Processes args into SQL command and queries data"""

    def __init__(self, username, subjectcode, coursenum, insert=True):
        self._prepared_statements = []
        self._query_string = ""
        self._data = None
        
        self._subjectcode = subjectcode
        self._coursenum = coursenum
        self._insert = insert
        self._username = username

    def update(self):
        try:
            # Connect to database
            with connect('file:MajorMonkey.db?mode=rw', uri=True) as conn:
                with closing(conn.cursor()) as cursor:

                    # Fetch old course list
                    self.generate_search_query()
                    self._prepared_statements = [self._username]
                    cursor.execute(self._query_string, self._prepared_statements)
                    self._data = cursor.fetchall()

                    if self._data:
                        # User with pre-existing data, modify list!
                        self.generate_update_query()
                        course_string:str = self._data[0][0]

                        course_list:list = json.loads(course_string)

                        new_course = [self._subjectcode, self._coursenum]
                        if self._insert:
                            if new_course not in course_list:
                                course_list.append(new_course)
                        else:
                            if new_course in course_list:
                                course_list.remove(new_course)

                        course_list.sort()
                        self._prepared_statements = [json.dumps(course_list), self._username]

                    else:

                        # Cannot delete from non-existent list
                        if not self._insert:
                            return

                        # First time user, must insert new row!
                        self.generate_insert_query()
                        course_list = [[self._subjectcode, self._coursenum]]
                        self._prepared_statements = [self._username, json.dumps(course_list)]

                
                    cursor.execute(self._query_string, self._prepared_statements)

        except sqlite3.DatabaseError as ex:
            print(ex, file=sys.stderr)
            print(self._prepared_statements, file=sys.stderr)
            sys.exit(1)

    def generate_search_query(self):
        self._query_string = "SELECT courses FROM users WHERE username = ?;"

    def generate_update_query(self):
        self._query_string = "UPDATE users SET courses = ? WHERE username = ?;"


    def generate_insert_query(self):
        self._query_string = "INSERT INTO users VALUES (?, ?);"

# -----------------------------------------------------------------------------

class DegreeSearch(Database):
    """Processes args into SQL command and queries data"""

    def __init__(self):
        super().__init__()

    def search(self):
        """Manages the execution of the SQL query"""
        self.run_query()

    def generate_query(self):
        """Generates the SQL query string based on user query args"""
        self._query_string = "SELECT * FROM degrees ORDER BY degreename ASC;"

class DegreeInsert(Database):
    """Inserts degree data into database"""

    def __init__(self, degreename, requirements, electives):
        print("Inserting degree")
        print(degreename, requirements, electives)
        super().__init__()
        self._prepared_statements.extend([degreename, requirements, electives])

    def insert(self):
        """Runs the query"""
        self.run_query()

    def generate_query(self):
        """Generates the query string"""
        self._query_string = "INSERT INTO degrees VALUES (?, ?, ?);"

class RequisiteSearch(Database):
    """Processes args into SQL command and queries data"""

    def __init__(self, requisitename):
        super().__init__()
        # print("Requisite name:", requisitename)
        self._prepared_statements.append(requisitename)

    @property
    def data(self):
        """Returns the data from the query"""
        if self._data:
            return json.loads(self._data[0][0])
        return self._data


    def search(self):
        """Manages the execution of the SQL query"""
        self.run_query()

    def generate_query(self):
        """Generates the SQL query to search for requisites"""
        self._query_string = "SELECT (requisite) FROM requisites WHERE requisitename = ?;"

class RequisiteInsert(Database):
    """Inserts requisite data into database"""

    def __init__(self, requisitename, requisites):
        super().__init__()
        # print("Inserting requisite")
        print(requisitename, json.dumps(requisites))
        self._prepared_statements.extend([requisitename, json.dumps(requisites)])

    def insert(self):
        """Runs the query"""
        self.run_query()

    def generate_query(self):
        """Generates the query string"""
        print("About to insert requisite into database")
        # self._query_string = "DELETE FROM requisites WHERE TRUE;"
        self._query_string = "INSERT INTO requisites VALUES (?, ?);"