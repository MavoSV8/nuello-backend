import json

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request
from flask_cors import CORS
from flask_api import status
from bcrypt import hashpw, checkpw, gensalt

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


class TableParentModel(db.Model):
    __abstract__ = True
    __table_args__ = {'extend_existing': True}  # may be worth to replace it with different solution
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)

    def __init__(self, id, name, desc):
        self.id = id
        self.name = name
        self.desc = desc

    def __repr__(self):
        return '<Table %r, %r, %r>' % (self.id, self.name, self.desc)


def get_table_model(table_name):
    class GenericTable(TableParentModel):
        __tablename__ = table_name

    return GenericTable


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


@app.route('/tables/<table_name>', methods=['GET'])
def get_table(table_name):
    if request.method == "GET":
        model = get_table_model(table_name)
        tables = model.query.all()
        results = [
            {
                "id": table.id,
                "name": table.name,
                "desc": table.desc
            } for table in tables]

        return json.dumps(results)


# @app.route('/tables/add/<id>/<table_name>/<desc>', methods=['POST'])
# def add_table(id, table_name, desc):
#     # def add_record(table_name):
#     if request.method == 'POST':
#         tables_model = TablesModel
#         new_row = tables_model(id=id, name=table_name, desc=desc)
#
#         db.session.add(new_row)
#         model = get_table_model(table_name)
#         table_name.model.create(db.session.bind)
#         db.session.commit()
#         return json.dumps({"operation": "singup", "result": "success"})

@app.route('/tables/<table_name>/add/<row_id>/<name>/<desc>', methods=['POST'])
def add_record(table_name, row_id, name, desc):
    if request.method == 'POST':
        model = get_table_model(table_name)

        new_row = model(id=row_id, name=name, desc=desc)
        db.session.add(new_row)
        db.session.commit()
        return json.dumps({"operation": "singup", "result": "success"})

@app.route('/tables/<table_name>/delete/<row_id>', methods=['POST'])
def delete_record(table_name, row_id):
    if request.method == 'POST':
        model = get_table_model(table_name)

        row = model.query.filter_by(id=row_id).delete()
        # db.session.delete(row)
        # db.execute('delete from ' + table_name + ' where id = ' + row_id)

        # new_row = model(id=row_id, name=name, desc=desc)
        # db.session.add(new_row)
        db.session.commit()
        return json.dumps({"operation": "singup", "result": "success"})

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
