""" Helper functions for Bootra application.py

Section contents in alphabetical order.

SECTIONS:
    - Config
    - SQL Helper Functions
    - Other Helper Functions
"""

__author__ = "Jack Cahill"

#################################### CONFIG ###################################

import requests

from cs50 import SQL
from datetime import date, timedelta
from flask import session

db = SQL("sqlite:///library.db")


######################### SQL HELPER FUNCTIONS #########################

def delete_from_current(book_id):
    """
    Deletes book from users current table.

    Args:
        book_id (int): uniquely identifies with usre_id row to be deleted

    Returns:
        NONE
    """
    db.execute("DELETE FROM current WHERE book_id = ? AND user_id = ?",
               book_id, session["user_id"])


def current_to_history(book):
    """
    Removes book from users current and inserts into users history.

    Args:
        book (dict): contains data for book to be moved

    Returns:
        NONE
    """
    start_date = str_to_datetime(book["start_date"])
    end_date = date.today()
    days = (end_date - start_date).days + 1
    rate = book["pages"] / days

    db.execute("INSERT INTO history " \
               "(user_id, book_id, start_date, end_date, days, rate) " \
               "VALUES (?, ?, ?, ?, ?, ?)",
               session["user_id"], book["id"], start_date, end_date, days, rate)
    delete_from_current(book["id"])


def insert_into_current(book_id, target_date=None):
    """
    Inserts new row into current table.

    Args:
        book_id (int): uniquely identifies book to be inserted
        target_date (str): inserted if specified, NULL in table otherwise

    Returns:
        NONE
    """
    if target_date:
        db.execute("INSERT INTO current (user_id, book_id, target_date) " \
                   "VALUES (?, ?, ?)", session["user_id"], book_id, target_date)
    else:
        db.execute("INSERT INTO current (user_id, book_id) VALUES (?, ?)",
                   session["user_id"], book_id)


def new_book(book):
    """
    Inserts new row into books table.

    Args:
        book (dict): values for new book row

    Returns:
        NONE
    """
    db.execute("INSERT INTO books (title, author, pages, isbn) " \
               "VALUES (?, ?, ?, ?)",
               book["title"], book["author"], book["pages"], book["isbn"])


def new_user(username, password_hash):
    """
    Inserts new row into users table.

    Args:
        username (str)
        password_hash(str)

    Returns:
        NONE
    """
    db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
               username, password_hash)


def select_from_books(isbn):
    """
    Selects and returns data on a book with specific ISBN.

    Args:
        isbn (str): uniquely identifies book

    Returns:
        dict of book data if book in books table
        None if book not in table
    """
    book = db.execute("SELECT * FROM books WHERE isbn = ?", isbn)
    return book[0] if book else None


def select_from_current(book_id=None, isbn=None):
    """
    Selects and returns data of users books in current table.

    Args:
        book_id (int): for searching for specific book
        isbn (str): for searching for a specific book
        Selects all books in current if no args

    Returns:
        Dict of book data if book_id specified and book found
        None if book_id specified and book not found

        List of book data dicts if book_id not specified
            (empty list if no books found)
            Books ordered by most to least recently started
    """
    if book_id:
        book = db.execute("SELECT * FROM books JOIN current ON id = book_id " \
                          "WHERE id = ? AND user_id = ?",
                          book_id, session["user_id"])
        return book[0] if book else None
    elif isbn:
        book = db.execute("SELECT * FROM books JOIN current ON id = book_id " \
                          "WHERE isbn = ? AND user_id = ?",
                          isbn, session["user_id"])
        return book[0] if book else None
    else:
        return db.execute("SELECT * FROM books JOIN current ON id = book_id " \
                          "WHERE user_id = ? ORDER BY start_date DESC",
                          session["user_id"])


def select_from_history(order):
    """
    Selects and returns data of books in users history table.

    Args:
        order (str): SQL command specifiying order e.g. 'end_date DESC'

    Returns:
        List of book data dicts (empty list if no books found)
            Books ordered by most to least recently finished
    """
    return db.execute("SELECT * FROM books JOIN history ON id = book_id " \
                      f"WHERE user_id = ? ORDER BY {order}", session["user_id"])


def select_from_users(username):
    """
    Returns data on a user corresponding to input username.

    Args:
        username (str): unqiquely identifies user

    Return:
        dict of user data if user exists
        None if user doesn't exist
    """
    user = db.execute("SELECT * FROM users WHERE username = ?", username)
    return user[0] if user else None


def update_current(book_id, column, value):
    """
    Update value corresponding to specific column and row in current table.

    Args:
        book_id (int): uniquely identifies with user_id row to be updated
        column (str): column name in table of value to be updated
        value (str or int): the new value

    Returns:
        NONE
    """
    db.execute("UPDATE current SET ? = ? WHERE book_id = ? AND user_id = ?",
               column, value, book_id, session["user_id"])


def user_books():
    """
    Calculates users total books read.

    Args:
        NONE

    Returns:
        int of users total book count
    """
    return db.execute("SELECT COUNT(*) FROM history WHERE user_id = ?",
                      session["user_id"])[0]["COUNT(*)"]


def user_pages():
    """
    Calculates users total pages read.

    Args:
        NONE

    Returns:
        int of users total page count
    """
    history_pages = db.execute("SELECT SUM(pages) FROM books JOIN history " \
                               "ON id = book_id WHERE user_id = ?",
                               session["user_id"])[0]["SUM(pages)"]
    if history_pages is None:
        history_pages = 0

    current_pages = db.execute("SELECT SUM(page) FROM books JOIN current " \
                               "ON id = book_id WHERE user_id = ?",
                               session["user_id"])[0]["SUM(page)"]
    if current_pages is None:
        current_pages = 0

    return current_pages + history_pages


def user_rate(pages):
    """
    Calculates users average daily pages since starting their first book.

    Args:
        pages (int): users total page count

    Returns:
        int of users daily page rate rounded to nearest int
    """
    books = select_from_history("start_date ASC")
    if len(books) == 0:
        return 0

    # Books ordered by start date so first is earliest
    earliest_start = str_to_datetime(books[0]["start_date"])

    # +1 to count current day as whole day
    days = (date.today() - earliest_start).days + 1

    return round(pages / days)


######################## OTHER HELPER FUNCTIONS ########################

def append_progress(book):
    """
    Creates new progress percentage key, value pair a book.

    Args:
        book (dicts): contains data on the book to calculate progress for

    Returns:
        dict same as input with a new key, value 'progress' pair
            book['progress'] set to None if book hasn't been started yet
    """
    if book["page"]:
        book["progress"] = round((book["page"] / book["pages"]) * 100)
    else:
        book["progress"] = None

    return book


def calculate_date(pages, rate):
    """
    Calculates date to read a number of pages at a given rate starting tomorrow.

    Args:
        pages (int): pages left read
        rate (float): pages read per day rate

    Returns:
        date string in nice format e.g. Sat 15 Aug 2020
    """
    days = (pages / rate)
    if days.is_integer():
        days = int(days)
    else:
        days = int(days) + 1
    end_date = date.today() + timedelta(days=days)
    return end_date.strftime("%a %e %b %Y")


def calculate_rate(start_date, end_date, pages):
    """
    Calculates daily page reading rate across a defined period.

    Args:
        start_date (datetime): start of period to calculate rate for
        end_date (datetime): end of period to calculate rate for
        pages(int): number of page to read

    Return:
        float of reading rate
    """
    days = (end_date - start_date).days + 1
    return pages / days


def lookup_book(isbn):
    """
    Looks up data on book identified by ISBN using Open Library API.
    https://openlibrary.org/dev/docs/api/books

    Args:
        isbn (str)

    Returns:
        dict containing title, author and number of pages for the book
        None if an error is encountered
    """
    try:
        response = requests.get("https://openlibrary.org/api/books?" \
                                f"bibkeys=ISBN:{isbn}&format=json&jscmd=data")
        response.raise_for_status()
    except requests.RequestException:
        return None

    try:
        data = response.json()[f"ISBN:{isbn}"]
        return {
            "title": data["title"],
            "author": data["authors"][0]["name"],
            "pages": data["number_of_pages"],
            "isbn": isbn
        }
    except (KeyError, TypeError, ValueError):
        return None


def reformat_date(dictionary, key):
    """
    Reformats date into a nicer format. e.g. Sat 15 Aug 2020

    Args:
        dictionary (dict): contains date to be reformated
        key (str): key name of date to reformat

    Returns:
        dict same as input whith appropriate date reformated
    """
    if dictionary[key]:
        # Needs to be datetime type to use .strftime
        dictionary[key] = str_to_datetime(dictionary[key])
        dictionary[key] = dictionary[key].strftime("%a %e %b %Y")
    return dictionary


def str_to_datetime(str_date):
    """
    Converts string date into datetime date format.

    Args:
        str_date (str): of form 'YYYY-MM-DD'

    Returns:
        same date in datetime date form
    """
    list_date = str_date.split("-")
    return date(int(list_date[0]), int(list_date[1]), int(list_date[2]))


def valid_isbn(isbn):
    """
    Performs checksum on input ISBN-13 number.

    Args:
        isbn (str)

    Returns:
        True if input a valid ISBN-13
        False if input not a valid ISBN-13
    """
    try:
        # Calculate check_sum (x_0 + 3x_1 + x_2 + 3x_3 + ...)
        check_sum = 0
        for i, digit in enumerate(isbn):
            if i % 2 == 0:
                check_sum += int(digit)
            else:
                check_sum += int(digit) * 3

        if check_sum % 10 == 0 and len(isbn) == 13:
            return True
        else:
            return False
    except (TypeError, ValueError):
        return False