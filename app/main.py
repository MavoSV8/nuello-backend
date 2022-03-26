import json

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
#                                                        change below if address differs
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ovizxqphegguzs:c55b21b95c83814fb811e6f58e1eb8c876b11bce22ec5f53f640b201a75a6849@ec2-99-80-170-190.eu-west-1.compute.amazonaws.com:5432/d4poogetisskjb"
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class TablesModel(db.Model):
    __tablename__ = 'tables'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return '<Table %r, %r>' % (self.id, self.name)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/tables', methods=['GET'])
# def something():
#     return 'IT WORKS!'
def get_tables():
    if request.method == "GET":
        tables = TablesModel.query.all()
        results = []
        #     {
        #         "id": table.id,
        #         "name": table.name,
        #     } for table in tables]

        return json.dumps(results)
