# MajorMonkey

## Group Members:
Gabriel Dos Santos, EJ Wilford, Alex Romero-Ruffo, and John Sedrak

## Introduction:
Our final project for CPSC 437 Introduction to Databases is a major calculator called MajorMonkey. It provides users with the ability to select courses they have taken throughout their time at Yale and find the major with the least amount of courses remaining! This is especially useful for students who have taken a wide variety of courses and want to figure out what to major in.

## Basic architecture:
MajorMonkey is a web application built using Flask in Python. The majorapp manages communication between the user and the databases of courses and major requirements. This is done through well-defined classes which interface with the database making all of the relevant queries. The database tier of the product uses SQLite3 as the database engine. The view tier uses basic html/css to display courses and major results.

## Features:
Users are able to log in to MajorMonkey using CaaS/NetId. This enables the backend to keep track of users and their course history. Therefore users can return to the web application and always have their added history saved.

Once a student takes a course, they can add it to their course history using the course search functionality. The search bar dynamically creates a complex SQL statement with “AND”s, “LIKE”s, and “ORDER BY” to find the courses in question. Thereafter, users can easily add or remove courses from their list.

Finally, once all of the relevant courses have been logged, students can find a major match! A complex algorithm runs through the user history and all major requirements to find the most optimal majors the student can complete.

## Data Description & Cleaning:
For the courses, we queried the Yale API to find a list of all courses offered at the university. We then stored the relevant fields being title, name, number, and distributional category in our database. This allows users to type in partial information of a course they have taken and we will find all courses that have any matching fields.

For the major requirements, we had to manually generate the data from the Yale major requirements pages. This involved human parsing of web pages to copy and paste relevant course requirements for each major. Then the raw data would be processed into a well-defined list that included scenarios for complex course requirements such as “6 CPSC courses in the 400 level”. We also decided to split up requirements and electives into different fields in order to reduce redundancy when there are degrees with the same core requirements such as EP&E Concentration in Economics vs EP&E Concentration in Politics.

## Technical Challenges:
We faced challenges creating the algorithm to determine whether a taken course fulfilled a major requirement. This was due to issues like double counting a course into multiple categories or improper parsing through nested lists of course requirement data. Through printing out course matches and running edge cases we were able to resolve this issue and acquire the proper number of remaining major courses. In the future we plan to address issues with course numbers that aren't pure integers like "HIST 101J" so that the algorithm can properly count and compare them.
