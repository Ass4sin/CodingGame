import stripe
from flask import Flask, render_template, request, redirect, jsonify, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, logout_user, login_user, current_user, login_required, UserMixin
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)
stripe.api_key = os.getenv('STRIPE_API_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/coding_game'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modèle pour représenter un utilisateur dans la base de données
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    role = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<User {self.name}, Role: {self.role}>'

    def get_id(self):
        return self.id

# Modèle pour représenter un article de blog
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)

# Modèle pour représenter un commentaire associé à un blog
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)

# Modèle pour représenter un rendez-vous
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)

with app.app_context():
    db.create_all()
    login_manager = LoginManager(app)
    app.secret_key = 'key'

# Charge un utilisateur à partir de son identifiant pour Flask-Login
@login_manager.user_loader
def load_users(uid):
    return User.query.get(uid)

# Redirige les utilisateurs non authentifiés vers la page d'accueil
@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/')

# Injecte la date et l'heure actuelle dans tous les templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# =====================================
# Routes principales de l'application
# =====================================

# Page d'accueil
@app.route('/')
def home():
    return render_template('index.html')

# Page "À propos"
@app.route('/about')
def about():
    return render_template('about.html')

# Page des services
@app.route('/services')
def services():
    return render_template('services.html')

# Page des ateliers
@app.route('/ateliers')
def ateliers():
    return render_template('ateliers.html')

# Page dédiée au coaching
@app.route('/coaching')
def coaching_details():
    return render_template('coaching_details.html')

# Page de contact
@app.route('/contact')
def contact():
    return render_template('contact.html')

# =====================================
# Gestion des utilisateurs
# =====================================

# Affiche le formulaire d'inscription
@app.route('/signup')
def signup():
    return render_template('signup.html')

# Traite le formulaire d'inscription
@app.route('/signup-check', methods=["POST"])
def signup_check():
    # Récupère les informations du formulaire
    username = request.form.get('username')
    print(username)
    email = request.form.get('email')
    password = request.form.get('password')
    password_confirmation = request.form.get('password-confirmation')

    # Vérifie que les mots de passe correspondent
    if password == password_confirmation:
        # Hash du mot de passe pour le stockage sécurisé
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

# Gère la connexion des utilisateurs
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter(User.name == username).first()
        # Vérifie le mot de passe à l'aide de bcrypt
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect('/')
        else:
            return "Invalid credentials", 401

# Déconnexion de l'utilisateur courant
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

# =====================================
# Gestion des Blogs et Commentaires
# =====================================

# Affiche la liste de tous les blogs
@app.route('/blogs')
def blog_list():
    # Exécute une requête pour récupérer tous les blogs
    blogs = db.session.execute(db.select(Blog)).scalars()
    print(blogs)
    return render_template("blog_list.html", blogs=blogs)

# Affiche les détails d'un blog et ses commentaires,
# et permet d'ajouter un commentaire via POST
@app.route('/blogs/<int:blog_id>', methods=['POST', 'GET'])
def blog_details(blog_id):
    if request.method == 'GET':
        # Récupère le blog spécifique grâce à son ID
        blog = Blog.query.get(blog_id)

        # Vérifie si le blog existe
        if not blog:
            return "Blog non trouvé", 404

        # Récupère les commentaires associés à ce blog
        comments = db.session.execute(db.select(Comment).filter(Comment.blog_id == blog_id)).scalars().all()

        return render_template("blog.html", blog=blog, comments=comments)


    elif request.method == 'POST':
        # Récupère le contenu du commentaire depuis le formulaire
        content = request.form.get('content')

        if not content:
            return "Le commentaire ne peut pas être vide", 400

        with app.app_context():
            # Crée un nouveau commentaire associé au blog et à l'utilisateur courant
            new_comment = Comment(author=current_user.name, content=content, blog_id=blog_id)
            db.session.add(new_comment)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error: {e}")
                return "Une erreur est survenue", 500

        return redirect(f'/blogs/{blog_id}')


# Crée une session de paiement avec Stripe pour un service de coaching
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
                    'unit_amount': 20000,  # Montant en centimes (200 EUR)
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:5000/success',
            cancel_url='http://localhost:5000/cancel',
        )
        # Retourne l'ID de session pour permettre le redirection côté client
        return jsonify({'id': session.id})
    except Exception as e:
        print(f"Stripe error: {e}")
        return jsonify(error=str(e)), 400

# Affiche le formulaire de création d'un blog pour les administrateurs
@app.route('/blogs/form', methods=['POST', 'GET'])
def blog_form():
    if current_user.is_authenticated == False or current_user.role != 'admin':
        return redirect('/')
    if request.method == 'GET':
        return render_template("blog_form.html")
    elif request.method == 'POST':
        # Récupère les données du formulaire de création de blog
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

# Permet à un administrateur de modifier un blog existant
@app.route('/blogs/edit/<int:blog_id>', methods=['GET', 'POST'])
def update_blog(blog_id):
    # Vérification que l'utilisateur est connecté et qu'il a le rôle 'admin'
    if not current_user.is_authenticated or current_user.role != 'admin':
        return redirect('/')
    # Récupère le blog par son ID
    blog = Blog.query.get(blog_id)
    if not blog:
        return "Blog non trouvé", 404

    if request.method == 'GET':
        # Affiche le formulaire de modification avec les données existantes
        return render_template("blog_edit.html", blog=blog)
    elif request.method == 'POST':
        # Récupère les nouvelles valeurs du formulaire
        title = request.form.get('title')
        content = request.form.get('content')
        if title:
            blog.title = title
        if content:
            blog.content = content
        try:
            # Valide les modifications dans la base de données
            db.session.commit()
            return redirect(url_for('blog_details', blog_id=blog_id))
        except Exception as e:
            db.session.rollback()
            print(f"Erreur : {e}")
            return "Une erreur est survenue", 500
        return redirect('/')


@app.route('/blogs/delete/<int:blog_id>', methods=['POST'])
def delete_blog(blog_id):
    # Vérifie que l'utilisateur est authentifié et a le rôle 'admin'
    if not current_user.is_authenticated or current_user.role != 'admin':
        return redirect('/')

    # Récupère le blog correspondant à l'ID
    blog = Blog.query.get(blog_id)
    if not blog:
        return "Blog non trouvé", 404

    # Supprime le blog de la base de données
    db.session.delete(blog)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de la suppression: {e}")
        return "Une erreur est survenue", 500

    # Redirige vers la liste des blogs après suppression
    return redirect(f'/blogs/{blog_id}')

# =====================================
# Gestion des Rendez-vous et Autres
# =====================================

# Affiche la page de compte utilisateur avec ses rendez-vous
@app.route('/account')
@login_required
def account():
    appointments = Appointment.query.filter_by(name=current_user.name).all()
    return render_template('account.html', appointments=appointments)

# Affiche une page avec un calendrier (exemple de route pour le calendrier)
@app.route('/calendar')
def test():
    return render_template("calendar.html")

# Traite les données du calendrier pour créer un nouveau rendez-vous
@app.route('/calendar-date', methods=["POST"])
def test_date():
    if request.method == 'POST':
        # Récupère les informations de rendez-vous du formulaire
        name = request.form['name']
        date = request.form['date']
        time = request.form['time']
        # Combine la date et l'heure en un seul objet datetime
        date_time_str = f"{date} {time}"
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
        new_appointment = Appointment(name=name, date_time=date_time_obj)
        db.session.add(new_appointment)
        db.session.commit()
        return redirect('/')
    appointments = Appointment.query.all()
    return render_template('index.html', appointments=appointments)

# Permet le téléchargement d'un fichier PDF depuis le dossier 'static/pdf'
@app.route('/download-packages')
def download_packages():
    return send_from_directory(
        directory=os.path.join(app.root_path, 'static', 'pdf'),
        path='Packages.pdf',
        as_attachment=True
    )

# Point d'entrée de l'application, lance le serveur en mode debug
if __name__ == '__main__':
    app.run(debug=True)
