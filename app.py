from flask import Flask, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from forms.user_forms import RegistrationForm, LoginForm
from models.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from flask_app import db, login_manager
from flask_login import LoginManager
from flask_login import login_user, logout_user, login_required
from flask_login import LoginManager
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user

from models.models import db, User


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
csrf = CSRFProtect(app)



db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app) 


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        role = form.role.data
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists.')
            return redirect(url_for('auth.register'))
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role = form.role.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session["user_id"] = user.id
            session["username"] = user.username
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", form=form)

@app.route("/dashboard")
@login_required
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    print(f"current userrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr :{current_user}")
    return render_template('dashboard.html', user=current_user)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)

