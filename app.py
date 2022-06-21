import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, session, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TheHardkiss.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

uploads = 'static/uploads'
extensions = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = uploads
app.secret_key = 'He`s saving my life. Nobody knows he could. He makes me smile. He makes me feel so good.'

def checkFile(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    year = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<Album %r>' % self.id

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<users {self.id}>"

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/album')
def album():
    return render_template('album.html', albums = db.session.query(Album).order_by(Album.year.desc()).all())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            hash = generate_password_hash(request.form['password'])

            if request.form['password'] != request.form['password_confirm'] and len(request.form['password']) < 3:
                return redirect('/register')

            user = Users(email=request.form['login'], password=hash)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
        except:
            db.session.rollback()
            return "Помилка вставки в базі даних"

    return render_template('register.html')

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        if len(request.form['email']) > 0 and len(request.form['password']) >= 3:
            email = request.form['email']
            psword = request.form['password']

            user = Users.query.filter_by(email=email).first()

            if user is not None:
                if check_password_hash(pwhash=user.password, password=psword):
                    session['user'] = email
                    return redirect('/home')
            else:
                redirect('/login')

    return render_template('login.html')

@app.route('/exit')
def exit():
    session.pop('user', None)
    return redirect('/home')

@app.route('/createAlbum', methods=['GET', 'POST'])
def createAlbum():
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                flash('Помилка шляху')
                return redirect(request.url)
            file = request.files['file']

            if file.filename == '':
                flash('Немає файлу')
                return redirect(request.url)

            if file and checkFile(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                album_title = request.form['album_title']
                album_year = request.form['album_year']

                album = Album(year = album_year, title = album_title, image = filename)
                db.session.add(album)
                db.session.commit()

                return redirect(url_for('album'))
        except:
            db.session.rollback()

    return render_template('create_album.html')

@app.route('/updateAlbum/<int:id>', methods=['GET', 'POST'])
def updateAlbum(id):
    album = Album.query.get(id)

    if request.method == 'POST':
        try:
            file = ''
            if 'file' in request.files:
                file = request.files['file']

            album_title = request.form['album_title']
            album_year = request.form['album_year']

            if file and checkFile(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                db.session.query(Album).filter(Album.id == id).update(
                    {Album.title: album_title, Album.year: album_year, Album.image: filename})

            else:
                db.session.query(Album).filter(Album.id == id).update(
                    {Album.title: album_title, Album.year: album_year})

            db.session.commit()
            return redirect(url_for('album'))
        except:
            db.session.rollback()

    return render_template('update_album.html', album = album)

@app.route('/deleteAlbum/<int:id>')
def deleteAlbum(id):
    db.session.query(Album).filter(Album.id == id).delete()
    db.session.commit()

    return redirect('/album')

if __name__ == '__main__':
    app.run(debug=False)
