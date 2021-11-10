import flask
from pymongo import MongoClient

app = flask.Flask(__name__)

@app.route('/')

def home():
    client = MongoClient('mongo',27017)
    db = client.chatDatabase
    collection = db.chatCollection
    results = collection.find()
    return flask.render_template('index.html', data=results)

@app.route('/register', methods=['GET', 'POST'])
def register():
    client = MongoClient('mongo',27017)
    db = client.chatDatabase
    collection = db.chatCollection
    username = flask.request.form['username']
    password = flask.request.form['password']
    collection.insert_one({"username": username, "password": password})
    client.close()
    return flask.redirect(flask.url_for('home'),code=301)

@app.route('/<error>')
def error(error):
    return f"404 not found. Page '{error}' does not exist."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8000')#change to false for production
