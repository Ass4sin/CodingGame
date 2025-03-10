from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, logout_user, login_user, current_user, login_required, UserMixin
from flask_bcrypt import Bcrypt

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

with app.app_context():
    db.create_all()
    login_manager = LoginManager(app)
    app.secret_key= 'key'

@login_manager.user_loader
def load_users(uid):
    return User.query.get(uid)

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
@app.route('/login', methods=['GET', 'POST'])
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
        else:
            return 'Failed'
def login(uid):
    user = User.query.get(uid)
    login_user(user)
    return 'Success'

@app.route('/logout')
def logout():
   logout_user()
   return 'Success'

@app.route('/test')
def test():
    if current_user.is_authenticated:
        return str(current_user.name)

if __name__ == '__main__':
    app.run(debug=True)
