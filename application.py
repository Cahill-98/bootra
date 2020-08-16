""" Bootra

A simple web app for book tracking and monitoring your reading progress.

Submitted as the final project to CS50's Introduction to Computer Science
course.

This script contains the initial setup and the routes.
Needs the helpers.py script to run.

SECTIONS:
    - Config
    - Login Required Routes
    - Login, Register, Logout Routes
"""

__author__ = "Jack Cahill"

#################################### CONFIG ###################################

from datetime import date
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from functools import wraps
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import *

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def login_required(f):
    """Decorate routes to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


############################ LOGIN REQUIRED ROUTES ############################

@app.route("/")
@login_required
def index():
    """
    The main homepage for displaying the users current library of books.
    Data shown is title, author, start date, current page, total pages and a
    percentage progress bar.

    GET:
        Selects users current books from database.
        Reformats dates for nicer displaying.
        Calculates progress percentages for books for progress bars.
        Renders index.html template.
    """
    books = select_from_current()
    for book in books:
        reformat_date(book, "start_date")
        append_progress(book)

    return render_template("index.html", books=books)


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """
    History page for displaying the users books read history and lifetime stats.
    Data shown on each book is title, author, start date, finished date, days
    to read, pages and daily page rate.
    Lifetime stats are total books, total pages and average daily page rate.

    POST:
        Reached through /book page when a book is completed.
        Transfers book from current table to history table for that user.
        Redirects user back to homepage.

    GET:
        Selects users book history from database.
        Reformats dates for nicer displaying.
        Calculates user lifetime stats.
        Renders history.html template.
    """
    if request.method == "POST":

        book_id = request.form.get("book_id")
        book = select_from_current(book_id)

        if book["start_date"] is None:
            flash("You haven't started this book yet!")
            return redirect(url_for("book", book_id=book_id))

        current_to_history(book)
        flash("Congratulations! You have just completed " + book["title"] + ".")
        return redirect("/")

    # GET method
    else:
        books = select_from_history(order="end_date DESC")
        for book in books:
            reformat_date(book, "start_date")
            reformat_date(book, "end_date")

        stats = {"books": user_books(), "pages": user_pages()}
        stats["rate"] = user_rate(stats["pages"])
        return render_template("history.html", books=books, stats=stats)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """
    Page with form for adding book to user's current table.

    POST:
        Reached through /add page when form submitted.
        Checks inputs are valid.
        Looks up book info and inserts new row into books table if it is a new
        book.
        Insert new row into current linking the current user and the book.
        Redirects user to homepage.

    GET:
        Renders add.html template.
    """
    if request.method == "POST":

        isbn = request.form.get("isbn")
        target = request.form.get("target")

        if not valid_isbn(isbn):
            flash("Please enter a valid ISBN!")
            return render_template("add.html")

        book_in_current = select_from_current(isbn=isbn)
        if book_in_current:
            flash("This book is already in your current!")
            return render_template("add.html")

        in_books = select_from_books(isbn)
        if not in_books:
            book_info = lookup_book(isbn)
            if book_info:
                new_book(book_info)
                book_id = select_from_books(isbn)["id"]
            else:
                flash("Sorry, we were unable to find that book!")
                return render_template("add.html")
        else:
            book_id = in_books["id"]

        if target:
            insert_into_current(book_id, target)
        else:
            insert_into_current(book_id)
        return redirect("/")

    # GET method
    else:
        # Todays date used as min date in add.html
        tomorrow = str(date.today() + timedelta(days=1))
        return render_template("add.html", tomorrow=tomorrow)


@app.route("/book", methods=["GET", "POST"])
@login_required
def book():
    """
    Display dashboard for current book with estimated completion dates at
    different rates.
    Also displays book info such as title, author, date started as well as
    cover image.
    Info and cover image from Open Library API.
    https://openlibrary.org/dev/docs/api/books

    POST:
        Reached through /book page when target date is updated.
        Current table is updated with new target date.

    GET:
        Calculates the needed rates and dates and redners the book template.
        dates['current'] the completion date if continued at rates['current].
        rates['target'] is rate needed to reach target completion date.
        dates['15min'], dates['30min'], dates['1hour'] completion dates when
        reading for 15min, 30min and 1 hour resp. daily.
    """
    if request.method == "POST":

        book_id = request.form.get("book_id")
        target = request.form.get("target")

        if target is None:
            flash("Please enter a date!")
            return redirect(url_for("book", book_id=book_id))

        update_current(book_id, "target_date", target)
        return redirect(url_for("book", book_id=book_id))

    # GET method
    else:
        book_id = request.args.get("book_id")
        book = select_from_current(book_id)
        append_progress(book)
        pages_left = book["pages"] - book["page"]
        today = date.today()
        tomorrow = today + timedelta(days=1)
        dates = {}
        rates = {}

        if book["start_date"]:
            # start_date stored as datetime for calculations
            start_date = str_to_datetime(book["start_date"])
            reformat_date(book, "start_date")
            rates["current"] = calculate_rate(start_date, today, book["page"])
            dates["current"] = calculate_date(pages_left, rates["current"])
        else:
            rates["current"] = dates["current"] = None

        if book["target_date"]:
            # target_date stored as datetime for calculations
            target_date = str_to_datetime(book["target_date"])
            reformat_date(book, "target_date")
            # Reset target date to NULL if reached
            if (target_date - today).days < 1:
                update_current(book_id, "target_date", None)
                rates["target"] = None
                flash("Target date has been reset!")
            else:
                rates["target"] = calculate_rate(tomorrow, target_date, pages_left)
        else:
            rates["target"] = None

        dates["15min"] = calculate_date(pages_left, 11)
        dates["30min"] = calculate_date(pages_left, 22)
        dates["1hour"] = calculate_date(pages_left, 44)

        # Tomorrow is min date for target date, used in book.html
        dates["tomorrow"] = str(tomorrow)
        return render_template("book.html", book=book, rates=rates, dates=dates)


@app.route("/remove", methods=["POST"])
def remove():
    """
    Removes a book from the users current books.

    POST:
        Reached through /book page when the remove button is clicked.
        Removes the book corresponding to the book_id of the page
        the user is currently on.
        Redirects user back to homepage.
    """
    book_id = request.form.get("book_id")
    delete_from_current(book_id)
    return redirect("/")


@app.route("/update", methods=["POST"])
def update():
    """
    Updates users current page number for a book.

    POST:
        Reached through /book page when update button clicked.
        Updates current table with new page number entered.
        If first update then start date is set as today.
        Reloads the same book page with updated page number.
    """
    page = request.form.get("page")
    book_id = request.form.get("book_id")

    if page is None:
        flash("Please enter a page number to update!")
        return redirect(url_for("book", book_id=book_id))

    try:
        page = int(page)
    except:
        flash("Please enter an integer for the page number!")
        return redirect(url_for("book", book_id=book_id))

    start_date = select_from_current(book_id)["start_date"]
    if start_date is None:
        update_current(book_id, "start_date", str(date.today()))

    update_current(book_id, "page", page)
    return redirect(url_for("book", book_id=book_id))


######################## LOGIN, REGISTER, LOGOUT ROUTES #######################

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Log in page for returning users.

    GET:
        Renders login.html template.

    POST:
        Reached through /login page when Log In button clicked.
        Checks user exists and password is correct then remembers their id
        before redirecting to the homepage logged in.
    """
    # Forget any user id
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if None in [username, password]:
            flash("Please provide a username and password!")
            return render_template("login.html")

        user = select_from_users(username)
        if user is None or not check_password_hash(user["hash"], password):
            flash("Invalid username and/or password!")
            return render_template("login.html")

        session["user_id"] = user["id"]
        return redirect("/")

    # GET method
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """
    Logs current user out.

    GET:
        Clears user_id from session.
        Redirects to login page.
    """
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Page where new user can register.

    POST:
        Reached through /register page when Sign Up button clicked.
        Checks username not taken and passwords match.
        Inserts new row in the user table for the new user.
        Redirects to homepage

    GET:
        Renders the register.html template.
    """

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if None in [username, password, confirmation]:
            flash("Please provide a username and password!")
            return render_template("register.html")

        name_taken = select_from_users(username)
        if name_taken:
            flash("Username already taken!")
            return render_template("register.html")

        if password != confirmation:
            flash("Passwords must match!")
            return render_template("register.html")

        password_hash = generate_password_hash(password)
        new_user(username, password_hash)
        user = select_from_users(username)
        session["user_id"] = user["id"]
        return redirect("/")

    # GET method
    else:
        return render_template("register.html")