import stripe
from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, logout_user, login_user, current_user, login_required, UserMixin
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/coding_game'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    role = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<User {self.name}, Role: {self.role}>'

    def get_id(self):
        return self.id

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)


with app.app_context():
    db.create_all()
    login_manager = LoginManager(app)
    app.secret_key= 'key'

@login_manager.user_loader
def load_users(uid):
    return User.query.get(uid)

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/')

# Context processor to add current year to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/ateliers')
def ateliers():
    return render_template('ateliers.html')

@app.route('/coaching')
def coaching_details():
    return render_template('coaching_details.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')



@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup-check', methods=["POST"])
def signup_check():
    username = request.form.get('username')
    print(username)
    email = request.form.get('email')
    password = request.form.get('password')
    password_confirmation = request.form.get('password-confirmation')
    if password == password_confirmation:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        with app.app_context():
            new_user = User(name=username, password=hashed_password, email=email, role='user')
            db.session.add(new_user)
            try:
                db.session.commit()
                return redirect('/login')
            except Exception as e:
                db.session.rollback()
                print(f"Error: {e}")
                return "An error occurred", 500
    else:
        return "Passwords dont match", 400
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password)
        user =  User.query.filter(User.name == username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect('/')



@app.route('/logout')
def logout():
   logout_user()
   return redirect(url_for('home'))


@app.route('/blogs')
def blog_list():
    blogs = db.session.execute(db.select(Blog)).scalars()
    print(blogs)
    return render_template("blog_list.html", blogs=blogs)

@app.route('/blogs/<blog_id>', methods=['POST', 'GET'])
def blog_details(blog_id):
    if request.method == 'GET':
        blogs = db.session.execute(db.select(Blog).filter(Blog.id == blog_id)).scalars()
        comments = db.session.execute(db.select(Comment)).scalars()
        return render_template("blog.html", blogs=blogs, comments=comments)
    elif request.method == 'POST':
        content = request.form.get('content')
        with app.app_context():
            new_comment = Comment(author=current_user.name, content=content, blog_id=blog_id)
            db.session.add(new_comment)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error: {e}")
                return "An error occurred", 500
            return  redirect(f'/blogs/{blog_id}')

@app.route('/blogs/form', methods=['POST', 'GET'])
def blog_form():
    if request.method == 'GET':
        return render_template("blog_form.html")
    elif request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        with app.app_context():
            new_blog = Blog(title=title, content=content)
            db.session.add(new_blog)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error: {e}")
                return "An error occurred", 500
            return redirect('/blogs')






@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': 'Coaching de leadership féminin',
                    },
                    'unit_amount': 1,  # Amount in cents (200 EUR)
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://yourwebsite.com/success',
            cancel_url='http://yourwebsite.com/cancel',
        )
        return jsonify({'id': session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/account')
@login_required
def account():
    # Get user's appointments if they exist
    appointments = Appointment.query.filter_by(name=current_user.name).all()
    return render_template('account.html', appointments=appointments)


@app.route('/calendar')
def test():
    return render_template("calendar.html")




@app.route('/calendar-date', methods=["POST"])
def test_date():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        time = request.form['time']
        date_time_str = f"{date} {time}"
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
        new_appointment = Appointment(name=name, date_time=date_time_obj)
        db.session.add(new_appointment)
        db.session.commit()
        return redirect('/')
    appointments = Appointment.query.all()
    return render_template('index.html', appointments=appointments)

if __name__ == '__main__':
    app.run(debug=True)