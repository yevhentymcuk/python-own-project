from flask import Flask, request, session, redirect, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
import os
from datetime import datetime

SESSION_USER_ID = 'user_id'

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, 'school.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'kiuVkyaxU14Gb1b5REoq2D0udY0b7rxvtnd_0ByyE74'
db = SQLAlchemy(app)


# === MODELS ==================================================================
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


class News(db.Model):
    __tablename__ = 'News'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text(), nullable=False)
    created_on = db.Column(db.Date(), default=datetime.utcnow())
    deleted = db.Column(db.Boolean, default=False)


# створюємо базу даних
# with app.app_context():
#     db.create_all()


# === ROUTES ==================================================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/news')
def news():
    page = request.args.get('page', 1, type=int)
    list_news = News.query.paginate(page=page, per_page=6)

    for item in list_news:
        if len(item.text) > 200:
            item.text = item.text[:200] + ' ...'

    return render_template('news.html', list_news=list_news,
                           user_id=session.get(SESSION_USER_ID))


@app.route('/news/<int:news_id>')
def news_detail(news_id):
    news_item = News.query.filter_by(id=news_id).first()

    if news_item:
        news_item.text = news_item.text.replace('\n', '<br>')
        return render_template('news_detail.html', news_item=news_item)

    abort(404)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# --- ADMIN ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if not user:
            message = 'Неправильний Email!'
        else:
            if user.check_password(password):
                session[SESSION_USER_ID] = user.id
                return redirect('/')

            message = 'Неправильний пароль'

    return render_template('login.html', message=message)

@app.route('/add_news')
def ad_news():
    if SESSION_USER_ID not in session:
        redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        id = request.form['id']
        image = request.form['image']
        text = request.form['text']

        if id:
            row = News.query.filter_by(id=id).first()
            row.name = name
            row.text = text
            row.image= image
        else:
            row = News(nam=name, text=text, image=image)

        db.session.add(row)
        db.session.commit()

        redirect('/')

    return render_template('add_edit_news.html',
                           message='Додати новину',
                           id=0, name='', text='', image='')


@app.route('/edit_news')
def edit_news():
    pass


@app.route('/logout')
def logout():
    session.pop(SESSION_USER_ID, None)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
