import flask
import bcrypt
from pymongo import MongoClient

app = flask.Flask(__name__)

@app.route('/')
def home():
    if not flask.session.get('logged_in'):
        return flask.render_template('index.html')
    else:
        if flask.session.get('user') == None:
            return flask.render_template('index.html')
        else:
            return flask.render_template('index.html', data=flask.session.get('user'))


@app.route('/login')
def login():
    return flask.render_template('login.html')

@app.route('/logout')
def logout():
    flask.session['logged_in'] = False
    flask.session['user'] = ''
    return flask.redirect(flask.url_for('home'))


@app.route('/checkCredentials' , methods=['GET', 'POST'])
def checkCredentials():
    client = MongoClient('mongo',27017)
    # client = MongoClient('mongodb://localhost:27017')
    db = client.chatDatabase
    collection = db.chatCollection
    username = flask.request.form['username']
    password = flask.request.form['password']
    check = collection.find_one({"username": username})
    client.close()
    if check == None:
        app.logger.info("doesn't exist!")
        return flask.redirect(flask.url_for('login'))
    else:
        if bcrypt.checkpw(password.encode(), check["password"]) == True:
            flask.session['logged_in'] = True
            flask.session['user'] = username
            return flask.redirect(flask.url_for('home'))
        else:
            flask.flash("Password does not match! Please try again.")
            return flask.redirect(flask.url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    return flask.render_template('register.html')

@app.route('/checkAvailability', methods=['GET', 'POST'])
def checkAvailability():
    client = MongoClient('mongo',27017)
    # client = MongoClient('mongodb://localhost:27017')
    db = client.chatDatabase
    collection = db.chatCollection
    username = flask.request.form['username']
    password = flask.request.form['password']
    re_password = flask.request.form['re-password']
    check = collection.count_documents({"username": username})
    if check != 0:
        flask.flash("Duplicated username! Please use another username")
        return flask.redirect(flask.url_for('register'))
    
    elif password != re_password:
        flask.flash("Please enter the password agian!")
        return flask.redirect(flask.url_for('register'))

    else:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        collection.insert_one({"username": username, "password": hashed})
        flask.flash("Now you are our member!")
        client.close()
        return flask.redirect(flask.url_for('login'))


@app.route('/<error>')
def error(error):
    return f"404 not found. Page '{error}' does not exist."

if __name__ == "__main__":
    app.secret_key ="123"
    app.run(host='0.0.0.0', port='8000', debug=False)#change to false for production
