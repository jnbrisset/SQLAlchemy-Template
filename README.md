# SQLAlchemy-template

SQLAlchemy-template is a template for a SQLAlchemy implementation, which is mostly copied from SQLAlchemy version 1.3 documentation and put into a single python script for an easy import to a project.

As explained in Session Basics on SQLAlchemy documentation, it is strongly suggested to limit the scope of the session to manipulate or query the data. 
In this spirit, ```contextmanager``` was used to create a ```session_scope()``` when interaction with the database is needed. If an exception is raised, the session will roll back to the original database at the start of the session. The session will also closed at the end of the transaction.

In the session_scope(), there are a few examples of common transactions. This part of the file should be deleted or put in comments in order to quickly reference to them, if need be.

## Installation
Confirm that SQLAlchemy package is installed. 

Clone this repository to your project in order to import.

## Usage
The database is created in memory. In order to save it to a file, replace ":memory:" with the path to the database file.

There are five examples of tables given: a main table, a one-to-many table, one unassociative table, and 2 many-to-many tables.
You can inspire yourself from the structure of those tables to create your own tables needed for your project.

The ```session_scope()``` of the file should be deleted by the end of the project. In case you would like to keep a quick reference to transaction examples, you should put in comments that section such that it doesn't interact with the database.

In the script where the transactions will take place:
```python
from sqlalchemy-template import session_scope()

with session_scope() as session:
    # Include your session transactions here.
```

## Contributing
Pull and push requests are welcome for adding common transactions that you believe that would be useful to users as a quick reference. If there are any changes before the provided examples, in the core of the file, please provide a description of the change.

## Acknowledgement
Most of the code is from SQLAlchemy documentation, so all credits are given to the authors of the documentation.

## License
[MIT](https://choosealicense.com/licenses/mit/)
