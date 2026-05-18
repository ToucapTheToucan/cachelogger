from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os

# Create a Flask application object.
# __name__ tells Flask where this file is; it uses that to find templates, static files, etc.
app = Flask(__name__)

# Where uploaded images will be stored (static/uploads)
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# app.config is a dictionary-like object that holds settings

#Configuring where flask stores files and the max length of each file
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024 # 16 MB max file size

# sqlalchemy_database_uri represents where the database lives
# sqlite:////geocaches.db means that we're using sqlite and storing data in geocaches.db
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///geocaches.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#Binds SQLAlchemy to my flask app
db = SQLAlchemy(app)

class Geocache(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    found_date = db.Column(db.Date) # Stored as text in SQLite but as a proper date with SQLAlchemy
    image_filename = db.Column(db.String(255)) # Stores image filename in static/uploads

# Checks if geocaches.db exists yet and creates it if not
with app.app_context():
    db.create_all()

# Define a *route*: which URL should trigger which function.
@app.route("/")
def home():
    # Whatever this function returns is sent back as the HTTP response body.
    # This line fetches all the geocaches from the DB (queries all the geocaches)
    geocaches = Geocache.query.all()

    # Pass geocaches into the template
    return render_template("home.html", geocaches=geocaches)

@app.route("/add", methods=["GET", "POST"])
def add_cache():
    if request.method == "POST":
        name = request.form["name"]
        latitude = float(request.form["latitude"])
        longitude = float(request.form["longitude"])
        notes = request.form.get("notes", "")

        found_date_str = request.form.get("found_date") # e.g. "2025-12-17"
        # Converts string into Python date object
        found_date = datetime.strptime(found_date_str, "%Y-%m-%d").date()

        # Handling uploaded file
        photo = request.files.get("photo")
        image_filename = None

        if photo and photo.filename: # makes sure user actually selects a file
            #Clean the filename
            filename = secure_filename(photo.filename)

            #Could avoid collisions here late by adding timestamp or UUID
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            # Writes file to satic/uploads/filename
            photo.save(save_path)

            image_filename = filename

        # Setting up a new row for our DB from the data from the request
        new_cache = Geocache(
            name=name,
            latitude=latitude,
            longitude=longitude,
            notes=notes,
            found_date=found_date,
            image_filename=image_filename, # may be None if no photo
        )
        
        # first line marks the new_cache to be inserted, 2nd line writes the changes to the db
        db.session.add(new_cache)
        db.session.commit()

        return redirect(url_for("home"))
    
    return render_template("add_cache.html")

# This block runs only if you do 'python app.py'
if __name__ == '__main__':
    # debug=True gives you nice error pages and auto-reload when you edit code
    app.run(debug=True)







# Original def home(): code
   # Orignal Code: return "Hello, geocaching!"
    # New Code:
    # geocaches = [
    #     {
    #         "name": "MTRPcache1",
    #         "latitude": 47.1234,
    #         "longitude": -122.5678,
    #         "notes": "Nice view over the valley."
    #     },
    #     {
    #         "name": "Riverside Mystery",
    #         "latitude": 47.2234,
    #         "longitude": -122.6678,
    #         "notes": "Tricky hide near the bridge."
    #     },
    # ]
