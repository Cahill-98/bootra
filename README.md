# Bootra

A simple web app for **boo**k **tra**cking and monitoring your reading progress.

Submitted as the final project to CS50's Introduction to Computer Science course.

## Showcase

### Register and Login

*Image*

Keeps user's personal libraries and progress separate within different accounts.

### Homepage

*Image*

Lists the user's currently reading books followed by unread books with most recently started / added books at the top.

### Book Dashboard

##### On Target

*Image*

##### Not on Target

*Image*

##### No Target Set

*Image*

Set target date and receive an updating necessary daily page rate.
Get predicted completion date at your current reading speed for that book

### Add Books

*Image*

Used to add new books to your bookshelf. A checksum is performed on the ISBN number to make sure it is valid. *ISBN is used to get the book cover image.*

### History

*Image*

View a log of books read and daily pages read stats starting with the most recently finished books at the top. Get possible completion dates following daily reading time quotas.

### Database

*Image*

Stores main data for each book only once and links to the corresponding users through the *current* and *history* tables. When a book is finished, that user and book id pairing is transferred from *current* into *history*.

## Built With

* [Flask](https://palletsprojects.com/p/flask/)
* [Werkzeug](https://palletsprojects.com/p/werkzeug/)
* [Jinja](https://palletsprojects.com/p/jinja/)
* [Bootstrap](https://getbootstrap.com/)
* [SQLite](https://www.sqlite.org/index.html)

## Acknowledgements

* [CS50](https://www.edx.org/course/cs50s-introduction-to-computer-science)
* [Passlib](https://pypi.org/project/passlib/)
* [Open Library](https://openlibrary.org/developers/api)
* Extra?
