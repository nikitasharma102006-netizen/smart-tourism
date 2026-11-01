from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "smart_tourism_secret"

# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/home")
def home_page():
    return render_template("index.html")

def get_db():
    conn = sqlite3.connect("tourism.db")
    conn.row_factory = sqlite3.Row
    return conn

def update_booking_table():
    conn = get_db()

    columns = [
        row["name"]
        for row in conn.execute("PRAGMA table_info(bookings)")
    ]

    if "hotel" not in columns:
        conn.execute(
            "ALTER TABLE bookings ADD COLUMN hotel TEXT DEFAULT ''"
        )

    if "people" not in columns:
        conn.execute(
            "ALTER TABLE bookings ADD COLUMN people INTEGER DEFAULT 1"
        )

    conn.commit()
    conn.close()
# Create database and users table
def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/places")
def places():
    return render_template("places.html")

@app.route("/place/goa")
def goa():
    return redirect("/place/Goa")

@app.route("/place/<place_name>")
def place_details(place_name):
    place_name = place_name.capitalize()

    places_data = {

        "Goa": {
            "title": "Goa",
            "emoji": "🏖️",
            "about": "Goa is famous for beautiful beaches, nightlife, water sports and Portuguese heritage.",
            "places": ["Baga Beach", "Calangute Beach", "Fort Aguada", "Dudhsagar Waterfalls"],
            "best_time": "November to February",
            "budget": "₹5,000 - ₹15,000",
            "lat": 15.4909,
            "lng": 73.8278

        },

        "Manali": {
            "title": "Manali",
            "emoji": "🏔️",
            "about": "Manali is a beautiful mountain destination famous for snow, nature, adventure and scenic views.",
            "places": ["Solang Valley", "Rohtang Pass", "Hadimba Temple", "Mall Road"],
            "best_time": "October to June",
            "budget": "₹6,000 - ₹18,000",
            "lat": 32.2432,
            "lng": 77.1892
            
            
        },

        "Kerala": {
            "title": "Kerala",
            "emoji": "🌴",
            "about": "Kerala is famous for backwaters, greenery, beaches, hill stations and beautiful landscapes.",
            "places": ["Alleppey", "Munnar", "Kovalam Beach", "Thekkady"],
            "best_time": "September to March",
            "budget": "₹7,000 - ₹20,000",
            "lat": 10.8505,
            "lng": 76.2711
        },

        "Mumbai": {
            "title": "Mumbai",
            "emoji": "🏙️",
            "about": "Mumbai is a vibrant city famous for its landmarks, beaches, food and entertainment.",
            "places": ["Gateway of India", "Marine Drive", "Juhu Beach", "Elephanta Caves"],
            "best_time": "October to February",
            "budget": "₹4,000 - ₹12,000",
            "lat": 19.0760,
            "lng": 72.8777
        },

        "Jaipur": {
            "title": "Jaipur",
            "emoji": "🏰",
            "about": "Jaipur is the Pink City, famous for forts, palaces, culture, markets and traditional food.",
            "places": ["Amber Fort", "Hawa Mahal", "City Palace", "Jal Mahal"],
            "best_time": "October to March",
            "budget": "₹5,000 - ₹15,000",
            "lat": 26.9124,
            "lng": 75.7873
        },

        "Delhi": {
            "title": "Delhi",
            "emoji": "🏛️",
            "about": "Delhi is famous for historical monuments, markets, culture and famous landmarks.",
            "places": ["India Gate", "Red Fort", "Qutub Minar", "Lotus Temple"],
            "best_time": "October to March",
            "budget": "₹4,000 - ₹12,000",
            "lat": 28.6139,
            "lng": 77.2090
        }
    }

    place = places_data.get(place_name)

    if not place:
        return "Place not found", 404

    return render_template("PlaceDetails.html", place=place)


@app.route("/hotels")
def hotels():
    return render_template("hotels.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        try:
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:
            conn.close()
            return "Email already registered!"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()

        conn.close()

        if user:
            session["user"] = user["name"]
            return redirect("/dashboard")

        return "Invalid email or password!"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        destination = request.form["destination"]
        hotel = request.form["hotel"]
        checkin = request.form["checkin"]
        checkout = request.form["checkout"]
        people = request.form["people"]

        conn = get_db()

        conn.execute("""
            INSERT INTO bookings
            (name, email, destination, hotel, checkin, checkout, people)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            email,
            destination,
            hotel,
            checkin,
            checkout,
            people
        ))

        conn.commit()
        conn.close()

        return render_template("BookingSuccess.html")

    return render_template("Booking.html")

@app.route("/mybooking")
def mybooking():
    conn = sqlite3.connect("tourism.db")
    conn.row_factory = sqlite3.Row

    bookings = conn.execute("""
        SELECT * FROM bookings
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template("MyBookings.html", bookings=bookings)

if __name__ == "__main__":
    init_db()
    update_booking_table()
    app.run(debug=True)