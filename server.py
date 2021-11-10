from flask import Flask, render_template, request, redirect, Response, abort, url_for
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import re, hashlib, uuid

app = Flask(__name__)

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'

# class User(username, password):
#     u = username
#     p = password

db = []
@app.route('/')
# @app.route('/home')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    print(request.form['username'])
    print(request.form['password'])

    return redirect(url_for('home'))

    # if form.validate_on_submit():
    #     # hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') hash and salt in another way
    #     user = User(username=form.username.data, email=form.email.data, password=hashed_password)
    #     db.session.add(user)
    #     db.session.commit()
    #     flash('Your account has been created! You are now able to log in', 'success')
    #     return redirect(url_for('login'))
    # return render_template('register.html', title='Register', form=form)



@app.route('/<error>')
def error(error):
    return f"404 not found. Page '{error}' does not exist."

if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug = True)#change to false for production
