from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

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
def coaching():
    return render_template('coaching.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)

