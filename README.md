# Bootra

A simple web app for **boo**k **tra**cking and monitoring your reading progress.

Submitted as the final project to CS50's Introduction to Computer Science course.

## Showcase

### Homepage

![Homepage screenshot](/screenshots/home.png)

Lists the user's currently reading and unread books with most recently started at the top.

### Book Dashboard

##### On Target

![On target book dashboard](/screenshots/book_on_target.png)

##### Not on Target

![Not on target book dashboard](/screenshots/book_off_target.png)

##### No Target Set

![No target book dashboard](/screenshots/book_add_target.png)

Set target date and receive the daily page rate required to hit that target. Also get predicted completion dates when reading at your current rate, 15 mins daily, 30 mins daily or 1 hour daily.

### Add Books

![Add book screenshot](/screenshots/add_book.png)

Used to add new books to your bookshelf. A checksum is performed on the ISBN number to make sure it is valid. Book information and covers is looked up using the Open Library API.

### History

![History screenshot](/screenshots/history.png)

View a log of books read with their respective daily page rates starting with the most recently finished books at the top. Also get users lifetime stats for total books and pages and lifetime average daily pages.

### Register and Login

![Login screenshot](/screenshots/login.png)

Keeps user's personal libraries and progress separate within different accounts. Passwords hashed before stored.

### Database

![Database diagram](/screenshots/database.png)

Stores main data for each book only once and links to the corresponding users through the *current* and *history* tables. When a book is finished, that unique user and book id pairing is transferred from *current* into *history*.

## Built With

* [Flask](https://palletsprojects.com/p/flask/)
* [Jinja](https://palletsprojects.com/p/jinja/)
* [Bootstrap](https://getbootstrap.com/)
* [SQLite](https://www.sqlite.org/index.html)

## Acknowledgements

* [CS50](https://www.edx.org/course/cs50s-introduction-to-computer-science)
* [Open Library](https://openlibrary.org/developers/api)