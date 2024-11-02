from crypt import methods
from flask import Flask, request, session, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
import os

from sqlalchemy.testing.suite.test_reflection import users

SESSION_USER_ID = 'user_id'

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, 'school.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dI4DXyeF1MvLyRyFayQuWm198f_fed0rQV4S_nAOgmo'
db = SQLAlchemy(app)


# === MODELS =====================================================================================
class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(25), nullable=False)
    role = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<User: {self.username}>'

    def check_password(self, password):
        return check_password_hash(self.password, password)



with app.app_context():
    db.create_all()

# === ROUTES ===================================================================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    # код ...
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/courses')
def courses():
    return render_template('courses.html')


@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

# --- ADMIN ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    massage = ''

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if not user:
            massage = 'неправильний Email!'
        else:
            if user.check_password(password):
                session[SESSION_USER_ID] = user.id
                return redirect('/')

            massage = 'неправильний пароль!'

    return render_template('login.html', massage=massage)

@app.route('/login', methods=['GET', 'POST'])
def logout():
    session.pop(SESSION_USER_ID, None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
