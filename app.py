import csv
import os
from cs50 import SQL
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import psycopg2
import psycopg2.extras

UPLOAD_FOLDER = "static/images"

# Configure application
app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")

app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure database of series books and movies
db = SQL("postgresql://seriesbooksmovies_user:eeRYG1fTZxxukmG1js8qjdYskvP2pqkS@dpg-cgav6ot269v4ico9ug60-a/seriesbooksmovies")

db.execute("CREATE TABLE IF NOT EXISTS books (image TEXT, title TEXT, year INTEGER, author TEXT, acountry TEXT, acity TEXT, scountry TEXT, scity TEXT, description TEXT, character1 TEXT, character2 TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS movies (image TEXT, title TEXT, year INTEGER, screenwriter TEXT, acountry TEXT, acity TEXT, scountry TEXT, scity TEXT, description TEXT, cast1 TEXT, cast2 TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS series (image TEXT, title TEXT, year INTEGER, screenwriter TEXT, acountry TEXT, acity TEXT, scountry TEXT, scity TEXT, description TEXT, cast1 TEXT, cast2 TEXT, actualimage BYTEA)")
db.execute("CREATE TABLE IF NOT EXISTS results (image TEXT, title TEXT, year INTEGER, authorscreenwriter TEXT, acountry TEXT, acity TEXT, scountry TEXT, scity TEXT, description TEXT, charactercast1 TEXT, charactercast2 TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS reviews (title TEXT, review TEXT, rating INTEGER)")
db.execute("CREATE TABLE IF NOT EXISTS titles (title TEXT, category TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS countries (country TEXT)")

def first(text):

    sentence = []

    # https://codehandbook.org/python-capitalize-first-letter-of-all-sentences/

    for i in text.split('.'):

        sentence.append(i.lstrip().capitalize())

    return '. '.join(sentence)

@app.route("/", methods=["GET", "POST"])
def homepage():
    
    if request.method == "GET":

        db.execute("DELETE FROM countries")

        file = open("countries.csv", "r")
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            country = row
            db.execute("INSERT INTO countries (country) VALUES (?)", country)

        movies = db.execute("SELECT * FROM movies ORDER BY title ASC")
        books = db.execute("SELECT * FROM books ORDER BY title ASC")
        series = db.execute("SELECT * FROM series ORDER BY title ASC")
        
        return render_template("homepage.html", movies=movies, books=books, series=series)

    if request.method == "POST":
        
        title = request.form.get("title");
        print(f'{title}')

        results = db.execute("SELECT * FROM reviews WHERE title = ?", title)

        if results == []:

            error = "No Reviews Found"

            return render_template("reviews.html", error=error)

        return render_template("reviews.html", results=results)
    
@app.route("/search", methods=["GET", "POST"])
def search():

    if request.method == "GET":

        countries = db.execute("SELECT * FROM countries")

        return render_template("search.html", countries=countries)

    elif request.method == "POST":

        countries = db.execute("SELECT * FROM countries")

        db.execute("DELETE FROM results")

        search = request.form.get("type").title();

        if search == "City":

            city = request.form.get("city").title();

            db.execute("INSERT INTO results (image, title, year, authorscreenwriter, acountry, acity, scountry, scity, description, charactercast1, charactercast2) SELECT * FROM series WHERE acity = ? OR scity = ?", city, city)

            db.execute("INSERT INTO results (image, title, year, authorscreenwriter, acountry, acity, scountry, scity, description, charactercast1, charactercast2) SELECT * FROM movies WHERE acity = ? OR scity = ?", city, city)

            db.execute("INSERT INTO results (image, title, year, authorscreenwriter, acountry, acity, scountry, scity, description, charactercast1, charactercast2) SELECT * FROM books WHERE acity = ? OR scity = ?", city, city)

        elif search == "Country":

            country = request.form.get("country");

            db.execute("INSERT INTO results (image, title, year, authorscreenwriter, acountry, acity, scountry, scity, description, charactercast1, charactercast2) SELECT * FROM series WHERE acountry = ? OR scountry = ?", country, country)

            db.execute("INSERT INTO results (image, title, year, authorscreenwriter, acountry, acity, scountry, scity, description, charactercast1, charactercast2) SELECT * FROM movies WHERE acountry = ? OR scountry = ?", country, country)

            db.execute("INSERT INTO results (image, title, year, authorscreenwriter, acountry, acity, scountry, scity, description, charactercast1, charactercast2) SELECT * FROM books WHERE acountry = ? OR scountry = ?", country, country)

        results = db.execute("SELECT * FROM results ORDER BY title ASC")

        if results == []:

            error = "No Results Found"

            return render_template("search.html", error=error, results=results, countries=countries)

        return render_template("search.html", results=results, countries=countries)

@app.route("/submit", methods=["GET", "POST"])
def submit():

    if request.method == "GET":

        countries = db.execute("SELECT * FROM countries")

        titles = db.execute("SELECT * FROM titles ORDER BY title ASC")

        return render_template("submit.html", countries=countries, titles=titles)

    if request.method == "POST":

        category = request.form.get("type")
        title = request.form.get("title").title()
        year = request.form.get("year")
        author_country = request.form.get("Acountry")
        author_city = request.form.get("Acity").title()
        setting_country = request.form.get("Scountry")
        setting_city = request.form.get("Scity").title()
        description = first(request.form.get("description"))
        c = request.form.get("person").title()

        if category == "Movie":

            # https://roytuts.com/upload-and-display-image-using-python-flask/

            image = request.files['image2']
            filename = secure_filename(image.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(path)

            screenwriter = request.form.get("screenwriter").title()

            d = request.form.get("cast member").title()

            db.execute("INSERT INTO movies (image, title, year, screenwriter, acountry, acity, scountry, scity, description, cast1, cast2) VALUES (?,?,?,?,?,?,?,?,?,?,?)", path, title, year, screenwriter, author_country, author_city, setting_country, setting_city, description, c, d)
            
            db.execute("INSERT INTO titles (title, category) VALUES (?,?)", title, category)

        elif category == "Book":

            image = request.files['image']
            filename = secure_filename(image.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(path)

            author = request.form.get("author").title()

            d = request.form.get("character").title()

            db.execute("INSERT INTO books (image, title, year, author, acountry, acity, scountry, scity, description, character1, character2) VALUES (?,?,?,?,?,?,?,?,?,?,?)", path, title, year, author, author_country, author_city, setting_country, setting_city, description, c, d)

            db.execute("INSERT INTO titles (title, category) VALUES (?,?)", title, category)

        else:

            image = request.files['image3']
            filename = secure_filename(image.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(path)
            
            actualimage = image.read()

            screenwriter = request.form.get("screenwriter").title()

            d = request.form.get("cast member").title()

            db.execute("INSERT INTO series (image, title, year, screenwriter, acountry, acity, scountry, scity, description, cast1, cast2, actualimage) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", path, title, year, screenwriter, author_country, author_city, setting_country, setting_city, description, c, d, actualimage)

            db.execute("INSERT INTO titles (title, category) VALUES (?,?)", title, category)
            
        return render_template("thankyou.html", title=title)

@app.route("/review", methods=["GET", "POST"])
def review():

    if request.method == "GET":

        titles = db.execute("SELECT * FROM titles ORDER BY title ASC")

        return render_template("review.html", titles=titles)

    if request.method == "POST":

        title = request.form.get('title').title()

        text = first(request.form.get('text'))

        star = request.form.get('star')

        db.execute("INSERT INTO reviews (title, review, rating) VALUES (?, ?, ?)", title, text, star)

        return render_template("thankyoureview.html", title=title)

@app.route("/reviews", methods=["GET"])
def reviews():

    title = request.form.get('title')

    results = db.execute("SELECT * FROM reviews WHERE title = ?", title)

    if results == []:

        error = "No Reviews Found"

        return render_template("reviews.html", error=error)

    return render_template("reviews.html", results=results)