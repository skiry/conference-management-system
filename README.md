# Conference Management System

Group project realized at Software Engineering in a team with another 2 members.

*How to run project

`cd` into `src/` and do:

1. `python3 manage.py makemigrations # create migrations for DB changes`
2. `python3 manage.py migrate # apply those changes to the DB`
3. `python3 manage.py runserver # and it'll open on localhost:8000`

It has many features, including different types of users and the actions they can perform according to the level of permissions, ie, the authors submitting proposals, the members of the Program Committee, the submissions' abstract and full papers proposed, meta-information about these, the deadlines for different phases of sending proposals, assigning paper to reviewers, evaluation deadline and announcing the results of paper valuation.
