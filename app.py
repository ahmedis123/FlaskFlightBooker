from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flights.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# تعريف نماذج قاعدة البيانات
class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_city = db.Column(db.String(100), nullable=False)
    to_city = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Flight {self.from_city} to {self.to_city} on {self.date}>"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Booking {self.name} for flight {self.flight_id}>"

# إنشاء الجداول في قاعدة البيانات
with app.app_context():
    db.create_all()

# إضافة بيانات تجريبية (يمكن حذفها لاحقًا)
def add_sample_data():
    if not Flight.query.first():
        flight1 = Flight(from_city="New York", to_city="Los Angeles", date="2025-03-10", price=300.00)
        flight2 = Flight(from_city="Chicago", to_city="Miami", date="2025-03-15", price=250.00)
        db.session.add(flight1)
        db.session.add(flight2)
        db.session.commit()

add_sample_data()

# الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# البحث عن الرحلات
@app.route('/flights', methods=['GET', 'POST'])
def flights():
    if request.method == 'POST':
        from_city = request.form['from']
        to_city = request.form['to']
        date = request.form['date']

        # البحث في قاعدة البيانات
        flights = Flight.query.filter(
            Flight.from_city == from_city,
            Flight.to_city == to_city,
            Flight.date == date
        ).all()

        return render_template('flights.html', flights=flights)
    return redirect(url_for('index'))

# حجز الرحلة
@app.route('/book/<int:flight_id>', methods=['GET', 'POST'])
def book(flight_id):
    flight = Flight.query.get_or_404(flight_id)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        # إنشاء حجز جديد
        booking = Booking(flight_id=flight.id, name=name, email=email)
        db.session.add(booking)
        db.session.commit()

        return f"Booking confirmed for {name} on flight {flight.from_city} to {flight.to_city}!"

    return render_template('booking.html', flight=flight)

# تعريف القوالب (HTML) داخل الكود
@app.route('/templates')
def templates():
    return {
        "index.html": """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Flight Booking</title>
        </head>
        <body>
            <h1>Flight Booking System</h1>
            <form action="/flights" method="POST">
                <label for="from">From:</label>
                <input type="text" id="from" name="from" required>
                <br>
                <label for="to">To:</label>
                <input type="text" id="to" name="to" required>
                <br>
                <label for="date">Date:</label>
                <input type="date" id="date" name="date" required>
                <br>
                <button type="submit">Search Flights</button>
            </form>
        </body>
        </html>
        """,
        "flights.html": """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Available Flights</title>
        </head>
        <body>
            <h1>Available Flights</h1>
            <ul>
                {% for flight in flights %}
                <li>
                    {{ flight.from_city }} to {{ flight.to_city }} on {{ flight.date }} - ${{ flight.price }}
                    <a href="{{ url_for('book', flight_id=flight.id) }}">Book Now</a>
                </li>
                {% endfor %}
            </ul>
        </body>
        </html>
        """,
        "booking.html": """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Book Flight</title>
        </head>
        <body>
            <h1>Book Flight</h1>
            <p>
                {{ flight.from_city }} to {{ flight.to_city }} on {{ flight.date }} - ${{ flight.price }}
            </p>
            <form method="POST">
                <label for="name">Name:</label>
                <input type="text" id="name" name="name" required>
                <br>
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
                <br>
                <button type="submit">Confirm Booking</button>
            </form>
        </body>
        </html>
        """
    }

if __name__ == '__main__':
    app.run(debug=True)
