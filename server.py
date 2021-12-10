import flask
import bcrypt
from flask_socketio import SocketIO, emit, send
from pymongo import MongoClient

app = flask.Flask(__name__)
socket_io = SocketIO(app)

postingArr = []
client = MongoClient('mongo',27017)
db = client.chatDatabase
collection = db.postingCollection
for x in collection.find({}):
    tmp = {
            "uploader" : x["Uploder"], 
            "title" : x["title"],
            "content" : x["content"]}
    postingArr.append(tmp)
client.close()

clients = 0
likes = 0
online_users = []

@app.route('/')
def home():
    if not flask.session.get('logged_in'):
        return flask.render_template('index.html')
    else:
        if flask.session.get('user') == None:
            return flask.render_template('index.html')
        else:
            global online_users
            name = flask.request.cookies.get('username')
            if not online_users.__contains__(name):
                online_users.append(name)
            if len(postingArr) != 0 :
              flask.session['posting'] = postingArr   
            return flask.render_template('index.html', data=name, onlineUsers=online_users, posting = flask.session.get('posting'))

@app.route('/chat')
def chatting():
    if not flask.session.get('logged_in'):
        return flask.render_template('index.html')
    else:
        if flask.session.get('user') is None:
            return flask.render_template('index.html')
        else:
            name = flask.request.cookies.get('username')
            client = MongoClient('mongo', 27017)
            db = client.chatDatabase
            collection = db.chatCollection
            msgs = ''
            check = collection.find({'msg': {'$exists': True}})
            if check:
                for x in collection.find({'msg': {'$exists': True}}):
                    username = x['uname']
                    message = x['msg']
                    msgs += f'<li>{username} : {message}</li>'
                app.logger.info(msgs)
                global online_users

                return flask.render_template('chat.html', data=name, message=msgs, onlineUsers=online_users, likes=likes)
            else:
                return flask.render_template('chat.html',data=name, likes=likes)


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
            elif message == 'like':
                global likes
                likes += 1
                to_client['like'] = likes
            else:
                to_client['username'] = currentUser
                to_client['message'] = currentUser + ' : ' + message
                collection.insert_one({"uname": currentUser, "msg": message})
            send(to_client, broadcast=True)

            if len(postingArr) != 0 :
              flask.session['posting'] = postingArr   
            return flask.render_template('index.html', data=flask.session.get('user'), posting = flask.session.get('posting'))
 

@app.route('/posting')
def posting():
    return flask.render_template('posting.html')

@app.route('/postNewContent', methods=['GET','POST'])
def postNewContent():
    client = MongoClient('mongo',27017)
    db = client.chatDatabase
    collection = db.postingCollection
    title = flask.request.form['title']
    content = flask.request.form['content']
    if title != "" and content != "":
        uploader = flask.session['user']
        collection.insert_one({"Uploder" : uploader ,"title" : title, "content" : content})
        tmp = {
            "uploader" : uploader, 
            "title" : title,
            "content" : content}
        postingArr.append(tmp)
    client.close()
    return flask.redirect(flask.url_for('home'))

@app.route('/login')
def login():
    return flask.render_template('login.html')


@app.route('/logout')
def logout():
    global online_users
    name = flask.request.cookies.get('username')
    online_users.remove(name)
    flask.session['logged_in'] = False
    flask.session['user'] = ''
    resp = flask.redirect(flask.url_for('home'))
    resp.set_cookie('username', value='')
    flask.session.clear()
    return resp


@app.route('/checkCredentials', methods=['GET', 'POST'])
def checkCredentials():
    client = MongoClient('mongo',27017)
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
            resp = flask.redirect(flask.url_for('home'))
            resp.set_cookie('username', value=username)
            return resp 
        

@app.route('/register', methods=['GET', 'POST'])
def register():
    return flask.render_template('register.html')


@app.route('/checkAvailability', methods=['GET', 'POST'])
def checkAvailability():
    client = MongoClient('mongo',27017)
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
