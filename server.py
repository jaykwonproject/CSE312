import flask
from flask_socketio import SocketIO, emit, send
from pymongo import MongoClient

app = flask.Flask(__name__)
socket_io = SocketIO(app)


@app.route('/')
def home():
    if not flask.session.get('logged_in'):
        return flask.render_template('index.html')
    else:
        if flask.session.get('user') == None:
            return flask.render_template('index.html')
        else:
            name = flask.request.cookies.get('username')
            return flask.render_template('index.html', data=name)


@app.route('/chat')
def chatting():
    if not flask.session.get('logged_in'):
        return flask.render_template('index.html')
    else:
        if flask.session.get('user') is None:
            return flask.render_template('index.html')
        else:
            client = MongoClient('mongo', 27017)
            db = client.chatDatabase
            collection = db.chatCollection
            msgs = ''
            check = collection.find({'msg': {'$exists': True}})
            app.logger.info("HIIIII")
            app.logger.info(check)
            if check:
                for x in collection.find({'msg': {'$exists': True}}):
                    app.logger.info("HELLOOOOO")
                    app.logger.info(x)
                    username = x['uname']
                    message = x['msg']
                    msgs += f'<li>{username} : {message}</li>'
                app.logger.info(msgs)
                return flask.render_template('chat.html', message=msgs)
            else:
                return flask.render_template('chat.html')


@socket_io.on("message")
def request(message):
    if not flask.session.get('logged_in'):
        return flask.render_template('index.html')
    else:
        if flask.session.get('user') == None:
            return flask.render_template('index.html')
        else:
            client = MongoClient('mongo', 27017)
            db = client.chatDatabase
            collection = db.chatCollection
            to_client = dict()
            currentUser = flask.request.cookies.get('username')
            if message == 'new_connect':
                to_client['username'] = currentUser
                to_client['message'] = "welcome " + currentUser
            else:
                to_client['username'] = currentUser
                to_client['message'] = currentUser + ' : ' + message
                collection.insert_one({"uname": currentUser, "msg": message})
            send(to_client, broadcast=True)


@app.route('/login')
def login():
    return flask.render_template('login.html')


@app.route('/logout')
def logout():
    flask.session['logged_in'] = False
    flask.session['user'] = ''
    resp = flask.redirect(flask.url_for('home'))
    resp.set_cookie('username', value='')
    return flask.redirect(flask.url_for('home'))


@app.route('/checkCredentials', methods=['GET', 'POST'])
def checkCredentials():
    client = MongoClient('mongo', 27017)
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
        resp = flask.redirect(flask.url_for('home'))
        resp.set_cookie('username', value=username)
        return resp


@app.route('/register', methods=['GET', 'POST'])
def register():
    return flask.render_template('register.html')


@app.route('/checkAvailability', methods=['GET', 'POST'])
def checkAvailability():
    client = MongoClient('mongo', 27017)
    db = client.chatDatabase
    collection = db.chatCollection
    username = flask.request.form['username']
    password = flask.request.form['password']
    re_password = flask.request.form['re-password']
    check = collection.count_documents({"username": username})
    if check != 0:
        app.logger.info("Duplicated username! Please use another username")
        return flask.redirect(flask.url_for('register'))

    elif password != re_password:
        app.logger.info("Please enter the password agian!")
        return flask.redirect(flask.url_for('register'))

    else:
        collection.insert_one({"username": username, "password": password})
        app.logger.info("Now you are our member!")
        client.close()
        return flask.redirect(flask.url_for('login'))


@app.route('/<error>')
def error(error):
    return f"404 not found. Page '{error}' does not exist."


if __name__ == "__main__":
    app.secret_key = "123"
    app.run(host='0.0.0.0', port='8000', debug=True)  # change to false for production
