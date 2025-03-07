from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Email
from jinja2 import DictLoader
import os

# إعداد التطبيق وتكوينه
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'flights.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إعداد قاعدة البيانات
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

# تعريف النماذج (Forms) باستخدام Flask-WTF
class FlightSearchForm(FlaskForm):
    from_city = StringField("من", validators=[DataRequired()])
    to_city = StringField("إلى", validators=[DataRequired()])
    date = DateField("التاريخ", format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField("ابحث عن الرحلات")

class BookingForm(FlaskForm):
    name = StringField("الاسم", validators=[DataRequired()])
    email = EmailField("البريد الإلكتروني", validators=[DataRequired(), Email()])
    submit = SubmitField("تأكيد الحجز")

# تعريف القوالب (Templates) داخل قاموس واستخدام DictLoader لتحميلها
TEMPLATES = {
    "base.html": """
<!DOCTYPE html>
<html lang="ar">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}نظام حجز الرحلات{% endblock %}</title>
  <!-- ربط Bootstrap من CDN -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
  <div class="container mt-4">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
          </div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    {% block content %}{% endblock %}
  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """,
    "index.html": """
{% extends "base.html" %}
{% block title %}الصفحة الرئيسية{% endblock %}
{% block content %}
  <h1 class="mb-4">نظام حجز الرحلات</h1>
  <form method="POST" novalidate>
    {{ form.hidden_tag() }}
    <div class="mb-3">
      {{ form.from_city.label(class="form-label") }}
      {{ form.from_city(class="form-control") }}
    </div>
    <div class="mb-3">
      {{ form.to_city.label(class="form-label") }}
      {{ form.to_city(class="form-control") }}
    </div>
    <div class="mb-3">
      {{ form.date.label(class="form-label") }}
      {{ form.date(class="form-control") }}
    </div>
    <div class="mb-3">
      {{ form.submit(class="btn btn-primary") }}
    </div>
  </form>
{% endblock %}
    """,
    "flights.html": """
{% extends "base.html" %}
{% block title %}الرحلات المتوفرة{% endblock %}
{% block content %}
  <h1 class="mb-4">الرحلات المتوفرة</h1>
  {% if flights %}
    <ul class="list-group">
      {% for flight in flights %}
        <li class="list-group-item d-flex justify-content-between align-items-center">
          {{ flight.from_city }} إلى {{ flight.to_city }} في {{ flight.date }} - ${{ flight.price }}
          <a href="{{ url_for('book', flight_id=flight.id) }}" class="btn btn-success">احجز الآن</a>
        </li>
      {% endfor %}
    </ul>
  {% else %}
    <p>لا توجد رحلات متاحة للتاريخ المطلوب.</p>
  {% endif %}
{% endblock %}
    """,
    "booking.html": """
{% extends "base.html" %}
{% block title %}حجز الرحلة{% endblock %}
{% block content %}
  <h1 class="mb-4">حجز الرحلة</h1>
  <div class="mb-3">
    <p>{{ flight.from_city }} إلى {{ flight.to_city }} في {{ flight.date }} - ${{ flight.price }}</p>
  </div>
  <form method="POST" novalidate>
    {{ form.hidden_tag() }}
    <div class="mb-3">
      {{ form.name.label(class="form-label") }}
      {{ form.name(class="form-control") }}
    </div>
    <div class="mb-3">
      {{ form.email.label(class="form-label") }}
      {{ form.email(class="form-control") }}
    </div>
    <div class="mb-3">
      {{ form.submit(class="btn btn-primary") }}
    </div>
  </form>
{% endblock %}
    """,
    "404.html": """
{% extends "base.html" %}
{% block title %}الصفحة غير موجودة{% endblock %}
{% block content %}
  <h1>404 - الصفحة غير موجودة</h1>
  <p>عذرًا، الصفحة التي تبحث عنها غير موجودة.</p>
  <a href="{{ url_for('index') }}" class="btn btn-primary">العودة للصفحة الرئيسية</a>
{% endblock %}
    """,
    "500.html": """
{% extends "base.html" %}
{% block title %}خطأ في الخادم{% endblock %}
{% block content %}
  <h1>500 - خطأ في الخادم</h1>
  <p>حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى لاحقًا.</p>
  <a href="{{ url_for('index') }}" class="btn btn-primary">العودة للصفحة الرئيسية</a>
{% endblock %}
    """
}
app.jinja_loader = DictLoader(TEMPLATES)

# إنشاء الجداول وإضافة بيانات تجريبية في حال عدم وجود بيانات
with app.app_context():
    db.create_all()
    if not Flight.query.first():
        flight1 = Flight(from_city="New York", to_city="Los Angeles", date="2025-03-10", price=300.00)
        flight2 = Flight(from_city="Chicago", to_city="Miami", date="2025-03-15", price=250.00)
        db.session.add(flight1)
        db.session.add(flight2)
        db.session.commit()

# تعريف مسارات التطبيق
@app.route('/', methods=['GET', 'POST'])
def index():
    form = FlightSearchForm()
    if form.validate_on_submit():
        return redirect(url_for('flights', from_city=form.from_city.data, to_city=form.to_city.data, date=form.date.data.strftime("%Y-%m-%d")))
    return render_template("index.html", form=form)

@app.route('/flights')
def flights():
    from_city = request.args.get('from_city')
    to_city = request.args.get('to_city')
    date = request.args.get('date')
    flights = Flight.query.filter_by(from_city=from_city, to_city=to_city, date=date).all()
    return render_template("flights.html", flights=flights)

@app.route('/book/<int:flight_id>', methods=['GET', 'POST'])
def book(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    form = BookingForm()
    if form.validate_on_submit():
        booking = Booking(flight_id=flight.id, name=form.name.data, email=form.email.data)
        db.session.add(booking)
        db.session.commit()
        flash("تم تأكيد الحجز بنجاح!", "success")
        return redirect(url_for('index'))
    return render_template("booking.html", flight=flight, form=form)

# معالجة الأخطاء
@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("500.html"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
