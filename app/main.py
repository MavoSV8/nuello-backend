import json
import string

import sqlalchemy
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request
from flask_cors import CORS
from flask_api import status
from bcrypt import hashpw, checkpw, gensalt
from sqlalchemy import null

app = Flask(__name__)
#                                                        change below if address differs
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "postgresql://ovizxqphegguzs:c55b21b95c83814fb811e6f58e1eb8c876b11bce22ec5f53f640b201a75a6849@ec2-99-80-170-190.eu-west-1.compute.amazonaws.com:5432/d4poogetisskjb"
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class TablesModel(db.Model):
    __tablename__ = 'tables'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)

    def __init__(self, id, name, desc):
        self.id = id
        self.name = name
        self.desc = desc

    def __repr__(self):
        return '<Table %r, %r, %r>' % (self.id, self.name, self.desc)


class ListsModel(db.Model):
    __tablename__ = 'lists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey('tables.id'), nullable=False)

    def __init__(self, id, name, table_id):
        self.id = id
        self.name = name
        self.table_id = table_id

    def __repr__(self):
        return '<List %r, %r, %r>' % (self.id, self.name, self.table_id)


class CardsModel(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)
    assigne = db.Column(db.Text, nullable=True)

    def __init__(self, id, name, list_id, description, assigne):
        self.id = id
        self.name = name
        self.list_id = list_id
        self.description = description
        self.assigne = assigne

    def __repr__(self):
        return '<List %r, %r, %r, %r, %r>' % (self.id, self.name, self.list_id, self.description, self.assigne)

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)

    def __init__(self, name, password):
        self.name = name
        self.password = password

    def __repr__(self):
        return '<User %r, %r, %r, %r>' % (self.id, self.name, self.password, self.salt)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/tables', methods=['GET'])
def get_tables():
    if request.method == "GET":
        tables = TablesModel.query.all()
        results = [
            {
                "id": table.id,
                "name": table.name,
                "desc": table.desc
            } for table in tables]

        return json.dumps(results)


@app.route('/lists', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def get_lists():  # table_id
    if request.method == "GET":

        data = {}
        try:
            data = json.loads(request.data)
        except Exception:
            return 'Invalid request - missing parameters', status.HTTP_400_BAD_REQUEST
        if "table_id" not in data: #maybe just return all
            return 'Invalid request - missing parameters', status.HTTP_400_BAD_REQUEST
        if "id" in data:
            lists = ListsModel.query.filter_by(table_id=data["table_id"],id=data["id"])
        else:
            lists = ListsModel.query.filter_by(table_id=data["table_id"])
        # lists = ListsModel.query.all()
        results = [
            {
                "id": list.id,
                "name": list.name,
                "table_id": list.table_id
            } for list in lists]

        return json.dumps(results)
    if request.method == "POST":
        lists = ListsModel
        data = {}
        try:
            data = json.loads(request.data)
        except Exception:
            return 'Invalid request - missing parameters', status.HTTP_400_BAD_REQUEST

        # workaround, no idea how to not pass id without altering model
        id = ListsModel.query.order_by(ListsModel.id.desc()).first().id
        id += 1

        # new_row = card(id, data["name"],data["list_id"],data["description"],data["assigne"])
        new_row = lists(id, data["name"], data["table_id"])
        db.session.add(new_row)
        db.session.commit()

        print("List {} added".format(lists.name))

        return json.dumps({"operation": "post", "result": "success"})
    if request.method == "DELETE":
        lists = ListsModel
        data = {}
        try:
            data = json.loads(request.data)
        except Exception:
            return 'Invalid request', status.HTTP_400_BAD_REQUEST

        if "table_id" not in data or "id" not in data:
            return 'Invalid request - missing parameters', status.HTTP_400_BAD_REQUEST

        # //
        cards = CardsModel.query.filter_by(list_id=data["id"])
        for card in cards:
            card.query.filter_by(id=card.id).delete()
        # //
        lists.query.filter_by(id=data["id"], table_id=data["table_id"]).delete()
        db.session.commit()

        print("List {} deleted".format(lists.name))

        return json.dumps({"operation": "delete", "result": "success"})
    if request.method == "PATCH":
        lists = ListsModel
        data = {}
        try:
            data = json.loads(request.data)
        except Exception:
            return 'Invalid request', status.HTTP_400_BAD_REQUEST
        if "table_id" not in data or "id" not in data:
            return 'Invalid request - missing parameters', status.HTTP_400_BAD_REQUEST

        new_values = data.copy()
        new_values.pop("id", None)
        new_values.pop("table_id", None)
        print(new_values)

        # CardsModel.query.filter_by(id=data["id"],list_id=data["list_id"]).update(new_values)
        lists.query.filter_by(id=data["id"]).update(new_values)
        db.session.commit()

        print("List {} altered".format(lists.name))

        return json.dumps({"operation": "patch", "result": "success"})


@app.route('/cards', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def get_cards():
    if request.method == "GET":
        data = {}
        try:
            data = json.loads(request.data)
        except Exception:
            return 'Invalid request - missing parameters', status.HTTP_400_BAD_REQUEST
        if "list_id" not in data:
            return 'Invalid request - missing parameters', status.HTTP_400_BAD_REQUEST
        if "id" in data:
            cards = CardsModel.query.filter_by(list_id=data["list_id"],id=data["id"])
        else:
            cards = CardsModel.query.filter_by(list_id=data["list_id"])
        results = [
            {
                "id": card.id,
                "name": card.name,
                "list_id": card.list_id,
                "description": card.description,
                "assigne": card.assigne
            } for card in cards]

        return json.dumps(results)
    if request.method == "POST":
        card = CardsModel
        data = {}
        try:
            data = json.loads(request.data)
        except Exception:
            return 'Invalid request - missing parameters', status.HTTP_400_BAD_REQUEST

        # workaround, no idea how to not pass id without altering model
        id = CardsModel.query.order_by(CardsModel.id.desc()).first().id
        id += 1

        # new_row = card(id, data["name"],data["list_id"],data["description"],data["assigne"])
        new_row = card(id, data["name"], data["list_id"],
                       data["description"] if "description" in data else sqlalchemy.sql.null(),
                       data["assigne"] if "assigne" in data else sqlalchemy.sql.null())
        db.session.add(new_row)
        db.session.commit()

        print("Card {} added".format(card.name))

        return json.dumps({"operation": "post", "result": "success"})
    if request.method == "DELETE":
        card = CardsModel
        data = {}
        try:
            data = json.loads(request.data)
        except Exception:
            return 'Invalid request', status.HTTP_400_BAD_REQUEST

        if "list_id" not in data or "id" not in data:
            return 'Invalid request - missing parameters', status.HTTP_400_BAD_REQUEST

        card.query.filter_by(id=data["id"], list_id=data["list_id"]).delete()
        db.session.commit()

        print("Card {} deleted".format(card.name))

        return json.dumps({"operation": "delete", "result": "success"})
    if request.method == "PATCH":
        card = CardsModel
        data = {}
        try:
            data = json.loads(request.data)
        except Exception:
            return 'Invalid request', status.HTTP_400_BAD_REQUEST
        if "list_id" not in data or "id" not in data:
            return 'Invalid request - missing parameters', status.HTTP_400_BAD_REQUEST

        new_values = data.copy()
        new_values.pop("id", None)
        new_values.pop("list_id", None)
        print(new_values)

        # CardsModel.query.filter_by(id=data["id"],list_id=data["list_id"]).update(new_values)
        card.query.filter_by(id=data["id"]).update(new_values)
        db.session.commit()

        print("Card {} altered".format(card.name))

        return json.dumps({"operation": "patch", "result": "success"})

@app.route('/signin', methods=['GET'])
def signin():
    if request.method == 'GET':
        print(request.args.to_dict())

        op = request.args.get("operation")
        name = request.args.get("name")
        pwd = request.args.get("pwd")

        # Validate request.
        if op != "singin" or name is None or pwd is None:
            return 'Invalid request', status.HTTP_400_BAD_REQUEST

        user = UserModel.query.filter_by(name=request.args.get("name")).first()

        # User does not exist.
        if user is None:
            return json.dumps({"operation": "singin", "result": "failure"})

        # Invalid password
        if not checkpw(pwd.encode('utf-8'), user.password.encode('utf-8')):
            return json.dumps({"operation": "singin", "result": "failure"})

        # All ok
        return json.dumps({"operation": "singin", "result": "success"})


@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        data = {}
        try:
            data = json.loads(request.data)
        except Exception:
            return 'Invalid request', status.HTTP_400_BAD_REQUEST

        if data["operation"] != "singup" or data["name"] is None or data["pwd"] is None:
            return 'Invalid request', status.HTTP_400_BAD_REQUEST

        user = UserModel(data["name"], hashpw(data["pwd"].encode('utf-8'), gensalt()).decode('utf-8'))

        db.session.add(user)
        db.session.commit()

        print("User {} added".format(user.name))

        return json.dumps({"operation": "singup", "result": "success"})


@app.route('/signout', methods=['POST'])
def signout():
    if request.method == 'POST':
        # db.session.pop('logged_in', None)
        return json.dumps({"operation": "signout", "result": "success"})
