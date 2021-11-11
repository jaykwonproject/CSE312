import flask
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

@app.route('/checkCredentials' , methods=['GET', 'POST'])
def checkCredentials():
    #client = MongoClient('mongo',27017)
    client = MongoClient('mongodb://localhost:27017')
    db = client.chatDatabase
    collection = db.chatCollection
    username = flask.request.form['username']
    password = flask.request.form['password']
    check = collection.find_one({"username": username, "password": password})
    client.close()
    if check == None:
        app.logger.info("doesn't exist!")
        return flask.redirect(flask.url_for('login'))
    else:
        flask.session['logged_in'] = True
        flask.session['user'] = username
        return flask.redirect(flask.url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    #client = MongoClient('mongo',27017)
    client = MongoClient('mongodb://localhost:27017')
    db = client.chatDatabase
    collection = db.chatCollection
    username = flask.request.form['username']
    password = flask.request.form['password']
    collection.insert_one({"username": username, "password": password})
    client.close()
    return flask.redirect(flask.url_for('login'))


@app.route('/<error>')
def error(error):
    return f"404 not found. Page '{error}' does not exist."

if __name__ == "__main__":
    app.secret_key ="123"
    app.run(host='0.0.0.0', port='8000', debug=True)#change to false for production
